from conans import ConanFile, tools
from conans.tools import SystemPackageTool
import glob, os

MXEGCCVERSION = "5.5.0"
MXEGITSHA="a063f9b35279d83f692df0345d84147c0f23c992"
STATUSTOOLCHAINVER="1"
VERSION="%s-%s" % (MXEGCCVERSION, STATUSTOOLCHAINVER)

class MXEToolchainx8664w64mingw32Conan(ConanFile):
  name = "mxetoolchain-x86_64-w64-mingw32"
  url = "https://github.com/mxe/mxe"
  license = "MIT"
  version = VERSION
  settings = {"os": ["Windows"], "arch": ["x86_64"]}
  options = {"mxe_git_sha":"ANY"}
  default_options = "mxe_git_sha={0}".format(MXEGITSHA)
  description = "MXE cross-compiling toolchain for Windows"

  def system_requirements(self):
    # https://mxe.cc/#requirements-debian
    pkgs = [
      "autoconf",
      "automake",
      "autopoint",
      "bash",
      "bison",
      "bzip2",
      "flex",
      "g++",
      "g++-multilib",
      "gettext",
      "git",
      "gperf",
      "intltool",
      "libc6-dev-i386",
      "libgdk-pixbuf2.0-dev",
      "libltdl-dev",
      "libssl-dev",
      "libtool-bin",
      "libxml-parser-perl",
      "make",
      "openssl",
      "p7zip-full",
      "patch",
      "perl",
      "pkg-config",
      "python",
      "ruby",
      "sed",
      "unzip",
      "wget",
      "xz-utils"
    ]
    installer = SystemPackageTool()
    for pkg in pkgs:
      installer.install(pkg)

  def target_tuple(self):
    return "{0}-w64-mingw32.shared".format(self.settings.arch)

  def source(self):
    git = tools.Git(folder="mxe")
    git.clone("https://github.com/mxe/mxe.git")
    git.checkout(self.options.mxe_git_sha)

  def build_id(self):
    self.info_build.options.mxe_git_sha = MXEGITSHA

  def build(self):
    with tools.chdir("./mxe"):
      pkgs = ["mingw-w64", "cc", "zlib", "libpng", "openssl", "icu4c", "harfbuzz", "freetype", "pcre2", "pthreads"]
      for pkg in pkgs:
        self.run("unset LD_LIBRARY_PATH CC CXX CFLAGS CXXFLAGS LDFLAGS && make --jobs={2} MXE_TARGETS={0} {1}".format(self.target_tuple(), pkg, os.environ.get("STATUS_JOBS", "6")))

  def package(self):
    toolchain = "mxe/usr"
    self.copy("%s-*" % self.target_tuple(), src=os.path.join(toolchain, "bin"), dst="bin", symlinks=False)
    self.copy("*.dll", src=os.path.join(toolchain, self.target_tuple(), "bin"), dst="bin", symlinks=False)
    self.copy("*", src=os.path.join(toolchain, "include"), dst="include", symlinks=False)
    self.copy("*", src=os.path.join(toolchain, self.target_tuple(), "include"), dst=os.path.join(self.target_tuple(), "include"), symlinks=False)
    self.copy("*", src=os.path.join(toolchain, self.target_tuple(), "lib"), dst=os.path.join(self.target_tuple(), "lib"), symlinks=False)
    self.copy("*", src=os.path.join(toolchain, "lib"), dst="lib", symlinks=False)
    self.copy("*", src=os.path.join(toolchain, "libexec"), dst="libexec", symlinks=False)
    self.copy("*", src=os.path.join(toolchain, self.target_tuple()), dst=self.target_tuple(), symlinks=False)

    # MXE is generally not relocatable (https://github.com/mxe/mxe/issues/1700, https://github.com/mxe/mxe/issues/1902),
    # but we can get around this for the toolchain by relying on the fact that e.g. `gcc` will look for `as`
    # so we'll just create symlinks to the right binaries on the same directory and add that directory to bindirs.
    # This symlinks folder will only be added to the PATH using a profile, so that other MXE-based package
    # can depend on this one without inadvertently using the mingw64 gcc and therefore build Windows binaries instead of Linux ones.
    with tools.chdir(os.path.join(self.package_folder, "bin")):
      symlink_path = "symlinks"
      tools.mkdir(symlink_path)
      for target in glob.iglob("%s-*" % self.target_tuple()):
        link_name = target.replace("%s-" % self.target_tuple(), "", 1)
        if link_name == "ld":
          target="{0}-{1}".format(self.target_tuple(), link_name)
          link_name = "real-ld"
        link_path = os.path.join(symlink_path, link_name)
        if not os.path.exists(link_path) and not link_name in ["cmake", "cpack"]:
          os.symlink(os.path.join("..", target), link_path)
        if link_name == "real-ld" and not os.path.exists(os.path.join(symlink_path, "collect2")):
          os.symlink(os.path.join("../../libexec/gcc", self.target_tuple(), MXEGCCVERSION, "collect2"), os.path.join(symlink_path, "collect2"))

  def package_info(self):
    self.cpp_info.includedirs = [
      os.path.join(self.package_folder, "include"),
      os.path.join(self.package_folder, self.target_tuple(), "include"),
      os.path.join(self.package_folder, "lib/gcc", self.target_tuple(), MXEGCCVERSION, "include")
    ] # Ordered list of include paths
    self.cpp_info.resdirs = []  # Directories where resources, data, etc can be found
    self.cpp_info.libdirs = [
      os.path.join(self.package_folder, "lib/gcc", self.target_tuple(), VERSION),
      os.path.join(self.package_folder, self.target_tuple(), "lib"),
      os.path.join(self.package_folder, self.target_tuple(), "lib", self.target_tuple(), VERSION),
      os.path.join(self.package_folder, self.target_tuple(), "lib")
    ]
    self.cpp_info.bindirs = [
      os.path.join(self.package_folder, "bin"),
      os.path.join(self.package_folder, "bin/symlinks")
    ]
    self.cpp_info.sysroot = self.package_folder

    # Add the compiler dir to the PATH
    self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
    self.env_info.CC = "%s-gcc" % self.target_tuple()
    self.env_info.CFLAGS = "-D_UNICODE -DUNICODE -Os"
    self.env_info.CXX = "%s-g++" % self.target_tuple()
    self.env_info.CXXFLAGS = "-D_UNICODE -DUNICODE -Os"
    self.env_info.WINDRES = "%s-windres" % self.target_tuple()
    self.env_info.STATUS_TRIPLE = self.target_tuple()

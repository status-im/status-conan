from conans import ConanFile, tools
from conans.tools import SystemPackageTool
from conans.errors import ConanInvalidConfiguration
import os, platform

VERSION="5.11.3"

class QtConan(ConanFile):
  name = "qt5-mxe"
  url = "https://github.com/mxe/mxe"
  license = "MIT"
  description = "MXE cross-compiled Qt5 for Windows"
  version = os.environ.get("CONAN_VERSION_OVERRIDE", VERSION)
  settings = "os", "arch", "build_type"
  options = { "webkit": [False, True] }
  default_options = "webkit=False"
  requires = "mxetoolchain-x86_64-w64-mingw32/5.5.0-1@status-im/stable"
  confFile = "qt.conf"

  def get_triple(self):
    return "%s-w64-mingw32.shared" % self.settings.arch

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

  def configure(self):
    if self.settings.os != "Windows" or platform.system() != "Linux":
      raise ConanInvalidConfiguration("This package is only meant to cross-compile for Windows. It cannot compile for %s" % self.settings.os)

  def source(self):
    git = tools.Git(folder="mxe")
    git.clone("https://github.com/mxe/mxe.git")
    git.checkout("a063f9b35279d83f692df0345d84147c0f23c992")

  def build(self):
    with tools.chdir("./mxe"):
      pkgs = ["qtbase", "qtdeclarative", "qtgraphicaleffects", "qtimageformats", "qtlocation", "qtquickcontrols", "qtquickcontrols2", "qtsensors", "qtserialport", "qtsvg", "qttools", "qtwebchannel", "qttranslations"]
      if self.options.webkit:
        pkgs += ["qtmultimedia", "qtwebkit"]
      for pkg in pkgs:
        self.run("unset LD_LIBRARY_PATH CC CXX CFLAGS CXXFLAGS LDFLAGS && make --jobs={2} MXE_TARGETS={0} {1}".format(self.get_triple(), pkg, os.environ.get("STATUS_JOBS", "6")))

  def package(self):
    toolchain = os.path.join("mxe/usr", self.get_triple())
    target_base = "gcc_64" if self.settings.arch == "x86_64" else "gcc_32"
    outputDir = ("bin", "include", "lib", "mkspecs", "Frameworks", "plugins", "qml", "translations")

    # TODO: Right now the package contains all the dependencies, for simplicity. In the future, we'll want to break this out into a toolchain package and maybe individual packages that get imported into this package
    for l in ("png16", "glib-2.0-0", "jpeg-9", "sqlite3-0", "webp-5"):
      self.copy("lib{0}.dll.a".format(l), src=os.path.join(toolchain, "lib"), dst=os.path.join(target_base, "lib"))
      self.copy("lib{0}*.dll".format(l), src=os.path.join(toolchain, "bin"), dst=os.path.join(target_base, "bin"))
      self.copy("{0}*.dll".format(l), src=os.path.join(toolchain, "bin"), dst=os.path.join(target_base, "bin"))

    source_base = os.path.join(toolchain, "qt5")
    tools.save(os.path.join(self.package_folder, target_base, "bin", self.confFile), 
"""
[Paths]
Prefix = ..
""")

    for d in outputDir:
      self.copy("*", src=os.path.join(source_base, d), dst=os.path.join(target_base, d))

    if self.options.webkit:
      self.copy("QtWebProcess.exe", src=os.path.join(source_base, "bin"), dst=os.path.join(target_base, "bin"))

  def package_info(self):
    base = "gcc_64" if self.settings.arch == "x86_64" else "gcc_32"
    baseFrameworks = ["Core", "Gui", "Qml", "Quick", "Network", "OpenGL", "Svg", "WebSockets", "Widgets"]
    frameworks = ["Positioning", "SerialPort", "WebChannel"]
    if self.options.webkit:
      baseFrameworks += ["WebKit", "WebKitWidgets"]
      frameworks += ["Sensors", "Sql"]
    frameworks += baseFrameworks
    includedirs = [os.path.join(base, "include")] + [os.path.join(base, "include/Qt%s" % a) for a in frameworks]

    self.cpp_info.bindirs = [os.path.join(base, "bin")]
    self.cpp_info.builddirs = [os.path.join(base, "lib/cmake", "Qt5%s" % a) for a in frameworks]
    self.cpp_info.libdirs = [os.path.join(base, "lib")]
    self.cpp_info.libs = ["Qt5%s" % a for a in baseFrameworks]
    self.cpp_info.includedirs = includedirs
 
    # Add the Qt5 binaries dir to the PATH
    self.env_info.PATH.append(os.path.join(base, "bin"))

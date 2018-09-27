from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment
import os

class CBuffer(object):
  def __init__(self):
    self.lines = []

  def write(self, buf):
    self.lines.append(buf.strip())

  def clear(self):
    self.lines = []

  def __str__(self):
    return "\n".join(self.lines)

class QtTest(ConanFile):
  settings = "os", "compiler", "build_type", "arch"
  requires = "qt5-mxe/5.11.2@status-im/stable"
  generators = "cmake"
  options = { "webkit": [False, True] }
  default_options = "webkit=False"

  def configure(self):
    self.options['qt5-mxe'].webkit = self.options.webkit

  def build(self):
    with tools.pythonpath(self):
      env_build = AutoToolsBuildEnvironment(self)
      with tools.environment_append(env_build.vars):
        vcvars = ""
        if self.settings.compiler == "Visual Studio":
          vcvars = tools.vcvars_command(self.settings) + "&&"
        cmake = CMake(self, cmake_system_name=(str(self.settings.os) == "Windows"))
        self.run('{0}cmake "{1}" {2}'.format(vcvars, self.source_folder, cmake.command_line))
        self.run("{0}cmake --build . {1}".format(vcvars, cmake.build_config))       

  def test(self):
    # Verify that we have a build that is usable on other machines (no hardcoded paths on binaries, etc)
    lddbuf = CBuffer()
    self.run("ldd `which rcc`", run_environment=True, output=lddbuf)
    for line in lddbuf.lines:
      if "lib/ld.so" in line or ".linuxbrew" in line:
        print("An unexpected dynamic module is linked in rcc: {line}".format(line=line))
        exit(1)

    # ldd rcc should return something like:
    #    linux-vdso.so.1 =>  (0x00007ffee3736000)
    #    libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fa171b42000)
    #    libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007fa1717c0000)
    #    libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007fa1714b7000)
    #    libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007fa1712a1000)
    #    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fa170ed7000)
    #    /lib64/ld-linux-x86-64.so.2 (0x00007fa171d5f000)
    #
    # Example wrong output
    #
    #    linux-vdso.so.1 (0x00007ffde25c9000)
    #    libgtk3-nocsd.so.0 => /usr/lib/x86_64-linux-gnu/libgtk3-nocsd.so.0 (0x00007f64933ae000)
    #    libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f649318f000)
    #    libstdc++.so.6 => /home/linuxbrew/.linuxbrew/lib/libstdc++.so.6 (0x00007f6492dd2000)
    #    libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f6492a34000)
    #    libgcc_s.so.1 => /home/linuxbrew/.linuxbrew/lib/libgcc_s.so.1 (0x00007f649281d000)
    #    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f649242c000)
    #    /home/linuxbrew/.linuxbrew/lib/ld.so => /lib64/ld-linux-x86-64.so.2 (0x00007f64935b5000)
    #    libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f6492228000)

    filebuf = CBuffer()
    self.run("file test_qt.exe", output=filebuf, cwd=os.path.join(self.build_folder, "bin"))
    if not (filebuf.lines[i] is "PE32+ executable(console) x86-64 (stripped to external PDB), for MS Windows" for i in filebuf.lines):
      print("Unexpected output file type: {0}".format(filebuf.lines))
      exit(1)

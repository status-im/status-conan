from conans import ConanFile, tools
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

class TestToolchain(ConanFile):
  settings = "os", "arch"
  requires = "mxetoolchain-x86_64-w64-mingw32/5.5.0-1@status-im/stable"
  buf = CBuffer()

  def build(self):
    self.run("mkdir bin")
    self.run("{compiler} -v -o bin/hello.exe {cxxflags} -static-libgcc -static-libstdc++ {src}/hello.cpp".format(
        compiler=os.getenv("CXX"),
        cxxflags=os.getenv("CXXFLAGS"),
        src=self.source_folder),
      run_environment=True,
      output=self.buf)

  def test(self):
    # Verify that we have a build that is usable on other machines (no hardcoded paths on binaries, etc)
    bindir=self.deps_cpp_info["mxetoolchain-x86_64-w64-mingw32"].bindirs[0]

    for filename in os.listdir(bindir):
      path=os.path.join(bindir, filename)
      if os.path.islink(path):
        symlink_target=os.readlink(path)
        if os.path.isabs(symlink_target):
          print("A symlink linking to an absolute path is present in the binaries directory. This might cause issues when the package is installed on another machine. File: {0}".format(filename))
          exit(1)

    lddbuf = CBuffer()
    self.run("ldd {bindir}/{windres}".format(bindir=bindir, windres=os.getenv("WINDRES")),
      run_environment=True,
      output=lddbuf)
    for line in lddbuf.lines:
      if "lib/ld.so" in line or "libfl.so.2" in line:
        print("An unexpected dynamic module is linked in {windres}: {line}".format(windres=os.getenv("WINDRES"), line=line))
        exit(1)

    # ldd os.getenv("WINDRES") should return something like:
    #     linux-vdso.so.1 =>  (0x00007ffeb5bca000)
    #     libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f6afcfa9000)
    #     libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f6afcbdf000)
    #     /lib64/ld-linux-x86-64.so.2 (0x00007f6afd1ad000)
    #
    # Example wrong output
    #
    #     linux-vdso.so.1 (0x00007ffc2adc7000)
    #     libgtk3-nocsd.so.0 => /usr/lib/x86_64-linux-gnu/libgtk3-nocsd.so.0 (0x00007fefae8dc000)
    #     libfl.so.2 => /usr/lib/x86_64-linux-gnu/libfl.so.2 (0x00007fefae6da000)
    #     libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007fefae4d6000)
    #     libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fefae0e5000)
    #     libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fefadec6000)
    #     /home/linuxbrew/.linuxbrew/lib/ld.so => /lib64/ld-linux-x86-64.so.2 (0x00007fefaeae3000)

    triple=os.getenv("STATUS_TRIPLE")
    self.output.info(triple)
    if not [line for line in self.buf.lines if line.startswith("Target: %s" % triple)]:
      print("Target mismatch/not found (expected {0})".format(triple))
      exit(1)
    if not [line for line in self.buf.lines if line.startswith("COLLECT_GCC=%s-g++" % triple)]:
      print("%s-g++ not set in COLLECT_GCC" % triple)
      exit(1)
    if not [line for line in self.buf.lines if line.startswith("Thread model: win32")]:
      print("Thread model mismatch/not found (expected win32)")
      exit(1)
    if not [line for line in self.buf.lines if line.startswith("gcc version 5.5.0")]:
      print("Thread model mismatch")
      exit(1)
    self.buf.clear()

import glob, io, json, os, sys
from conans.client.runner import ConanRunner

class CBuffer(object):
  def __init__(self):
    self.lines = []

  def write(self, buf):
    self.lines.append(buf.strip())

  def clear(self):
    self.lines = []

  def __str__(self):
    return "\n".join(self.lines)

def generate_profile(profiles_path, template_fname, buidinfo_json_path):
  with open(buidinfo_json_path, 'r') as f:
    template_dict = json.load(f)
    old_environ = os.environ.copy()
    new_environ = os.environ.copy()
    try:
      dep_paths = template_dict['deps_env_info']['PATH']
      if dep_paths:
        new_environ["PATH"] = "{0}:{1}".format(':'.join(dep_paths), new_environ["PATH"])
        os.environ.update(new_environ)

      generate_expanded_profile_from_in_file(profiles_path, template_fname)
    finally:
      os.environ.clear()
      os.environ.update(old_environ)
 
def generate_expanded_profile_from_in_file(profiles_path, f):
  nf = f.replace(".in", "")

  profile_path = os.path.join(profiles_path, f)
  print("Processing {0}...".format(profile_path))
  with open(profile_path, "r") as pf:
    data = pf.readlines()
    newlines = []

    # get CC binary
    cc = [i.split("CC=")[1] for i in data if i.startswith("CC=")][0].replace("ccache ", "").strip()
    cc_output = CBuffer()
    cc_cmd = "{0} -print-sysroot".format(cc)
    runner = ConanRunner()
    if not runner(cc_cmd, output=cc_output) is 0:
      print("Failed to run {0} for {1}!\n{2}".format(cc_cmd, f, cc_output.lines))
      return False

    sysroot = os.path.abspath(cc_output.lines[0].strip()) if cc_output.lines else None
    cc_output.clear()

    triple = [i.split("_STATUS_GCC_TRIPLE_NAME=")[1] for i in data if i.startswith("_STATUS_GCC_TRIPLE_NAME=")]
    if triple:
      triple = triple[0].strip()

    ccpath = os.path.abspath(os.path.join(sysroot, os.pardir))
    if not os.path.isdir(os.path.join(ccpath, triple)):
      ccpath = os.path.abspath(os.path.join(sysroot, os.pardir, os.pardir))
    triple_sysrootpath = os.path.normpath(os.path.abspath(os.path.join(sysroot, "usr", triple)))

    flags = " --sysroot=" + sysroot if sysroot else ""

    for line in data:
      line = line.rstrip()
      if line.startswith("LDFLAGS="):
        newlines.append("LDFLAGS={0}{1}".format(line.strip().split("LDFLAGS=")[1], flags))
      elif line.startswith("_STATUS_TRIPLE_PATH="):
        path=os.path.normpath(os.path.join(triple_sysrootpath, "../../..", line.strip().split("_STATUS_TRIPLE_PATH=")[1]))
        newlines.append("_STATUS_TRIPLE_PATH={0}".format(path))
      elif line.startswith("_STATUS_TRIPLE_SYSROOTPATH="):
        newlines.append("_STATUS_TRIPLE_SYSROOTPATH={0}".format(triple_sysrootpath))
      else:
        newlines.append(line)

    with open(os.path.join(profiles_path, nf), "w") as nfp:
      nfp.write("\n".join(newlines) + "\n")

  return True

if __name__ == '__main__':
  profiles_path = os.path.abspath(sys.argv[1])
  buidinfo_json_path = os.path.abspath(sys.argv[2])
  for template_fname in glob.glob("{0}/status-*.in".format(profiles_path)):
    generate_profile(profiles_path, template_fname, buidinfo_json_path)

import sys
import os
import traceback

# inputdir = sys.argv[1]

inputdir = sys.argv[1]
dry_run = False

os.chdir(inputdir)
print("getcwd:", os.getcwd())

files = [f for f in os.listdir() if os.path.isfile(f)]

def get_extension_dir(f):
    extdir = os.path.splitext(f)[1].strip('.')
    if not extdir:
        extdir = "unknown_ext"
    if not os.path.exists(extdir):
        os.mkdir(extdir)
    return extdir

for f in files:
    extdir = get_extension_dir(f)
    dest = os.path.join(extdir, f)
    print("Moving", f, " -> ", dest)
    try:
        if not dry_run:
            os.rename(f, dest)
    except FileExistsError:
        traceback.print_exc()
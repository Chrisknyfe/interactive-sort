import sys
import os
import random
import zipfile

""" Unzip all files in the selected folder """

SUPPORTED_FILENAMES = (".zip")

def unzip_to_folder(f):
    name, ext = os.path.splitext(f)
    dirname = os.path.dirname(f)
    outdir = os.path.join(dirname, name)
    print(f, "->", outdir)
    if not os.path.exists(outdir):
        with zipfile.ZipFile(f, 'r') as z:
            z.extractall(outdir)
    else:
        print(outdir, "already exists!")

directory = sys.argv[1]

files = []
for f in os.listdir(directory):
    fullfile = os.path.join(directory,f)
    name, ext = os.path.splitext(f)
    print(ext, fullfile)
    if os.path.isfile(fullfile) and ext in SUPPORTED_FILENAMES:
        files.append(fullfile)
    
print("directory:", directory)

print("len(os.listdir(directory)):", len(os.listdir(directory)))
print("len(files):", len(files))

for f in files:
    unzip_to_folder(f)


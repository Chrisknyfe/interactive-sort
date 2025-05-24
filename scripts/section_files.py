import sys
import os

# inputdir = sys.argv[1]

files_per_dir = 100
inputdir = sys.argv[1]
dry_run = False

os.chdir(inputdir)
print("getcwd:", os.getcwd())

files = [f for f in os.listdir() if os.path.isfile(f)]

print("sorting files...")
files.sort(key=lambda f: os.stat(f).st_mtime)

#print(files)

dir_counter = 0
def get_section_dir():
    global dir_counter
    dir_counter += 1
    seldir = "section_" + str(dir_counter)
    while os.path.exists(seldir):
        dir_counter += 1
        seldir = "section_" + str(dir_counter)
    return seldir

while files:
    selected = files[:files_per_dir]
    files = files[files_per_dir:]
    seldir = get_section_dir()
    print("seldir:", seldir)
    print("len(selected):", len(selected))
    if not dry_run:
        os.mkdir(seldir)
        for f in selected:
            os.rename(f, os.path.join(seldir, f))

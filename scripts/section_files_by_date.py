import sys
import os
from datetime import datetime


inputdir = sys.argv[1]
dry_run = False

def get_section_dir(fullpath):
    dt = datetime.fromtimestamp(os.stat(fullpath).st_birthtime)
    return os.path.join(os.path.dirname(fullpath), dt.strftime("section_%Y_%m"))

files_by_date = {}

print("inputdir is", inputdir)

for f in os.listdir(inputdir):
    fullpath = os.path.join(inputdir, f)
    if not os.path.isfile(fullpath):
        continue
    section_dir = get_section_dir(fullpath)
    if not section_dir in files_by_date:
        files_by_date[section_dir] = []
    files_by_date[section_dir].append(fullpath)

for section_dir, files in files_by_date.items():
    if not dry_run:
        os.makedirs(section_dir, exist_ok=True)
    for src in files:
        dst = os.path.join(section_dir, os.path.basename(src))
        print(f"{src} -> {dst}")
        if not dry_run:
            try:
                os.rename(src, dst)
            except FileExistsError as e:
                print(e)


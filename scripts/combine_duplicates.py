import sys
import os
import hashlib


class FileStat:
    def __init__(self, fullpath: str):
        self.fullpath = fullpath
        self.size = os.path.getsize(fullpath)
        self.birthtime = os.stat(fullpath).st_birthtime
        self._md5sum_cached = None
    def md5(self):
        if not self._md5sum_cached:
            self._md5sum_cached = hashlib.md5(open(self.fullpath,'rb').read()).hexdigest()
        return self._md5sum_cached
    def __repr__(self):
        return f"FileStats('{self.fullpath}', size: {self.size}, md5: {self._md5sum_cached})"
    
def list_filestats(inputdir: str):
    filestats = []
    for dirpath, dirnames, filenames in os.walk(inputdir):
        if dirpath.find("#recycle") != -1:
            print("skipping recycle bin: ", dirpath)
        else:
            print("scanning", dirpath)
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                filestats.append(FileStat(filepath))
    return filestats


def collect_files_by_size(filestats: list):
    files_by_size = {}
    for fs in filestats:
        if not fs.size in files_by_size:
            files_by_size[fs.size] = []
        files_by_size[fs.size].append(fs)
    return files_by_size


def collect_files_by_md5(filestats: list):
    files_by_md5 = {}
    for fs in filestats:
        if not fs.md5() in files_by_md5:
            files_by_md5[fs.md5()] = []
        files_by_md5[fs.md5()].append(fs)
    return files_by_md5


def combine_duplicates(filestats: list, inputdir: str):
    dry_run = False
    if len(filestats) < 2:
        return
    
    print("\nduplicates:")

    new_basename = os.path.basename(filestats[0].fullpath)
    newest_filestat = filestats[0]
    for fs in filestats:
        b = os.path.basename(fs.fullpath)
        if len(b) < len(new_basename):
            new_basename = b
        print(f"\t{fs}")
        if fs.birthtime > newest_filestat.birthtime:
            newest_filestat = fs

    src = newest_filestat.fullpath
    dst = os.path.join(inputdir, f"found_duplicates", new_basename)
    print(f"move {src} -> {dst}")
    if not dry_run:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(src, dst)
    for fs in filestats:
        target = fs.fullpath
        if os.path.exists(target):
            print(f"delete {target}")
            if not dry_run:
                os.remove(target)



inputdir = sys.argv[1]


filestats = list_filestats(inputdir)
files_by_size = collect_files_by_size(filestats)
for size, files in files_by_size.items():
    # print(f"{size}: {files}")
    if len(files) > 1:
        files_by_md5 = collect_files_by_md5(files)
        for md5, files2 in files_by_md5.items():
            # print(f"\t{md5}: {files2}")
            combine_duplicates(files2, inputdir)


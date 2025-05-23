import sys
import os
import hashlib


class FileStat:
    def __init__(self, fullpath: str, rating: int):
        self.fullpath = fullpath
        self.rating = rating
        self.size = os.path.getsize(fullpath)
        self._md5sum_cached = None
    def md5(self):
        if not self._md5sum_cached:
            self._md5sum_cached = hashlib.md5(open(self.fullpath,'rb').read()).hexdigest()
        return self._md5sum_cached
    def __repr__(self):
        return f"FileStats('{self.fullpath}', {self.rating}, size: {self.size}, md5: {self._md5sum_cached})"
    
def list_filestats(inputdir: str):
    filestats = []
    for f in os.listdir(inputdir):
        fullpath = os.path.join(inputdir, f)
        if os.path.isdir(fullpath):
            if not f.startswith("is_rated"):
                continue
            rating = int(f.split("_")[2])
            print(f"rating is {rating} for dir {f}")
            for f2 in os.listdir(fullpath):
                fullpath2 = os.path.join(fullpath, f2)
                if os.path.isfile(fullpath2):
                    filestats.append(FileStat(fullpath2, rating))
        elif os.path.isfile(fullpath):
            rating = 1
            filestats.append(FileStat(fullpath, rating))
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
    if len(filestats) < 2:
        return
    print("has dupllicates:")
    new_basename = os.path.basename(filestats[0].fullpath)
    new_rating = 0
    for fs in filestats:
        b = os.path.basename(fs.fullpath)
        if len(b) < len(new_basename):
            new_basename = b
        new_rating += fs.rating
        print(f"\t{fs}")
    new_fullpath = os.path.join(inputdir, f"is_rated_{new_rating}", new_basename)
    print("new rating will be:")
    print(f"\t{new_fullpath} rating: {new_rating}")

    src = filestats[0].fullpath
    dst = new_fullpath
    if dry_run:
        print(f"move {src} -> {dst}")
    for fs in filestats[1:]:
        if dry_run:
            target = fs.fullpath
            print(f"delete {target}")



inputdir = sys.argv[1]

dry_run = True

filestats = list_filestats(inputdir)
files_by_size = collect_files_by_size(filestats)
for size, files in files_by_size.items():
    print(f"{size}: {files}")
    if len(files) > 1:
        files_by_md5 = collect_files_by_md5(files)
        for md5, files2 in files_by_md5.items():
            print(f"\t{md5}: {files2}")
            combine_duplicates(files2, inputdir)


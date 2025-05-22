import sys
import os

inputdir = sys.argv[1]

dry_run = False



for f in os.listdir(inputdir):
    fullpath = os.path.join(inputdir, f)
    if not os.path.isfile(fullpath):
        continue
    filename, extension = os.path.splitext(fullpath)
    new_ext = ""
    if not extension:
        with open(fullpath, 'rb') as f:
            head = f.read(16)
            if head.find(b'JFIF') != -1:
                new_ext = ".jpg"
            elif head.find(b'PNG') != -1:
                new_ext = ".png"
            else:
                print("head:", head, "fullpath:", fullpath)
        if new_ext:
            print(fullpath, "->", fullpath + new_ext)
            os.rename(fullpath, fullpath + new_ext)
    else:
        print("ext:", extension, "fullpath:", fullpath)
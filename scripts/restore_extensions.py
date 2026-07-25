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
            if head.find(b'Exif') != -1:
                new_ext = ".jpg"
            elif head.find(b'PNG') != -1:
                new_ext = ".png"
            elif head.find(b'GIF') != -1:
                new_ext = ".gif"
            elif head.find(b'WEBP') != -1:
                new_ext = ".webp"
            else:
                print("head:", head, "fullpath:", fullpath)
        if new_ext:
            print(fullpath, "->", fullpath + new_ext)
            try:
                os.rename(fullpath, fullpath + new_ext)
            except FileExistsError as e:
                print(e)
    # else:
    #     print("ext:", extension, "fullpath:", fullpath)
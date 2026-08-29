import sys
import os
import pprint

pp = pprint.PrettyPrinter(indent=4)

inputdir = sys.argv[1]

# respect special directories from interactive_choose.py
SPECIAL_DIRNAMES = [
    "ic_no",
    "ic_yes",
    "ic_best",
]

SPECIAL_DIRS = {}
for name in SPECIAL_DIRNAMES:
    SPECIAL_DIRS[name] = os.path.join(inputdir, name)
    if not os.path.exists(SPECIAL_DIRS[name]):
        os.mkdir(SPECIAL_DIRS[name])

pp.pprint(SPECIAL_DIRS)

dry_run = False

def unique_dest(dest):
    counter = 0
    dirname = os.path.dirname(dest)
    basename = os.path.basename(dest)
    rawname, extension = os.path.splitext(basename)
    while os.path.exists(dest):
        counter += 1
        dest = os.path.join(dirname, rawname + "_" + str(counter) + extension)
    return dest
        

for root, dirs, files in os.walk(inputdir):
    #print("examining", root)
    #print("dirs:", dirs)
    #print("files:", files)

    for f in files:
        src = os.path.join(root, f)
        
        destdir = inputdir
        rootbase = os.path.basename(root)
        if rootbase in SPECIAL_DIRS.keys():
            destdir = SPECIAL_DIRS[rootbase]
            #print("rootbase:", rootbase, "special dir:", destdir)
        
        dest = unique_dest(os.path.join(destdir, f))
        print("moving", src, "to", dest)
        if not dry_run:
            os.rename(src, dest)
    

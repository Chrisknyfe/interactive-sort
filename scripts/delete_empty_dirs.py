import sys
import os

inputdir = sys.argv[1]

dry_run = False



allclear = False

# After deleting some emtpy dirs, loop again to check if higher-level dirs were emptied 
# in the process of deleting directories.
while(not allclear):
    delete_queue = []
    for root, dirs, files in os.walk(inputdir):
        #print("examining", root)
        #print("len(dirs):", len(dirs), "len(files):", len(files))
        if len(dirs) == 0 and len(files) == 0:
            delete_queue.append(root)

    delete_queue.sort(key=len, reverse=True)
    if len(delete_queue):
        for d in delete_queue:
            print("Deleting", d)
            if not dry_run:
                os.rmdir(d)
            else:
                allclear = True
    else:
        allclear = True
    

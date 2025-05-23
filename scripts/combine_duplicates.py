import sys
import os
import hashlib

inputdir = sys.argv[1]

dry_run = True

# [{ fullpath, md5sum, rating }]
file_ratings = []

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
                md5sum = hashlib.md5(open(fullpath2,'rb').read()).hexdigest()
                size = os.path.getsize(fullpath2)
                file_ratings.append({'fullpath': fullpath2, 'md5sum': md5sum, 'size': size, 'rating': rating})
    elif os.path.isfile(fullpath):
        rating = 1
        md5sum = hashlib.md5(open(fullpath,'rb').read()).hexdigest()
        size = os.path.getsize(fullpath)
        file_ratings.append({'fullpath': fullpath, 'md5sum': md5sum, 'size': size, 'rating': rating})

frcopy = file_ratings.copy()
for rating in file_ratings:
    print(rating)

    duplicates = []
    for i, r in reversed(list(enumerate(frcopy))):
        if r['md5sum'] == rating['md5sum'] and r['size'] == rating['size']:
            duplicates.append(r)
            del frcopy[i]

    # duplicates = [r for r in frcopy if r['md5sum'] == rating['md5sum'] and r['size'] == rating['size']]
    if len(duplicates) > 1:
        print("has dupllicates:")
        new_basename = os.path.basename(duplicates[0]['fullpath'])
        new_rating = 0
        for d in duplicates:
            b = os.path.basename(d['fullpath'])
            if len(b) < len(new_basename):
                new_basename = b
            new_rating += d['rating']
            print(f"\t{d}")
        new_fullpath = os.path.join(inputdir, f"is_rated_{new_rating}", new_basename)
        print("new rating will be:")
        print(f"\t{new_fullpath} rating: {new_rating}")

        src = duplicates[0]['fullpath']
        dst = new_fullpath
        if dry_run:
            print(f"move {src} -> {dst}")
        for d in duplicates[1:]:
            if dry_run:
                target = d['fullpath']
                print(f"delete {target}")
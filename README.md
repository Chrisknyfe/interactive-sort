![python_OT9DlPUk07_downscale](https://github.com/Chrisknyfe/interactive-sort/assets/652027/9891c1da-088a-4021-96ff-cee6f95a22de)

# interactive-sort
An interactive media sorting tool for images and videos, written with PyQt5. I use it to sort my memes. Yeah... memes.

Supports Windows 10. I haven't tested on other platforms.

# installation
- Install the latest version of python 3 for windows and add it to your PATH.
- From the command line run `pip install -r requirements.txt` . 

# usage
Drag a folder to `interactive_sort.bat`. Each image is scored based on how much you like it, starting at 0. Clicking `Yes+` increments the score by 1 and sorts the file into a subdirectory. Clicking `Best++` increments score by 2. Clicking `No-` will decrement the score, and if the score is 0 or below the media will be put into a trash folder. Press `Skip` to move on to the next image without scoring the current one.

Alternatively you can create your own category folders outside the scoring system. Add categories at the bottom of the sidebar on the left.

![explorer_ZSEwRxEMgr](https://github.com/Chrisknyfe/interactive-sort/assets/652027/d9bd1d25-e38f-4938-aa71-63844a2db776)

Scored and categorized images will show up in folders named `is_rated_N` or `is_categorized_X`. Discarded images (scored 0 or lower) will show up in `is_trash`.

# other useful scripts

## delete_empty_dirs

Deletes empty subdirectories within the chosen root directory. If the root directory also ends up being an emtpy directory, delete it as well.
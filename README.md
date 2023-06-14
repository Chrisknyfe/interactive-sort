
![python_OT9DlPUk07](https://github.com/Chrisknyfe/interactive-sort/assets/652027/eb51653c-d35a-49cf-bf35-c9ffb26b8165)

# interactive-sort
An interactive media sorting tool for images and videos, written with PyQt5. I use it to sort my memes. Yeah... memes.

Supports Windows 10. I haven't tested on other platforms.

# installation
- Install the latest version of python 3 for windows and add it to your PATH.
- From the command line run `pip install -r requirements.txt` . 

# usage
Drag a folder to `interactive_sort.bat`. Each image is scored based on how much you like it, starting at 0. Clicking `Yes+` increments the score by 1 and sorts the file into a subdirectory. Clicking `Best++` increments score by 2. Clicking `No-` will decrement the score, and if the score is 0 or below the media will be put into a trash folder.

Alternatively you can create your own category folders outside the scoring system.

import sys
import os
import random
import subprocess
import shutil
import traceback
import time
import datetime
from enum import Enum
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QProgressBar, QMainWindow, QFrame, QHBoxLayout, QVBoxLayout, QLineEdit, QStackedLayout
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap, QMovie
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal, QRect

VLC_EXE = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
CHROME_EXE = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
EXPLORER_EXE = r'explorer.exe'

class DisplayMethod(Enum):
    EXECUTABLE = 1
    IMAGE = 2
    MOVIE = 3

class MediaType():
    def __init__(self, extension, executable, displaymethod):
        self.extension = extension
        self.executable = executable
        self.displaymethod = displaymethod

class MediaFile():
    def __init__(self, fullpath, mediatype : MediaType, score=0):
        self.fullpath = fullpath
        self.mediatype = mediatype
        self.score = score


FILETYPES = {}

def add_filetype(t):
    FILETYPES[t.extension] = t

add_filetype(MediaType(".jpg", VLC_EXE, DisplayMethod.IMAGE))
add_filetype(MediaType(".jpeg", VLC_EXE, DisplayMethod.IMAGE))
add_filetype(MediaType(".png", VLC_EXE, DisplayMethod.IMAGE))
add_filetype(MediaType(".webp", VLC_EXE, DisplayMethod.IMAGE))

add_filetype(MediaType(".webm", VLC_EXE, DisplayMethod.EXECUTABLE))
add_filetype(MediaType(".mp4", VLC_EXE, DisplayMethod.EXECUTABLE))
add_filetype(MediaType(".mov", VLC_EXE, DisplayMethod.EXECUTABLE))
add_filetype(MediaType(".wmv", VLC_EXE, DisplayMethod.EXECUTABLE))
add_filetype(MediaType(".mpg", VLC_EXE, DisplayMethod.EXECUTABLE))
add_filetype(MediaType(".avi", VLC_EXE, DisplayMethod.EXECUTABLE))
add_filetype(MediaType(".flv", VLC_EXE, DisplayMethod.EXECUTABLE))

add_filetype(MediaType(".gif", CHROME_EXE, DisplayMethod.MOVIE))
#add_filetype(MediaType(".pdf", CHROME_EXE, DisplayMethod.EXECUTABLE))
add_filetype(MediaType(".url", EXPLORER_EXE, DisplayMethod.EXECUTABLE))

""" Interactively select files from a folder. """

def move(file, dir):
    try:
        os.rename(file, os.path.join(dir, os.path.basename(file)))
    except Exception as e:
        traceback.print_exc()

if len(sys.argv) > 1:
    directory = sys.argv[1]
else:
    raise RuntimeError("No directory specified!")
    
unseen_files = []
seen_files = []
categories = []

def recognize_category_dir(dir):
    dirname = os.path.basename(dir)
    category = dirname[12:]
    categories.append(category)

def recognize_category(category):
    categories.append(category)

def add_seen_files_from_score_dir(dir):
    dirname = os.path.basename(dir)
    score = int(dirname[9:])
    for f in os.listdir(dir):
        fullpath = os.path.join(dir, f)
        filename, extension = os.path.splitext(fullpath)
        if os.path.isfile(fullpath) and extension in FILETYPES:
            mediatype = FILETYPES[extension]
            mediafile = MediaFile(fullpath, mediatype, score=score)
            seen_files.append(mediafile)

def add_unseen_files_from_dir(dir):
    for f in os.listdir(dir):
        fullpath = os.path.join(dir, f)
        filename, extension = os.path.splitext(fullpath)
        if os.path.isfile(fullpath) and extension in FILETYPES:
            mediatype = FILETYPES[extension]
            mediafile = MediaFile(fullpath, mediatype)
            unseen_files.append(mediafile)
        if os.path.isdir(fullpath) and f.startswith("is_rated_"):
            add_seen_files_from_score_dir(fullpath)
        if os.path.isdir(fullpath) and f.startswith("is_category_"):
            recognize_category_dir(fullpath)

add_unseen_files_from_dir(directory)

print("directory:", directory)

def get_full_dir_and_mkdir(dir):
    fulldir = os.path.join(directory, dir)
    if not os.path.isdir(fulldir):
        os.mkdir(fulldir)
    return fulldir

def get_dir_for_score(score):
    if score > 0:
        dir = "is_rated_{}".format(score)
    else:
        dir = "is_trash"
    return get_full_dir_and_mkdir(dir)

def get_dir_for_category(category):
    return get_full_dir_and_mkdir("is_category_{}".format(category))

def get_temp_dir():
    fulldir = os.path.join(directory, "_is_tmp")
    if not os.path.isdir(fulldir):
        os.mkdir(fulldir)
    return fulldir

def get_temp_copy_of_file(fullpath):
    tmpdir = get_temp_dir()
    basename = os.path.basename(fullpath)
    targetfile = os.path.join(tmpdir, basename)
    try:
        shutil.copyfile(fullpath, targetfile)
        return targetfile
    except Exception as e:
        traceback.print_exc()
        return None

def clean_temp_dir():
    tmpdir = os.path.join(directory, "_is_tmp")
    if os.path.isdir(tmpdir):
        for f in os.listdir(tmpdir):
            fullpath = os.path.join(tmpdir, f)
            if os.path.isfile(fullpath):
                try:
                    os.remove(fullpath)
                except Exception:
                    traceback.print_exc()

button_width = 200
button_height = 75
small_button_height = 40
label_height = 30
progress_height = 30

class CategoryButton(QPushButton):
    categoryClicked = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clicked.connect(self.onClicked, Qt.QueuedConnection)

    @pyqtSlot()
    def onClicked(self):
        self.categoryClicked.emit(self.text())

class AspectRatioLabel(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # stores aspect ratio
        self.pixmapWidth = 0
        self.pixmapHeight = 0

    @pyqtSlot(QPixmap)
    def setPixmap(self, pm: QPixmap) -> None:
        self.pixmapWidth = pm.width()
        self.pixmapHeight = pm.height()
        self.updateMargins()
        super().setPixmap(pm)


    @pyqtSlot(QMovie)
    def setMovie(self, movie: QMovie) -> None:
        movie.updated.connect(self.onMovieUpdated)
        super().setMovie(movie)

    @pyqtSlot(QRect)
    def onMovieUpdated(self, rect):
        self.pixmapWidth = rect.width()
        self.pixmapHeight = rect.height()
        self.updateMargins()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.updateMargins()
        super().resizeEvent(a0)


    def updateMargins(self):
        if self.pixmapWidth == 0 or self.pixmapHeight == 0:
            return
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return
        if w * self.pixmapHeight > h * self.pixmapWidth:
            m = (w - (self.pixmapWidth * h / self.pixmapHeight)) / 2
            m = int(m)
            self.setContentsMargins(m, 0, m, 0)
        else:
            m = (h - (self.pixmapHeight * w / self.pixmapWidth)) / 2
            m = int(m)
            self.setContentsMargins(0, m, 0, m)


class App(QMainWindow):

    def makeqss(self, color, hovercolor):
        qss = """
    QPushButton:hover {
        background-color: #%s
    }
    QPushButton {
        background-color: #%s;
    }
                """
        return qss % (hovercolor, color)
    def __init__(self):
        super().__init__()

        self.chosen = None
        self.proc = None
        self.unseen_files_total = len(unseen_files)
        self.seen_files_total = len(seen_files)
        self.likelihood_seen = 0.0

        centralframe = QFrame(self)
        self.setCentralWidget(centralframe)
        centralLayout = QHBoxLayout(centralframe)

        ## Sidebar

        sidebar = QFrame(self)
        self.sidebarLayout = QVBoxLayout(sidebar)
        centralLayout.addWidget(sidebar)
        sidebar.setMaximumWidth(button_width + 30)
            
        self.filelabel = QLabel("file.ext", self)
        self.filelabel.setMinimumSize(button_width, label_height * 2)
        self.sidebarLayout.addWidget(self.filelabel)
        font = self.filelabel.font()
        font.setPointSize(12)
        self.filelabel.setFont(font)


        self.scorelabel = QLabel("Score: -1", self)
        self.scorelabel.setMinimumSize(button_width, label_height)
        self.sidebarLayout.addWidget(self.scorelabel)
        font = self.scorelabel.font()
        font.setPointSize(24)
        self.scorelabel.setFont(font)

        self.unseen_progress = QProgressBar(self)
        self.unseen_progress.setMinimumSize(button_width, progress_height)
        self.unseen_progress.setFormat("%p% - %v/%m")
        self.unseen_progress.setMaximum(self.unseen_files_total)
        self.sidebarLayout.addWidget(self.unseen_progress)

        self.seen_progress = QProgressBar(self)
        self.seen_progress.setMinimumSize(button_width, progress_height)
        self.seen_progress.setFormat("%p% - %v/%m")
        self.seen_progress.setMaximum(self.seen_files_total)
        self.sidebarLayout.addWidget(self.seen_progress)
        
        best_btn = QPushButton('Best++', self)
        best_btn.setMinimumSize(button_width, button_height)
        best_btn.clicked.connect(self.click_best)
        self.sidebarLayout.addWidget(best_btn)
        
        # font for all buttons
        font = best_btn.font()
        font.setPointSize(32)
        
        best_btn.setFont(font)
        best_btn.setStyleSheet(self.makeqss("666055", "eedd00"))
 
        yes_btn = QPushButton('Yes+', self)
        yes_btn.setMinimumSize(button_width, button_height)
        self.sidebarLayout.addWidget(yes_btn)
        yes_btn.clicked.connect(self.click_yes)
        yes_btn.setFont(font)
        yes_btn.setStyleSheet(self.makeqss("556655", "00ff00"))


        no_btn = QPushButton('No-', self)
        no_btn.setMinimumSize(button_width, button_height)
        self.sidebarLayout.addWidget(no_btn)
        no_btn.clicked.connect(self.click_no)
        no_btn.setFont(font)
        no_btn.setStyleSheet(self.makeqss("665555", "ff0000"))


        skip_btn = QPushButton('Skip', self)
        skip_btn.setMinimumSize(button_width, button_height)
        self.sidebarLayout.addWidget(skip_btn)
        skip_btn.clicked.connect(self.click_skip)
        skip_btn.setFont(font)
        skip_btn.setStyleSheet(self.makeqss("555566", "0000ff"))


        categories_title = QLabel("Categories", self)
        categories_title.setMinimumSize(button_width, label_height)
        self.sidebarLayout.addWidget(categories_title)
        font = categories_title.font()
        font.setPointSize(12)
        categories_title.setFont(font)

        category_btn_frame = QFrame(self)
        self.categoryLayout = QVBoxLayout(category_btn_frame)
        self.sidebarLayout.addWidget(category_btn_frame)

        for category in categories:
            self.add_category_button(category)

        new_category_title = QLabel("Create New Category:", self)
        new_category_title.setMinimumSize(button_width, label_height)
        self.sidebarLayout.addWidget(new_category_title)
        font = new_category_title.font()
        font.setPointSize(12)
        new_category_title.setFont(font)
        
        new_category_frame = QFrame(self)
        new_category_layout = QHBoxLayout(new_category_frame)
        self.sidebarLayout.addWidget(new_category_frame)

        self.new_category_lineedit = QLineEdit(self)
        self.new_category_btn = QPushButton("+", self)
        self.new_category_btn.clicked.connect(self.click_new_category)
        new_category_layout.addWidget(self.new_category_lineedit)
        new_category_layout.addWidget(self.new_category_btn)

        ## Content

        self.contentframe = QFrame(self)
        self.contentLayout = QStackedLayout(self.contentframe)
        centralLayout.addWidget(self.contentframe)

        self.imagelabel = AspectRatioLabel(self)
        self.contentLayout.addWidget(self.imagelabel)
        self.contentframe.setMinimumSize(1, 1)
        self.contentframe.hide()

        ## Window

        self.setWindowTitle("Interactive Sort")
        self.move(0, 50)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        self.resize(10,10)

        self.expanded_size_x = self.width() + 800

    def hide_content(self):
        if not self.contentframe.isHidden():
            self.expanded_size_x = self.width()
            self.contentframe.hide()
            self.resize(10, self.height())

    def show_content(self):
        if self.contentframe.isHidden():
            self.contentframe.show()
            self.resize(self.expanded_size_x, self.height())

    def stop_movie(self):
        movie = self.imagelabel.movie()
        if movie is not None:
            movie.stop()
            self.imagelabel.clear()
            del movie


    def add_category_button(self, category):
        category_btn = CategoryButton(category, self)
        category_btn.setMinimumSize(button_width, small_button_height)
        self.categoryLayout.addWidget(category_btn)
        category_btn.categoryClicked.connect(self.click_category, Qt.QueuedConnection)
        font = category_btn.font()
        font.setPointSize(16)
        category_btn.setFont(font)
        category_btn.setStyleSheet(self.makeqss("999999", "dddddd"))

    @pyqtSlot()
    def cleanup_app(self):
        self.cleanup_proc()
        clean_temp_dir()

    def cleanup_proc(self):
        self.stop_movie()
        if self.proc is not None:
            self.proc.kill()
            self.proc.wait()
            time.sleep(0.1)

    def close(self):
        self.cleanup_proc()
        super().close()
        
    def set_filelabel(self, f):
        text = os.path.basename(f.fullpath)
        if os.path.isfile(f.fullpath):
            stat = os.stat(f.fullpath)
            ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
            text += '\n' + str(ctime)
        self.filelabel.setText(text)
        self.scorelabel.setText('Score: ' + str(f.score))
        

    def choose_next(self):
        self.chosen = None
        if self.chosen is None and len(seen_files):
            # Add 0.4% likelihood each turn, up to 35%
            # self.likelihood_seen = min(0.35, self.likelihood_seen + 0.004)
            # roll for viewing a seen file instead of an unseen one
            if random.random() < self.likelihood_seen or len(unseen_files) == 0:
                index = random.randint(0, len(seen_files)-1)
                self.chosen = seen_files[index]
                del seen_files[index]

        if self.chosen is None and len(unseen_files):
            index = random.randint(0, len(unseen_files)-1)
            self.chosen = unseen_files[index]
            del unseen_files[index]

        if self.chosen is None:
            print('All done!')
            QApplication.quit()
        else:
            self.display_mediafile(self.chosen)

            self.set_filelabel(self.chosen)
            unseen_done = self.unseen_files_total - len(unseen_files)
            seen_done = self.seen_files_total - len(seen_files)
            self.unseen_progress.setValue(unseen_done)
            self.seen_progress.setValue(seen_done)

    def display_mediafile(self, mediafile):
        displaymethod = mediafile.mediatype.displaymethod
        if displaymethod is DisplayMethod.EXECUTABLE:
            self.hide_content()
            args = [mediafile.mediatype.executable, mediafile.fullpath]
            self.proc = subprocess.Popen(args, shell=False)
        elif displaymethod is DisplayMethod.IMAGE:
            self.show_content()
            img = QPixmap(mediafile.fullpath)
            self.imagelabel.setPixmap(img)
            self.imagelabel.setScaledContents(True)
        elif displaymethod is DisplayMethod.MOVIE:
            self.show_content()
            tmpfile = get_temp_copy_of_file(mediafile.fullpath)
            movie = QMovie(tmpfile)
            self.imagelabel.setMovie(movie)
            self.imagelabel.setScaledContents(True)
            self.imagelabel.updateMargins()
            movie.start()


    @pyqtSlot()
    def click_yes(self):
        if self.chosen:
            print("yes to this file:", self.chosen.fullpath)
            self.cleanup_proc()
            self.chosen.score += 1
            scoredir = get_dir_for_score(self.chosen.score)
            move(self.chosen.fullpath, scoredir)
            self.choose_next()

    @pyqtSlot()
    def click_no(self):
        if self.chosen:
            print("no to this file:", self.chosen.fullpath)
            self.cleanup_proc()
            self.chosen.score -= 1
            scoredir = get_dir_for_score(self.chosen.score)
            move(self.chosen.fullpath, scoredir)
            self.choose_next()
            
    @pyqtSlot()
    def click_best(self):
        if self.chosen:
            print("best to this file:", self.chosen.fullpath)
            self.cleanup_proc()
            self.chosen.score += 2
            scoredir = get_dir_for_score(self.chosen.score)
            move(self.chosen.fullpath, scoredir)
            self.choose_next()

    @pyqtSlot()
    def click_skip(self):
        if self.chosen:
            print("skipping file:", self.chosen.fullpath)
            self.cleanup_proc()
            self.choose_next()

    @pyqtSlot(str)
    def click_category(self, category):
        print("category clicked: ", category)
        if self.chosen:
            print("category", category, "to this file:", self.chosen.fullpath)
            self.cleanup_proc()
            categorydir = get_dir_for_category(category)
            move(self.chosen.fullpath, categorydir)
            self.choose_next()


    @pyqtSlot()
    def click_new_category(self):
        category = self.new_category_lineedit.text()
        print("make a new category: ", category)
        recognize_category(category)
        self.add_category_button(category)
        self.new_category_lineedit.setText("")
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    random.seed()
    window.show()
    window.choose_next()
    app.aboutToQuit.connect(window.cleanup_app)
    sys.exit(app.exec_())


import sys
import json
import subprocess
from os import listdir
from os.path import isfile, join

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QStatusBar,
    QTextEdit,
    QToolBar
)

from PySide6.QtGui import (
    QAction,        
    QIcon,
    QPixmap
)

from PySide6.QtCore import (
    QSize,
    Qt
)

class FilterInfo(QWidget):
    def __init__(self):
        super().__init__()

        title = QLabel("Keywords:")
        control = QTextEdit()

        layout = QHBoxLayout()
        layout.addWidget(title)
        layout.addWidget(control)

        self.resize(512, 256)

        self.setLayout(layout)
        

class ProductInfo(QWidget):
    def __init__(self):
        super().__init__()
        self.title = QLabel()
        self.title.setTextFormat(Qt.RichText)
        self.title.setAlignment(Qt.AlignLeft)

        self.resize(512,1080-256)

        layout = QVBoxLayout()
        layout.addWidget(self.title)

        self.setLayout(layout)

    def setContent(self, product):
        self.title.setText(f"""<b>{product['title']}</b>""")

class ImageGallery(QWidget):
    def __init__(self):
        super().__init__()

        self.db = {}
        self.product_map = {}

        self.setWindowTitle ("Content Gallery")

        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setIconSize(QSize(256,256))
        self.list_widget.itemClicked.connect(self.show_image)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.product_filter = FilterInfo()
        self.product_filter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.product_info = ProductInfo()
        self.product_info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.rightpanel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget (self.product_filter)
        layout.addWidget (self.product_info)
        self.rightpanel.setLayout (layout)
        
        layoutAll = QHBoxLayout()
        layoutAll.addWidget (self.list_widget)
        layoutAll.addWidget (self.rightpanel)

        self.setLayout (layoutAll)
        

        # Get array of files
        files = self.get_files()

        self.add_images (files)

    def get_files(self):
        files=[]
        content = json.load(open('pretty.json', 'r'))
        for cname in content:
            for pname in content[cname]:
                product = content[cname][pname]
                icon_path = product['iconPath']
                files.append(icon_path)
                self.product_map[icon_path] = product

        print (f'Added {len(files)} products.')

        self.db = content

        return files

    def add_images(self, image_paths):
        for path in image_paths:
            pixmap = QPixmap (path)
            item = QListWidgetItem()
            item.setIcon (QIcon(pixmap))
            item.setData(Qt.UserRole, path)
            self.list_widget.addItem(item)

    def show_image(self, item):
        path = item.data(Qt.UserRole)
        product_info = self.product_map[path]
        label = f"""
        {product_info['title']}
        {product_info['artistNames']}
        """
        
        self.product_info.setContent(product=product_info)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle ("Content Pilot 1.0")

        gallery=ImageGallery()
        self.setCentralWidget(gallery)


        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)

        load_action = QAction("Load DB", self)
        load_action.setStatusTip("Fetch metadata from Studio and refresh search indexes")
        load_action.triggered.connect(self.loadButtonClicked)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quitButtonClicked)

        statusbar= QStatusBar(self)
        self.setStatusBar(statusbar)

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(load_action)
        file_menu.addAction(quit_action)
        
        self.resize(1920,1080)

    def quitButtonClicked(self, s):
        sys.exit(-1)

    def loadButtonClicked(self, s):
        self.reloadDatabase()


    def reloadDatabase(self):
        print (f'Executing system call to download metadata')
        subprocess.run([
            "C:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe",
            "-noPrompt",
            "-noDefaultScene",
            "-cleanOnLaunch",
            '0',
            "-instanceName",
            "50001",
            'x:/working/content_viewer2/DB_List_Products.dsa'
        ])
        print (f'Metadata download complete.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

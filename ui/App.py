import os
import sys
import random
from GalleryViewer import ImageGallery, CommandPanel, DetailPanel, ImageData
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout
)

class App(QWidget):
    def __init__(self, images, parent=None):
        super().__init__(parent)

        # Create UI Elements
        self.application_layout = QGridLayout()
        self.command_panel_layout = QVBoxLayout()
        self.gallery_panel_layout = QVBoxLayout()
        self.detail_panel_layout = QVBoxLayout()

        self.command_panel = CommandPanel()
        self.command_panel_layout.addWidget (self.command_panel)

        self.image_gallery = ImageGallery(images)
        self.gallery_panel_layout.addWidget(self.image_gallery)

        self.detail_panel = DetailPanel()
        self.detail_panel_layout.addWidget(self.detail_panel)

        self.application_layout.addLayout(self.command_panel_layout, 0, 0)
        self.application_layout.addLayout(self.gallery_panel_layout, 0, 1)
        self.application_layout.addLayout(self.detail_panel_layout, 0, 2)

        self.setLayout(self.application_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    catlist=["nature", "animals", "abstract", "cool", "machinery"]
    collist=["red", "green", "blue", "indigo", "violet", "black", "white"]

    images=[]
    files=os.listdir("data")
    n=0
    for file in files:
        img=ImageData(f"data/{file}",
                     category=random.choice(catlist),
                     color=random.choice(collist))
        images.append(img)
        n+=1
        if (n>32):
            break


    app_widget = App(images)
    app_widget.setWindowTitle("Content Viewer 2")
    app_widget.show()
    
#    gallery = ImageGallery(images)
#    gallery.setWindowTitle("Image Gallery")
#    gallery.show()

    sys.exit(app.exec())

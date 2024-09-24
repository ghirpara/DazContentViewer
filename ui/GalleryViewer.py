import os
import sys
import random
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QPushButton,
    QGridLayout,
    QLineEdit,
)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QFont, QColor
from PySide6.QtCore import Qt, QSize, QPoint


class MixImage(QLabel):
    id_counter=0
    
    def __init__(self, path):
        QLabel.__init__(self)
        self.pixmap = QPixmap(path)
        self.setPixmap(self.pixmap.scaled(QSize(512, 512), Qt.KeepAspectRatio))
        self.id = MixImage.id_counter

        MixImage.id_counter +=1
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

        self.draw_badge (painter, "G8F", 20, 20)
        self.draw_badge (painter, str(self.id), 20, 40)

        painter.end()

    def draw_badge(self, painter, text, x, y):
        painter.setFont(QFont("Arial", 12))
        painter.setPen(QColor("white"))
        painter.setBrush(QColor(255, 0, 0, 128))
        painter.drawRoundedRect(x, y, 40, 25, 10, 10)
        painter.drawText(x + 10, y + 18, text)
        
        
class MixWidget(QWidget):

    def __init__(self, image_data):
        QWidget.__init__(self)
        self.image = MixImage(image_data.path)
        self.label = QLabel(image_data.path)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget (self.image)
        self.layout.addWidget(self.label)

class ImageData:
    """Represents data for an image, including its path and attributes."""

    def __init__(self, path, **attributes):
        self.path = path
        self.attributes = attributes

    def matches_filter(self, filter_dict):
        """Checks if the image matches a given filter dictionary."""
        rv=True
        for key, value in filter_dict.items():
            if key in self.attributes and self.attributes[key] != value:
                rv=False
                break
        return rv

class ImageGallery(QWidget):
    def __init__(self, images, parent=None):
        super().__init__(parent)

        self.images = images
        self.current_filter = {}  # Start with no filter

        # Create UI elements
        self.image_layout = QGridLayout()
        self.image_area = QWidget()
        self.image_area.setLayout(self.image_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_area)
        self.scroll_area.setWidgetResizable(True)

        self.filter_layout = QGridLayout()
        self.filter_label = QLabel("Filter:")
        self.filter_line_edits = {}
        self.filter_buttons = {}
        self.filter_apply_button = QPushButton("Apply Filter")

        self.common_layout = QHBoxLayout()
        self.quit_button = QPushButton("Quit")
        self.common_layout.addWidget(self.quit_button)

        # Add filter widgets
        for i, attribute in enumerate(self.images[0].attributes):
            label = QLabel(f"{attribute}:")
            line_edit = QLineEdit()
            self.filter_line_edits[attribute] = line_edit
            button = QPushButton(QIcon("filter.png"), "")  # Use a filter icon
            self.filter_buttons[attribute] = button
            self.filter_layout.addWidget(label, i, 0)
            self.filter_layout.addWidget(line_edit, i, 1)
            self.filter_layout.addWidget(button, i, 2)

        self.filter_layout.addWidget(self.filter_apply_button, len(self.images[0].attributes), 0, 1, 3)

        # Connect signals and slots
        self.filter_apply_button.clicked.connect(self.apply_filter)
        for button in self.filter_buttons.values():
            button.clicked.connect(self.update_filter)

        self.quit_button.clicked.connect(self.safe_quit)

        self.biglabel1 = QLabel ("1  THIS IS A PLACEHOLDER")
        self.biglabel2 = QLabel ("2  THIS IS A PLACEHOLDER")
        self.biglabel3 = QLabel ("3  THIS IS A PLACEHOLDER")

        left_panel_layout = QVBoxLayout()
        left_panel_layout.addWidget(self.scroll_area)
        left_panel_layout.addLayout(self.filter_layout)
        left_panel_layout.addLayout(self.common_layout)

        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(self.biglabel1)
        right_panel_layout.addWidget(self.biglabel2)
        right_panel_layout.addWidget(self.biglabel3)

        # Create main layout
        main_layout = QGridLayout()
        main_layout.addLayout(left_panel_layout, 0, 0)
        main_layout.addLayout(right_panel_layout, 0, 1)
        
        self.setLayout(main_layout)

        self.update_gallery()  # Initially display all images

    def safe_quit(self):
        sys.exit(0)

    def update_filter(self):
        sender = self.sender()
        attribute = [key for key, value in self.filter_buttons.items() if value == sender][0]
        line_edit = self.filter_line_edits[attribute]
        filter_value = line_edit.text()
        self.current_filter[attribute] = filter_value if filter_value else None

    def apply_filter(self):
        self.update_gallery()

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())): 
            layout.takeAt(i).widget().hide()
            
    def update_gallery(self):
        self.clear_layout(self.image_layout)
        row = 0
        col = 0
        for i, image_data in enumerate(self.images):
            if image_data.matches_filter(self.current_filter):
                mixwidget = MixWidget(image_data)
                self.image_layout.addWidget(mixwidget, row, col)
                col += 1
                if col > 3:  # Adjust column limit as needed
                    col = 0
                    row += 1

        # Re-layout the image area to ensure all widgets are correctly sized
        self.image_area.adjustSize()


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
#        n=n+1
#        if (n>256):
#            break

    gallery = ImageGallery(images)
    gallery.setWindowTitle("Image Gallery")
    gallery.show()

    sys.exit(app.exec())

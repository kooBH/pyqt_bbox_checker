from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication,QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider,QVBoxLayout, QWidget)
from PyQt6.QtGui import QImage,QPixmap

# https://doc.qt.io/qt-6/opengl-changes-qt6.html
#from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import numpy as np
import cv2

class bboxChecker(QWidget):
    def __init__(self, parent=None):
        super(bboxChecker, self).__init__(parent)

        self.layout_main = QVBoxLayout()

        #self.widget_display = QOpenGLWidget()
        self.widget_display = QLabel()
        self.layout_main.addWidget(self.widget_display)

        self.widget_slider = QSlider(Qt.Orientation.Horizontal)
        self.layout_main.addWidget(self.widget_slider)

        self.layout_control = QHBoxLayout()
        self.btn_load = QPushButton("Load")
        self.label_frame = QLabel("/")
        self.layout_control.addWidget(self.btn_load)
        self.layout_control.addWidget(self.label_frame)
        self.layout_main.addLayout(self.layout_control)

        self.label_path = QLabel(".")
        self.layout_main.addWidget(self.label_path)

        self.setLayout(self.layout_main)

        self.btn_load.pressed.connect(self.showDialog)

        self.label_frame.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.widget_slider.valueChanged.connect(self.display)
        self.frameCount = 0
    

    

    def showDialog(self):
        path = QFileDialog.getOpenFileName(self, 'Open file', './', "mp4 (*.mp4)")
        # (path, type)
        path = str(path[0])
        self.path = path

        print(path)
        if path == "" :
            pass
        else :
            self.label_path.setText(path)
            self.load(path)

    def load(self,path):
        cap = cv2.VideoCapture(path)
        self.frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.buf = np.empty((self.frameCount, self.frameHeight, self.frameWidth, 3), np.dtype('uint8'))
        print(self.buf.shape)

        self.widget_slider.setRange(0,self.frameCount)

        fc = 0
        ret = True

        while (fc < self.frameCount  and ret):
            ret, self.buf[fc] = cap.read()
            fc += 1
        cap.release()

        self.display(0)

    def display(self,idx):
        if self.frameCount <=0:
            return
        if idx < 0 or idx >= self.frameCount:
            return

        tmp = self.buf[idx]

        cv2.rectangle(tmp, (50,50), (100,100), (0,255,0), 2)

        qImg = QImage(tmp, self.frameWidth, self.frameHeight, self.frameWidth*3, QImage.Format.Format_BGR888)
        pixmap01 = QPixmap.fromImage(qImg)
        pixmap_image = QPixmap(pixmap01)
        self.widget_display.setPixmap(pixmap_image)

        self.label_frame.setText(str(idx)+" / "+str(self.frameCount))

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    gallery = bboxChecker()
    gallery.show()
    sys.exit(app.exec()) 

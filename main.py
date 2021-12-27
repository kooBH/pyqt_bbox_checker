from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QApplication,QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider,QVBoxLayout, QWidget)
from PyQt6.QtGui import QImage,QPixmap

# https://doc.qt.io/qt-6/opengl-changes-qt6.html
#from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import numpy as np
import cv2

class bboxChecker(QWidget):
    def __init__(self, parent=None):
        super(bboxChecker, self).__init__(parent)

        self.idx = 0
        self.w = 1280
        self.h = 720
        self.frameCount = 0
        self.cap = None

        ## PyQt6 GUI
        self.layout_main = QVBoxLayout()

        #self.widget_display = QOpenGLWidget()
        self.widget_display = QLabel()
        self.layout_main.addWidget(self.widget_display)

        self.widget_slider = QSlider(Qt.Orientation.Horizontal)
        self.layout_main.addWidget(self.widget_slider)

        self.layout_control = QHBoxLayout()
        self.btn_load = QPushButton("Load")
        self.label_frame = QLabel("/")
        self.btn_left = QPushButton("<-")
        self.btn_right = QPushButton("->")
        self.layout_control.addWidget(self.btn_load)
        self.layout_control.addWidget(self.label_frame)
        self.layout_control.addWidget(self.btn_left)
        self.layout_control.addWidget(self.btn_right)
        self.layout_main.addLayout(self.layout_control)

        self.label_path = QLabel(".")
        self.layout_main.addWidget(self.label_path)

        self.setLayout(self.layout_main)

        self.btn_load.pressed.connect(self.showDialog)

        self.widget_display.setFixedSize(QSize(1280,720))
        self.label_frame.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.widget_slider.sliderMoved.connect(self.display)


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
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(path)
        self.frameCount = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.widget_slider.setRange(0,self.frameCount)


        self.display(0)

    def display(self,idx):
        if self.frameCount <=0:
            return
        if idx < 0 or idx >= self.frameCount:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES,idx)
        ret,tmp = self.cap.read()

        if not ret :
            return

        tmp = cv2.resize(tmp,(self.w,self.h),interpolation = cv2.INTER_LINEAR )
        cv2.rectangle(tmp, (50,50), (100,100), (0,255,0), 2)

        qImg = QImage(tmp, self.w, self.h, self.w*3, QImage.Format.Format_BGR888)
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

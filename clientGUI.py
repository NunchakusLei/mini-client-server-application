#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, cv2, socket, numpy as np, struct
from func import blockDCT, blockIDCT, blockZigzag, lengthCoding
from common_func import *
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QLineEdit, QSlider, QLabel
from PyQt5.QtCore import Qt
from pyQt_show_image import ImageWidget


port = 60001                    # Reserve a port for your service.


class ClientApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.cvImg = None
        self.host = ""
        self.L_value = 1
        self.connected = False
        self.initUI()
        self.s = socket.socket()        # Create a socket object

    def initUI(self):

        self.statusBar()

        self.filename = QLineEdit(self)
        self.filename.move(20, 70)
        self.filename.resize(280,20)
        self.filename.setPlaceholderText("Image file path")
        self.filename.textChanged[str].connect(self.onFilenameChanged)

        self.hostname = QLineEdit(self)
        self.hostname.move(20, 40)
        self.hostname.resize(280,20)
        self.hostname.setPlaceholderText("Server host name")
        self.hostname.textChanged[str].connect(self.onHostnameChanged)

        self.connect_btn = QPushButton("Send", self)
        self.connect_btn.move(30, 100)
        self.connect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self.connect_callback)

        self.preview_btn = QPushButton("Preview", self)
        self.preview_btn.move(150, 100)
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self.preview_callback)

        self.L_value_label = QLabel(self)
        self.L_value_label.setGeometry(320, 10, 50, 30)
        self.L_value_label.setText("L value: " + str(1))
        self.L_value_label.adjustSize()

        L_value_sld = QSlider(Qt.Horizontal, self)
        L_value_sld.setFocusPolicy(Qt.NoFocus)
        L_value_sld.valueChanged[int].connect(self.changeLValue)
        L_value_sld.setMinimum(1)
        L_value_sld.setMaximum(8)
        L_value_sld.setGeometry(20, 10, 280, 30)
        L_value_sld.resize(280,30)

        self.setGeometry(720, 300, 420, 170)
        self.setWindowTitle('Client')
        self.show()

    def changeLValue(self, value):
        self.L_value_label.setText("L value: " + str(value))
        self.L_value_label.adjustSize()
        self.L_value = value

    def preview_callback(self):
        self.image_preview = ImageWidget(self.cvImg, description="Client's image")

    def onHostnameChanged(self, hostname):
        self.host = hostname
        if len(hostname)==0 or self.cvImg is None:
            self.connect_btn.setEnabled(False)
        else:
            self.connect_btn.setEnabled(True)

    def onFilenameChanged(self, filename):
        self.cvImg = cv2.imread(filename, 0)
        if self.cvImg is None:
            self.statusBar().showMessage("Error! file could not load. Please check the filename.")
            self.preview_btn.setEnabled(False)
            self.connect_btn.setEnabled(False)
        else:
            self.statusBar().showMessage("")
            self.preview_btn.setEnabled(True)
            self.onHostnameChanged(self.hostname.text())

    def connect_callback(self):
        print("connecting...")
        self.statusBar().showMessage("connecting...")

        self.s = socket.socket()        # Create a socket object

        try:
            self.s.connect((self.host, port))
            print("Connected to server.")
            self.statusBar().showMessage("Connected to server.")

            self.sendImage()

        except ConnectionRefusedError as e:
            self.statusBar().showMessage(str(e))
            print(str(e))
        else:
            self.connected = True

    def sendImage(self):

        Q = createQ(self.L_value)
        encoded_img = blockDCT(self.cvImg.astype(np.float64),Q.shape,Q)
        max_value = np.max(encoded_img)
        min_value = np.min(encoded_img)
        image = normalize(encoded_img)
        h, w = self.cvImg.shape

        zigzaged_image = blockZigzag(image, Q.shape, Q)

        image = lengthCoding(zigzaged_image)

        try:
            self.s.send(struct.pack("f", float(max_value)))
            self.s.send(struct.pack("f", float(min_value)))
            self.s.send(struct.pack("f", float(h)))
            self.s.send(struct.pack("f", float(w)))
            self.s.send(bytearray([self.L_value]))

            # send the image
            for i in range(len(image)):
                value = bytearray([image[i]])
                self.s.send(value)
            # for i in range((image.shape)[0]):
            #     for j in range((image.shape)[1]):
            #         value = bytearray([image[i][j]])
            #         self.s.send(value)
            #         # print(image[i][j])
        except BrokenPipeError as e:
            self.statusBar().showMessage(str(e))
            self.s.close()
        else:
            print('Done sending.\n')
            self.statusBar().showMessage('Done sending.')

            self.disconnect()

    def disconnect(self):
        self.s.close()
        self.connected = False
        del self.s


if __name__ == '__main__':

    app = QApplication(sys.argv)
    client = ClientApp()
    sys.exit(app.exec_())

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, cv2, socket, numpy as np, struct
from func import blockIDCT, blockUnzigzag, lengthDecoding
from common_func import *
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QLineEdit, QSlider, QLabel
from PyQt5.QtCore import Qt
from pyQt_show_image import ImageWidget


port = 60001                    # Reserve a port for your service.


class ServerApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.cvImg = None
        self.L_value = 1
        self.connected = False
        self.initUI()
        self.s = socket.socket()        # Create a socket object

    def initUI(self):

        self.statusBar()

        self.hostname = QLineEdit(self)
        self.hostname.move(20, 10)
        self.hostname.resize(280,20)
        self.hostname.setPlaceholderText("Server host name")
        self.hostname.textChanged[str].connect(self.onHostnameChanged)

        self.filename = QLineEdit(self)
        self.filename.move(20, 40)
        self.filename.resize(280,20)
        self.filename.setPlaceholderText("Save as")
        self.filename.textChanged[str].connect(self.onFilenameChanged)

        self.save_btn = QPushButton("Save", self)
        self.save_btn.move(304, 36)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.saveImage)

        self.connect_btn = QPushButton("Establish", self)
        self.connect_btn.move(30, 70)
        self.connect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self.runServer)

        self.recv_btn = QPushButton("Receive", self)
        self.recv_btn.move(150, 70)
        self.recv_btn.setEnabled(False)
        self.recv_btn.clicked.connect(self.receiveImage)

        self.setGeometry(300, 300, 420, 140)
        self.setWindowTitle('Server')
        self.show()

    def receiveImage(self):
        self.statusBar().showMessage("")

        self.readyForConnection()

        conn = self.conn

        data = b''
        while len(data)<4:
            data += conn.recv(4)
        max_value = struct.unpack("f", data)[0]

        data = b''
        while len(data)<4:
            data += conn.recv(4)
        min_value = struct.unpack("f", data)[0]

        data = b''
        while len(data)<4:
            data += conn.recv(4)
        h = struct.unpack("f", data)[0]

        data = b''
        while len(data)<4:
            data += conn.recv(4)
        w = struct.unpack("f", data)[0]

        received_image_size = (int(h), int(w))

        data = b''
        while len(data)<1:
            data += conn.recv(1)
        L = bytearray(data)[0]

        # print(max_value, min_value, L)

        received_len = 4 + 4 + 4 + 1
        received_image = []
        while True:

            data = conn.recv(1024)
            # print("HI")
            if not data:
                break
            received_len += len(data)

            my_bytes = bytearray(data)
            for i in range(len(my_bytes)):
                num = my_bytes[i]
                # print("Received number:", num)
                received_image.append(num)

        conn.close()

        print("The recv len:", received_len)
        # print("The length of the image", len(received_image))
        myQ = createQ(L)

        length_decoded_image = lengthDecoding(received_image)

        unzigzaged_image = blockUnzigzag(received_image_size, length_decoded_image, myQ.shape)

        received_image = np.reshape(unzigzaged_image, received_image_size)
        scaled_img = (received_image.astype(np.float64) / 255.0) * (max_value - min_value) + min_value


        decoded_img = blockIDCT(scaled_img, myQ.shape, myQ)
        # print(np.max(decoded_img), np.min(decoded_img))

        self.cvImg = normalize_cutoff_higher_and_lower(decoded_img).astype(np.uint8)

        self.image_preview = ImageWidget(self.cvImg, description="Server's image")
        print("The length of the image:", self.cvImg.shape[0]*self.cvImg.shape[1])
        # print("MSE:", compute_MSE(self.cvImg, cv2.imread("SampleImage.tif", 0)))
        print()

        self.recv_btn.setEnabled(True)
        self.onFilenameChanged(self.filename.text())

        self.statusBar().showMessage("New image received and displayed.")


    def onHostnameChanged(self, hostname):
        self.host = hostname
        if len(hostname)==0:
            self.connect_btn.setEnabled(False)
        else:
            self.connect_btn.setEnabled(True)


    def onFilenameChanged(self, filename):
        # cvImg = cv2.imread("SampleImage.tif", 0)
        if len(filename) == 0:
            self.statusBar().showMessage("No file name.")
            self.save_btn.setEnabled(False)
        elif self.cvImg is None:
            pass
        else:
            self.statusBar().showMessage("")
            if self.connected:
                self.save_btn.setEnabled(True)

    def readyForConnection(self):
        print("Server awaiting for client to connect ...")
        self.statusBar().showMessage("Server awaiting for client to connect ...")
        self.s.listen(5)                 # Now wait for client connection.
        conn, addr = self.s.accept()     # Establish connection with client.
        print('Got connection from', addr)
        self.statusBar().showMessage('Got connection from ' + str(addr))

        self.conn = conn
        self.recv_btn.setEnabled(True)
        self.connected = True

        if self.cvImg is not None:
            self.save_btn.setEnabled(True)

    def runServer(self):
        self.statusBar().showMessage("Establishing server ...")

        self.s = socket.socket()        # Create a socket object

        try:
            self.statusBar().showMessage("Server established")

            self.s.bind((self.host, port))   # Bind to the port

        except Exception as e:
            self.statusBar().showMessage(str(e))
        else:
            self.connect_btn.setEnabled(False)
            self.recv_btn.setEnabled(True)

    def saveImage(self):
        cv2.imwrite(self.filename.text(), self.cvImg)
        self.statusBar().showMessage("Image saved to "+self.filename.text())



if __name__ == '__main__':

    app = QApplication(sys.argv)
    server = ServerApp()
    sys.exit(app.exec_())

import sys, cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage

class ImageWidget(QWidget):

    def __init__(self, cvImg, description="image"):
        super().__init__()
        self.title = description
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.cvImg = cvImg
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # convert to Qt image
        height, width = self.cvImg.shape
        bytesPerLine = width
        qImg = QImage(self.cvImg.data, width, height, bytesPerLine, QImage.Format_Grayscale8)

        # Create widget
        label = QLabel(self)
        pixmap = QPixmap(qImg)
        label.setPixmap(pixmap)
        self.resize(pixmap.width(),pixmap.height())

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cvImg = cv2.imread("SampleImage.tif", 0)
    ex = ImageWidget(cvImg)
    sys.exit(app.exec_())

from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import sys
import mss
import numpy as np
import signal
import cv2 as cv

def mask_image(imgdata, imgtype='jpg', size=64):
    """Return a ``QPixmap`` from *imgdata* masked with a smooth circle.

    *imgdata* are the raw image bytes, *imgtype* denotes the image type.

    The returned image will have a size of *size* × *size* pixels.

    """
    # Load image and convert to 32-bit ARGB (adds an alpha channel):
    image = QImage.fromData(imgdata, imgtype)
    image.convertToFormat(QImage.Format_ARGB32)

    # Crop image to a square:
    imgsize = min(image.width(), image.height())
    rect = QRect(
        (image.width() - imgsize) / 2,
        (image.height() - imgsize) / 2,
        imgsize,
        imgsize,
    )
    image = image.copy(rect)

    # Create the output image with the same dimensions and an alpha channel
    # and make it completely transparent:
    out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
    out_img.fill(Qt.transparent)

    # Create a texture brush and paint a circle with the original image onto
    # the output image:
    brush = QBrush(image)        # Create texture brush
    painter = QPainter(out_img)  # Paint the output image
    painter.setBrush(brush)      # Use the image texture brush
    painter.setPen(Qt.NoPen)     # Don't draw an outline
    painter.setRenderHint(QPainter.Antialiasing, True)  # Use AA
    painter.drawEllipse(0, 0, imgsize, imgsize)  # Actually draw the circle
    painter.end()                # We are done (segfault if you forget this)

    # Convert the image to a pixmap and rescale it.  Take pixel ratio into
    # account to get a sharp image on retina displays:
    pr = QWindow().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    return pm

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    with mss.mss() as sct:
        # Get raw pixels from the screen, save it to a Numpy array
        im = np.array(sct.grab(sct.monitors[1]))
    
    cv.imshow("screenshot", im)
    cv.waitKey(0)
    cv.destroyAllWindows()
    
    

    app = QApplication(sys.argv)

    # Create widget
    label = QLabel()
    label2 = QLabel()
    h, w, c = im.shape
    print(h, w ,c)

    print('Removing alpha..')
    im = im[:,:,:3].copy()
    h, w, c = im.shape
    print('New shape: {},{},{}'.format(h, w, c))

    
    print(im.strides[0])
    qImg = QImage(im, w, h, QImage.Format_RGB888).rgbSwapped()

    #qImg = QImage(np.require(im, np.uint8, 'C'), w, h, im.strides[0], QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qImg)
    label.setPixmap(pixmap)
    label.resize(pixmap.width(), pixmap.height())

    label.keyPressEvent = app.quit()
     

    label.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowType_Mask)
    monitor = QDesktopWidget().screenGeometry(0)
    label.move(monitor.left(), monitor.top())
    #label.showFullScreen()
    label.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
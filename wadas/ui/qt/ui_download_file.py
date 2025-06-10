# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'download_file.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QWidget,
)


class Ui_DialogDownloadFile(object):
    def setupUi(self, DialogDownloadFile):
        if not DialogDownloadFile.objectName():
            DialogDownloadFile.setObjectName("DialogDownloadFile")
        DialogDownloadFile.resize(396, 128)
        self.label = QLabel(DialogDownloadFile)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 10, 371, 20))
        self.progressBar = QProgressBar(DialogDownloadFile)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setGeometry(QRect(10, 50, 371, 23))
        self.progressBar.setValue(0)
        self.pushButton_download = QPushButton(DialogDownloadFile)
        self.pushButton_download.setObjectName("pushButton_download")
        self.pushButton_download.setGeometry(QRect(200, 90, 75, 24))
        self.pushButton_cancel = QPushButton(DialogDownloadFile)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.pushButton_cancel.setGeometry(QRect(120, 90, 75, 24))

        self.retranslateUi(DialogDownloadFile)

        QMetaObject.connectSlotsByName(DialogDownloadFile)

    # setupUi

    def retranslateUi(self, DialogDownloadFile):
        DialogDownloadFile.setWindowTitle(
            QCoreApplication.translate("DialogDownloadFile", "Download file", None)
        )
        self.label.setText(
            QCoreApplication.translate(
                "DialogDownloadFile", "Click Download button to start.", None
            )
        )
        self.pushButton_download.setText(
            QCoreApplication.translate("DialogDownloadFile", "Download", None)
        )
        self.pushButton_cancel.setText(
            QCoreApplication.translate("DialogDownloadFile", "Cancel", None)
        )

    # retranslateUi

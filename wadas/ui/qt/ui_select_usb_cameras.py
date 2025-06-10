# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_usb_cameras.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QTabWidget, QWidget)

class Ui_DialogSelectUSBCameras(object):
    def setupUi(self, DialogSelectUSBCameras):
        if not DialogSelectUSBCameras.objectName():
            DialogSelectUSBCameras.setObjectName(u"DialogSelectUSBCameras")
        DialogSelectUSBCameras.resize(640, 480)
        self.buttonBox = QDialogButtonBox(DialogSelectUSBCameras)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 440, 621, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.label_errorMessage = QLabel(DialogSelectUSBCameras)
        self.label_errorMessage.setObjectName(u"label_errorMessage")
        self.label_errorMessage.setGeometry(QRect(10, 410, 621, 20))
        self.tabWidget = QTabWidget(DialogSelectUSBCameras)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 621, 391))
        self.tab_directInputs = QWidget()
        self.tab_directInputs.setObjectName(u"tab_directInputs")
        self.label_4 = QLabel(self.tab_directInputs)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 10, 601, 16))
        self.gridLayoutWidget_2 = QWidget(self.tab_directInputs)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(10, 30, 601, 331))
        self.gridLayout_localCameras = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_localCameras.setObjectName(u"gridLayout_localCameras")
        self.gridLayout_localCameras.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_directInputs, "")
        self.tab_camerasList = QWidget()
        self.tab_camerasList.setObjectName(u"tab_camerasList")
        self.gridLayoutWidget = QWidget(self.tab_camerasList)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 601, 351))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_threshold = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_threshold.setObjectName(u"lineEdit_threshold")

        self.gridLayout.addWidget(self.lineEdit_threshold, 0, 1, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.lineEdit_minContourArea = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_minContourArea.setObjectName(u"lineEdit_minContourArea")

        self.gridLayout.addWidget(self.lineEdit_minContourArea, 1, 1, 1, 1)

        self.lineEdit_detectionThreshold = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_detectionThreshold.setObjectName(u"lineEdit_detectionThreshold")

        self.gridLayout.addWidget(self.lineEdit_detectionThreshold, 2, 1, 1, 1)

        self.tabWidget.addTab(self.tab_camerasList, "")

        self.retranslateUi(DialogSelectUSBCameras)
        self.buttonBox.accepted.connect(DialogSelectUSBCameras.accept)
        self.buttonBox.rejected.connect(DialogSelectUSBCameras.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DialogSelectUSBCameras)
    # setupUi

    def retranslateUi(self, DialogSelectUSBCameras):
        DialogSelectUSBCameras.setWindowTitle(QCoreApplication.translate("DialogSelectUSBCameras", u"USB Camera(s) configuration", None))
        self.label_errorMessage.setText("")
        self.label_4.setText(QCoreApplication.translate("DialogSelectUSBCameras", u"Select local camera(s) you want to enable and provide unique ID for it.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_directInputs), QCoreApplication.translate("DialogSelectUSBCameras", u"Local cameras", None))
        self.label.setText(QCoreApplication.translate("DialogSelectUSBCameras", u"Sensitivity (threshold):", None))
        self.label_2.setText(QCoreApplication.translate("DialogSelectUSBCameras", u"Minimum contour area (px):", None))
        self.label_3.setText(QCoreApplication.translate("DialogSelectUSBCameras", u"Image detection threshold (img/s):", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_camerasList), QCoreApplication.translate("DialogSelectUSBCameras", u"Detection params", None))
    # retranslateUi


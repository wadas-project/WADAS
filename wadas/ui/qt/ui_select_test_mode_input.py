# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_test_mode_input.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QButtonGroup, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QSizePolicy,
    QWidget)

class Ui_DialogSelectTestModeInput(object):
    def setupUi(self, DialogSelectTestModeInput):
        if not DialogSelectTestModeInput.objectName():
            DialogSelectTestModeInput.setObjectName(u"DialogSelectTestModeInput")
        DialogSelectTestModeInput.resize(567, 193)
        self.buttonBox = QDialogButtonBox(DialogSelectTestModeInput)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 160, 551, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.gridLayoutWidget = QWidget(DialogSelectTestModeInput)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 541, 121))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.radioButton_url = QRadioButton(self.gridLayoutWidget)
        self.buttonGroup_2 = QButtonGroup(DialogSelectTestModeInput)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")
        self.buttonGroup_2.addButton(self.radioButton_url)
        self.radioButton_url.setObjectName(u"radioButton_url")
        self.radioButton_url.setChecked(True)

        self.gridLayout.addWidget(self.radioButton_url, 2, 0, 1, 1)

        self.line = QFrame(self.gridLayoutWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 1, 0, 1, 3)

        self.radioButton_video = QRadioButton(self.gridLayoutWidget)
        self.buttonGroup = QButtonGroup(DialogSelectTestModeInput)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButton_video)
        self.radioButton_video.setObjectName(u"radioButton_video")

        self.gridLayout.addWidget(self.radioButton_video, 0, 1, 1, 1)

        self.radioButton_image = QRadioButton(self.gridLayoutWidget)
        self.buttonGroup.addButton(self.radioButton_image)
        self.radioButton_image.setObjectName(u"radioButton_image")
        self.radioButton_image.setChecked(True)

        self.gridLayout.addWidget(self.radioButton_image, 0, 0, 1, 1)

        self.radioButton_file = QRadioButton(self.gridLayoutWidget)
        self.buttonGroup_2.addButton(self.radioButton_file)
        self.radioButton_file.setObjectName(u"radioButton_file")

        self.gridLayout.addWidget(self.radioButton_file, 3, 0, 1, 1)

        self.pushButton_select_file = QPushButton(self.gridLayoutWidget)
        self.pushButton_select_file.setObjectName(u"pushButton_select_file")

        self.gridLayout.addWidget(self.pushButton_select_file, 3, 2, 1, 1)

        self.lineEdit_url = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_url.setObjectName(u"lineEdit_url")

        self.gridLayout.addWidget(self.lineEdit_url, 2, 1, 1, 1)

        self.lineEdit_file = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_file.setObjectName(u"lineEdit_file")

        self.gridLayout.addWidget(self.lineEdit_file, 3, 1, 1, 1)

        self.label_error = QLabel(DialogSelectTestModeInput)
        self.label_error.setObjectName(u"label_error")
        self.label_error.setGeometry(QRect(10, 140, 541, 16))

        self.retranslateUi(DialogSelectTestModeInput)
        self.buttonBox.accepted.connect(DialogSelectTestModeInput.accept)
        self.buttonBox.rejected.connect(DialogSelectTestModeInput.reject)

        QMetaObject.connectSlotsByName(DialogSelectTestModeInput)
    # setupUi

    def retranslateUi(self, DialogSelectTestModeInput):
        DialogSelectTestModeInput.setWindowTitle(QCoreApplication.translate("DialogSelectTestModeInput", u"Select Test Model Mode input", None))
        self.radioButton_url.setText(QCoreApplication.translate("DialogSelectTestModeInput", u"URL", None))
        self.radioButton_video.setText(QCoreApplication.translate("DialogSelectTestModeInput", u"Video", None))
        self.radioButton_image.setText(QCoreApplication.translate("DialogSelectTestModeInput", u"Image", None))
        self.radioButton_file.setText(QCoreApplication.translate("DialogSelectTestModeInput", u"File", None))
        self.pushButton_select_file.setText(QCoreApplication.translate("DialogSelectTestModeInput", u"Select File", None))
        self.lineEdit_url.setPlaceholderText("")
        self.label_error.setText("")
    # retranslateUi


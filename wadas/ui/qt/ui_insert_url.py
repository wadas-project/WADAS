# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'insert_url.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_InsertUrlDialog(object):
    def setupUi(self, InsertUrlDialog):
        if not InsertUrlDialog.objectName():
            InsertUrlDialog.setObjectName(u"InsertUrlDialog")
        InsertUrlDialog.resize(640, 109)
        self.buttonBox = QDialogButtonBox(InsertUrlDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(0, 70, 621, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.verticalLayoutWidget = QWidget(InsertUrlDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 621, 61))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.lineEdit_url = QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_url.setObjectName(u"lineEdit_url")

        self.verticalLayout.addWidget(self.lineEdit_url)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(InsertUrlDialog)
        self.buttonBox.accepted.connect(InsertUrlDialog.accept)
        self.buttonBox.rejected.connect(InsertUrlDialog.reject)

        QMetaObject.connectSlotsByName(InsertUrlDialog)
    # setupUi

    def retranslateUi(self, InsertUrlDialog):
        InsertUrlDialog.setWindowTitle(QCoreApplication.translate("InsertUrlDialog", u"Insert image URL", None))
        self.label.setText(QCoreApplication.translate("InsertUrlDialog", u"URL:", None))
        self.lineEdit_url.setText(QCoreApplication.translate("InsertUrlDialog", u"https://www.parks.it/tmpFoto/30079_4_PNALM.jpeg", None))
    # retranslateUi


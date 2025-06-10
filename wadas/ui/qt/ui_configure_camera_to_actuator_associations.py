# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_camera_to_actuator_associations.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QTreeView, QWidget)

class Ui_DialogCameraActuatorAssociation(object):
    def setupUi(self, DialogCameraActuatorAssociation):
        if not DialogCameraActuatorAssociation.objectName():
            DialogCameraActuatorAssociation.setObjectName(u"DialogCameraActuatorAssociation")
        DialogCameraActuatorAssociation.resize(640, 480)
        self.treeView = QTreeView(DialogCameraActuatorAssociation)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setGeometry(QRect(10, 30, 621, 401))
        self.label = QLabel(DialogCameraActuatorAssociation)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 621, 16))
        self.pushButton_expandTreeView = QPushButton(DialogCameraActuatorAssociation)
        self.pushButton_expandTreeView.setObjectName(u"pushButton_expandTreeView")
        self.pushButton_expandTreeView.setGeometry(QRect(10, 440, 75, 24))
        self.pushButton_collapseTreeView = QPushButton(DialogCameraActuatorAssociation)
        self.pushButton_collapseTreeView.setObjectName(u"pushButton_collapseTreeView")
        self.pushButton_collapseTreeView.setGeometry(QRect(90, 440, 75, 24))
        self.pushButton_close = QPushButton(DialogCameraActuatorAssociation)
        self.pushButton_close.setObjectName(u"pushButton_close")
        self.pushButton_close.setGeometry(QRect(550, 440, 75, 24))

        self.retranslateUi(DialogCameraActuatorAssociation)

        QMetaObject.connectSlotsByName(DialogCameraActuatorAssociation)
    # setupUi

    def retranslateUi(self, DialogCameraActuatorAssociation):
        DialogCameraActuatorAssociation.setWindowTitle(QCoreApplication.translate("DialogCameraActuatorAssociation", u"Camera to Actuator associations", None))
        self.label.setText(QCoreApplication.translate("DialogCameraActuatorAssociation", u"Double click on a camera from the list to edit actuator(s) to associate:", None))
        self.pushButton_expandTreeView.setText(QCoreApplication.translate("DialogCameraActuatorAssociation", u"Expand all", None))
        self.pushButton_collapseTreeView.setText(QCoreApplication.translate("DialogCameraActuatorAssociation", u"Compress all", None))
        self.pushButton_close.setText(QCoreApplication.translate("DialogCameraActuatorAssociation", u"Close", None))
    # retranslateUi


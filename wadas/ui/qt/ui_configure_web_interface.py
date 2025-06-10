# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_web_interface.ui'
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
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_DialogConfigureWebInterface(object):
    def setupUi(self, DialogConfigureWebInterface):
        if not DialogConfigureWebInterface.objectName():
            DialogConfigureWebInterface.setObjectName(u"DialogConfigureWebInterface")
        DialogConfigureWebInterface.resize(634, 445)
        self.buttonBox = QDialogButtonBox(DialogConfigureWebInterface)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 410, 611, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(False)
        self.verticalLayoutWidget = QWidget(DialogConfigureWebInterface)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 50, 611, 301))
        self.verticalLayout_users = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_users.setObjectName(u"verticalLayout_users")
        self.verticalLayout_users.setContentsMargins(0, 0, 0, 0)
        self.label_errorMessage = QLabel(DialogConfigureWebInterface)
        self.label_errorMessage.setObjectName(u"label_errorMessage")
        self.label_errorMessage.setGeometry(QRect(20, 400, 601, 16))
        self.horizontalLayoutWidget = QWidget(DialogConfigureWebInterface)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 10, 611, 31))
        self.horizontalLayout_web_int_status = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_web_int_status.setObjectName(u"horizontalLayout_web_int_status")
        self.horizontalLayout_web_int_status.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.horizontalLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_web_int_status.addWidget(self.label_2)

        self.label_web_interface_status = QLabel(self.horizontalLayoutWidget)
        self.label_web_interface_status.setObjectName(u"label_web_interface_status")

        self.horizontalLayout_web_int_status.addWidget(self.label_web_interface_status)

        self.pushButton_start_web_interface = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_start_web_interface.setObjectName(u"pushButton_start_web_interface")

        self.horizontalLayout_web_int_status.addWidget(self.pushButton_start_web_interface)

        self.pushButton_stop_web_interface = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_stop_web_interface.setObjectName(u"pushButton_stop_web_interface")

        self.horizontalLayout_web_int_status.addWidget(self.pushButton_stop_web_interface)

        self.horizontalLayoutWidget_2 = QWidget(DialogConfigureWebInterface)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(10, 360, 611, 31))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_add_user = QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_add_user.setObjectName(u"pushButton_add_user")

        self.horizontalLayout.addWidget(self.pushButton_add_user)

        self.pushButton_remove_user = QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_remove_user.setObjectName(u"pushButton_remove_user")

        self.horizontalLayout.addWidget(self.pushButton_remove_user)

        self.pushButton_reset_password = QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_reset_password.setObjectName(u"pushButton_reset_password")

        self.horizontalLayout.addWidget(self.pushButton_reset_password)


        self.retranslateUi(DialogConfigureWebInterface)
        self.buttonBox.accepted.connect(DialogConfigureWebInterface.accept)
        self.buttonBox.rejected.connect(DialogConfigureWebInterface.reject)

        QMetaObject.connectSlotsByName(DialogConfigureWebInterface)
    # setupUi

    def retranslateUi(self, DialogConfigureWebInterface):
        DialogConfigureWebInterface.setWindowTitle(QCoreApplication.translate("DialogConfigureWebInterface", u"Configure web interface", None))
        self.label_errorMessage.setText("")
        self.label_2.setText(QCoreApplication.translate("DialogConfigureWebInterface", u"Web interface status:", None))
        self.label_web_interface_status.setText("")
        self.pushButton_start_web_interface.setText(QCoreApplication.translate("DialogConfigureWebInterface", u"Start", None))
        self.pushButton_stop_web_interface.setText(QCoreApplication.translate("DialogConfigureWebInterface", u"Stop", None))
        self.pushButton_add_user.setText(QCoreApplication.translate("DialogConfigureWebInterface", u"Add user", None))
        self.pushButton_remove_user.setText(QCoreApplication.translate("DialogConfigureWebInterface", u"Remove user", None))
        self.pushButton_reset_password.setText(QCoreApplication.translate("DialogConfigureWebInterface", u"Reset user password", None))
    # retranslateUi


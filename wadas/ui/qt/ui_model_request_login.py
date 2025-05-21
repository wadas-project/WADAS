# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'model_request_login.ui'
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
    QGridLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_DialogModelRequestLogin(object):
    def setupUi(self, DialogModelRequestLogin):
        if not DialogModelRequestLogin.objectName():
            DialogModelRequestLogin.setObjectName(u"DialogModelRequestLogin")
        DialogModelRequestLogin.resize(484, 207)
        self.gridLayout = QGridLayout(DialogModelRequestLogin)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_error = QLabel(DialogModelRequestLogin)
        self.label_error.setObjectName(u"label_error")

        self.gridLayout.addWidget(self.label_error, 5, 0, 1, 2)

        self.buttonBox = QDialogButtonBox(DialogModelRequestLogin)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)

        self.pushButton_request = QPushButton(DialogModelRequestLogin)
        self.pushButton_request.setObjectName(u"pushButton_request")

        self.gridLayout.addWidget(self.pushButton_request, 1, 1, 1, 1)

        self.groupBox_login = QGroupBox(DialogModelRequestLogin)
        self.groupBox_login.setObjectName(u"groupBox_login")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_login.sizePolicy().hasHeightForWidth())
        self.groupBox_login.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(self.groupBox_login)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_2 = QLabel(self.groupBox_login)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_3 = QLabel(self.groupBox_login)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.lineEdit_token = QLineEdit(self.groupBox_login)
        self.lineEdit_token.setObjectName(u"lineEdit_token")
        self.lineEdit_token.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout_2.addWidget(self.lineEdit_token, 2, 1, 1, 1)

        self.lineEdit_email = QLineEdit(self.groupBox_login)
        self.lineEdit_email.setObjectName(u"lineEdit_email")

        self.gridLayout_2.addWidget(self.lineEdit_email, 1, 1, 1, 1)

        self.label = QLabel(self.groupBox_login)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 2)


        self.gridLayout.addWidget(self.groupBox_login, 0, 0, 1, 2)

        self.label_request_title = QLabel(DialogModelRequestLogin)
        self.label_request_title.setObjectName(u"label_request_title")

        self.gridLayout.addWidget(self.label_request_title, 1, 0, 1, 1)

        QWidget.setTabOrder(self.lineEdit_email, self.lineEdit_token)
        QWidget.setTabOrder(self.lineEdit_token, self.pushButton_request)

        self.retranslateUi(DialogModelRequestLogin)
        self.buttonBox.accepted.connect(DialogModelRequestLogin.accept)
        self.buttonBox.rejected.connect(DialogModelRequestLogin.reject)

        QMetaObject.connectSlotsByName(DialogModelRequestLogin)
    # setupUi

    def retranslateUi(self, DialogModelRequestLogin):
        DialogModelRequestLogin.setWindowTitle(QCoreApplication.translate("DialogModelRequestLogin", u"Ai models access - Login", None))
        self.label_error.setText("")
        self.pushButton_request.setText(QCoreApplication.translate("DialogModelRequestLogin", u"Request access", None))
        self.groupBox_login.setTitle(QCoreApplication.translate("DialogModelRequestLogin", u"Login", None))
        self.label_2.setText(QCoreApplication.translate("DialogModelRequestLogin", u"Email:", None))
        self.label_3.setText(QCoreApplication.translate("DialogModelRequestLogin", u"Token:", None))
        self.label.setText(QCoreApplication.translate("DialogModelRequestLogin", u"Insert your credentials to download the AI models:", None))
        self.label_request_title.setText(QCoreApplication.translate("DialogModelRequestLogin", u"If you don't have credentials please request them:", None))
    # retranslateUi


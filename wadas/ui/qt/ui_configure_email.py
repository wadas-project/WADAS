# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_email.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGridLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTextEdit, QWidget)

class Ui_DialogConfigureEmail(object):
    def setupUi(self, DialogConfigureEmail):
        if not DialogConfigureEmail.objectName():
            DialogConfigureEmail.setObjectName(u"DialogConfigureEmail")
        DialogConfigureEmail.resize(522, 397)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DialogConfigureEmail.sizePolicy().hasHeightForWidth())
        DialogConfigureEmail.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(DialogConfigureEmail)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(DialogConfigureEmail)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayoutWidget = QWidget(self.tab_3)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 461, 254))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_password = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_password.setObjectName(u"lineEdit_password")
        self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.lineEdit_password, 4, 3, 1, 2)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)

        self.pushButton_testEmail = QPushButton(self.gridLayoutWidget)
        self.pushButton_testEmail.setObjectName(u"pushButton_testEmail")

        self.gridLayout.addWidget(self.pushButton_testEmail, 7, 3, 1, 2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 6, 4, 1, 1)

        self.lineEdit_smtpServer = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_smtpServer.setObjectName(u"lineEdit_smtpServer")

        self.gridLayout.addWidget(self.lineEdit_smtpServer, 5, 3, 1, 2)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 5, 1, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 6, 1, 1, 1)

        self.plainTextEdit_test_log = QPlainTextEdit(self.gridLayoutWidget)
        self.plainTextEdit_test_log.setObjectName(u"plainTextEdit_test_log")
        self.plainTextEdit_test_log.setReadOnly(True)

        self.gridLayout.addWidget(self.plainTextEdit_test_log, 8, 3, 1, 2)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 4, 1, 1, 1)

        self.lineEdit_senderEmail = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_senderEmail.setObjectName(u"lineEdit_senderEmail")

        self.gridLayout.addWidget(self.lineEdit_senderEmail, 0, 3, 1, 2)

        self.lineEdit_port = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_port.setObjectName(u"lineEdit_port")

        self.gridLayout.addWidget(self.lineEdit_port, 6, 3, 1, 1)

        self.lineEdit_username = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_username.setObjectName(u"lineEdit_username")

        self.gridLayout.addWidget(self.lineEdit_username, 3, 4, 1, 1)

        self.checkBox_username = QCheckBox(self.gridLayoutWidget)
        self.checkBox_username.setObjectName(u"checkBox_username")

        self.gridLayout.addWidget(self.checkBox_username, 3, 1, 1, 3)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.textEdit_recipient_email = QTextEdit(self.tab_4)
        self.textEdit_recipient_email.setObjectName(u"textEdit_recipient_email")
        self.textEdit_recipient_email.setGeometry(QRect(10, 50, 481, 161))
        self.label_5 = QLabel(self.tab_4)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 10, 471, 16))
        self.label_6 = QLabel(self.tab_4)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 30, 481, 16))
        self.tabWidget.addTab(self.tab_4, "")

        self.gridLayout_2.addWidget(self.tabWidget, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(DialogConfigureEmail)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 1)

        self.label_status = QLabel(DialogConfigureEmail)
        self.label_status.setObjectName(u"label_status")

        self.gridLayout_2.addWidget(self.label_status, 2, 0, 1, 1)

        self.checkBox_email_en = QCheckBox(DialogConfigureEmail)
        self.checkBox_email_en.setObjectName(u"checkBox_email_en")

        self.gridLayout_2.addWidget(self.checkBox_email_en, 0, 0, 1, 1)

        QWidget.setTabOrder(self.lineEdit_senderEmail, self.lineEdit_password)
        QWidget.setTabOrder(self.lineEdit_password, self.lineEdit_smtpServer)
        QWidget.setTabOrder(self.lineEdit_smtpServer, self.lineEdit_port)
        QWidget.setTabOrder(self.lineEdit_port, self.pushButton_testEmail)

        self.retranslateUi(DialogConfigureEmail)
        self.buttonBox.accepted.connect(DialogConfigureEmail.accept)
        self.buttonBox.rejected.connect(DialogConfigureEmail.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DialogConfigureEmail)
    # setupUi

    def retranslateUi(self, DialogConfigureEmail):
        DialogConfigureEmail.setWindowTitle(QCoreApplication.translate("DialogConfigureEmail", u"Configure Email notifications", None))
        self.label.setText(QCoreApplication.translate("DialogConfigureEmail", u"Sender email", None))
        self.pushButton_testEmail.setText(QCoreApplication.translate("DialogConfigureEmail", u"Test email", None))
        self.label_3.setText(QCoreApplication.translate("DialogConfigureEmail", u"SMTP server", None))
        self.label_4.setText(QCoreApplication.translate("DialogConfigureEmail", u"Port", None))
        self.label_2.setText(QCoreApplication.translate("DialogConfigureEmail", u"Password", None))
        self.checkBox_username.setText(QCoreApplication.translate("DialogConfigureEmail", u"Username (if different from sender email):", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("DialogConfigureEmail", u"Sender", None))
        self.label_5.setText(QCoreApplication.translate("DialogConfigureEmail", u"Insert recipients email address(es) separated by comma and space. ", None))
        self.label_6.setText(QCoreApplication.translate("DialogConfigureEmail", u"Example: email1@domail.com, email2@domail.com, email3@domail.com", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("DialogConfigureEmail", u"Recipients", None))
        self.label_status.setText("")
        self.checkBox_email_en.setText(QCoreApplication.translate("DialogConfigureEmail", u"Enable email notifications", None))
    # retranslateUi


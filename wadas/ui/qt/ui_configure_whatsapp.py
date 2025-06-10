# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_whatsapp.ui'
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
    QPlainTextEdit, QPushButton, QSizePolicy, QTabWidget,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_DialogConfigureWhatsApp(object):
    def setupUi(self, DialogConfigureWhatsApp):
        if not DialogConfigureWhatsApp.objectName():
            DialogConfigureWhatsApp.setObjectName(u"DialogConfigureWhatsApp")
        DialogConfigureWhatsApp.resize(552, 352)
        self.buttonBox = QDialogButtonBox(DialogConfigureWhatsApp)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 320, 531, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.label_errorMessage = QLabel(DialogConfigureWhatsApp)
        self.label_errorMessage.setObjectName(u"label_errorMessage")
        self.label_errorMessage.setGeometry(QRect(10, 300, 531, 20))
        self.tabWidget = QTabWidget(DialogConfigureWhatsApp)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 40, 531, 241))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayoutWidget = QWidget(self.tab)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 521, 211))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.checkBox_allowImg = QCheckBox(self.gridLayoutWidget)
        self.checkBox_allowImg.setObjectName(u"checkBox_allowImg")
        self.checkBox_allowImg.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_allowImg, 4, 0, 1, 2)

        self.plainTextEdit_testMessageLog = QPlainTextEdit(self.gridLayoutWidget)
        self.plainTextEdit_testMessageLog.setObjectName(u"plainTextEdit_testMessageLog")
        self.plainTextEdit_testMessageLog.setReadOnly(True)

        self.gridLayout_2.addWidget(self.plainTextEdit_testMessageLog, 6, 1, 1, 1)

        self.lineEdit_phoneID = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_phoneID.setObjectName(u"lineEdit_phoneID")

        self.gridLayout_2.addWidget(self.lineEdit_phoneID, 1, 1, 1, 1)

        self.pushButton_testMessage = QPushButton(self.gridLayoutWidget)
        self.pushButton_testMessage.setObjectName(u"pushButton_testMessage")

        self.gridLayout_2.addWidget(self.pushButton_testMessage, 5, 1, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)

        self.lineEdit_accessToken = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_accessToken.setObjectName(u"lineEdit_accessToken")
        self.lineEdit_accessToken.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout_2.addWidget(self.lineEdit_accessToken, 2, 1, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayoutWidget = QWidget(self.tab_2)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(9, 9, 511, 201))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.textEdit_recipientsNumbers = QTextEdit(self.verticalLayoutWidget)
        self.textEdit_recipientsNumbers.setObjectName(u"textEdit_recipientsNumbers")

        self.verticalLayout.addWidget(self.textEdit_recipientsNumbers)

        self.tabWidget.addTab(self.tab_2, "")
        self.label_3 = QLabel(DialogConfigureWhatsApp)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(8, 280, 531, 20))
        self.checkBox_enableWhatsAppNotifications = QCheckBox(DialogConfigureWhatsApp)
        self.checkBox_enableWhatsAppNotifications.setObjectName(u"checkBox_enableWhatsAppNotifications")
        self.checkBox_enableWhatsAppNotifications.setGeometry(QRect(10, 10, 481, 20))
        self.checkBox_enableWhatsAppNotifications.setChecked(True)
        self.checkBox_enableWhatsAppNotifications.setTristate(False)

        self.retranslateUi(DialogConfigureWhatsApp)
        self.buttonBox.accepted.connect(DialogConfigureWhatsApp.accept)
        self.buttonBox.rejected.connect(DialogConfigureWhatsApp.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DialogConfigureWhatsApp)
    # setupUi

    def retranslateUi(self, DialogConfigureWhatsApp):
        DialogConfigureWhatsApp.setWindowTitle(QCoreApplication.translate("DialogConfigureWhatsApp", u"Configure WhatsApp notifications", None))
        self.label_errorMessage.setText("")
        self.checkBox_allowImg.setText(QCoreApplication.translate("DialogConfigureWhatsApp", u"Enable detection/classification image attachment to the notification message", None))
        self.pushButton_testMessage.setText(QCoreApplication.translate("DialogConfigureWhatsApp", u"Test Message", None))
        self.label_2.setText(QCoreApplication.translate("DialogConfigureWhatsApp", u"Phone number ID:", None))
        self.label.setText(QCoreApplication.translate("DialogConfigureWhatsApp", u"Access token:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("DialogConfigureWhatsApp", u"Sender", None))
        self.label_4.setText(QCoreApplication.translate("DialogConfigureWhatsApp", u"List phone receiver numbers split by commas.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("DialogConfigureWhatsApp", u"Receivers", None))
        self.label_3.setText(QCoreApplication.translate("DialogConfigureWhatsApp", u"NOTE: WhatsApp name and logo are copyright of WhatsApp Inc.", None))
        self.checkBox_enableWhatsAppNotifications.setText(QCoreApplication.translate("DialogConfigureWhatsApp", u"Enable WhatsApp notifications", None))
    # retranslateUi


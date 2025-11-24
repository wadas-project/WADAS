# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_telegramweEGWU.ui'
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
    QDialogButtonBox, QGridLayout, QLabel, QPlainTextEdit,
    QPushButton, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_DialogConfigureTelegram(object):
    def setupUi(self, DialogConfigureTelegram):
        if not DialogConfigureTelegram.objectName():
            DialogConfigureTelegram.setObjectName(u"DialogConfigureTelegram")
        DialogConfigureTelegram.resize(528, 426)
        self.buttonBox = QDialogButtonBox(DialogConfigureTelegram)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(0, 390, 511, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.tabWidget = QTabWidget(DialogConfigureTelegram)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 30, 521, 311))
        self.tab_sender = QWidget()
        self.tab_sender.setObjectName(u"tab_sender")
        self.gridLayoutWidget = QWidget(self.tab_sender)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 501, 261))
        self.gridLayout_sender = QGridLayout(self.gridLayoutWidget)
        self.gridLayout_sender.setObjectName(u"gridLayout_sender")
        self.gridLayout_sender.setContentsMargins(0, 0, 0, 0)
        self.checkBox_enable_images = QCheckBox(self.gridLayoutWidget)
        self.checkBox_enable_images.setObjectName(u"checkBox_enable_images")

        self.gridLayout_sender.addWidget(self.checkBox_enable_images, 0, 0, 1, 2)

        self.plainTextEdit = QPlainTextEdit(self.gridLayoutWidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setReadOnly(True)

        self.gridLayout_sender.addWidget(self.plainTextEdit, 2, 1, 1, 1)

        self.pushButton_test_message = QPushButton(self.gridLayoutWidget)
        self.pushButton_test_message.setObjectName(u"pushButton_test_message")

        self.gridLayout_sender.addWidget(self.pushButton_test_message, 1, 1, 1, 1)

        self.tabWidget.addTab(self.tab_sender, "")
        self.tab_receivers = QWidget()
        self.tab_receivers.setObjectName(u"tab_receivers")
        self.pushButton_add_receiver = QPushButton(self.tab_receivers)
        self.pushButton_add_receiver.setObjectName(u"pushButton_add_receiver")
        self.pushButton_add_receiver.setGeometry(QRect(10, 250, 241, 24))
        self.pushButton_remove_receiver = QPushButton(self.tab_receivers)
        self.pushButton_remove_receiver.setObjectName(u"pushButton_remove_receiver")
        self.pushButton_remove_receiver.setGeometry(QRect(260, 250, 251, 24))
        self.verticalLayoutWidget = QWidget(self.tab_receivers)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 501, 231))
        self.verticalLayout_receivers = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_receivers.setObjectName(u"verticalLayout_receivers")
        self.verticalLayout_receivers.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_receivers, "")
        self.label_errorMessage = QLabel(DialogConfigureTelegram)
        self.label_errorMessage.setObjectName(u"label_errorMessage")
        self.label_errorMessage.setGeometry(QRect(10, 340, 511, 20))
        self.checkBox_enable_telegram_notifications = QCheckBox(DialogConfigureTelegram)
        self.checkBox_enable_telegram_notifications.setObjectName(u"checkBox_enable_telegram_notifications")
        self.checkBox_enable_telegram_notifications.setGeometry(QRect(10, 10, 621, 20))
        self.label_2 = QLabel(DialogConfigureTelegram)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 370, 501, 20))

        self.retranslateUi(DialogConfigureTelegram)
        self.buttonBox.accepted.connect(DialogConfigureTelegram.accept)
        self.buttonBox.rejected.connect(DialogConfigureTelegram.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DialogConfigureTelegram)
    # setupUi

    def retranslateUi(self, DialogConfigureTelegram):
        DialogConfigureTelegram.setWindowTitle(QCoreApplication.translate("DialogConfigureTelegram", u"Configure Telegram notifications", None))
        self.checkBox_enable_images.setText(QCoreApplication.translate("DialogConfigureTelegram", u"Enable images in Telegram notification messages", None))
        self.pushButton_test_message.setText(QCoreApplication.translate("DialogConfigureTelegram", u"Test Message", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_sender), QCoreApplication.translate("DialogConfigureTelegram", u"Sender", None))
        self.pushButton_add_receiver.setText(QCoreApplication.translate("DialogConfigureTelegram", u"Add Receiver", None))
        self.pushButton_remove_receiver.setText(QCoreApplication.translate("DialogConfigureTelegram", u"Remove Receiver", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_receivers), QCoreApplication.translate("DialogConfigureTelegram", u"Receivers", None))
        self.label_errorMessage.setText("")
        self.checkBox_enable_telegram_notifications.setText(QCoreApplication.translate("DialogConfigureTelegram", u"Enable Telegram notifications", None))
        self.label_2.setText(QCoreApplication.translate("DialogConfigureTelegram", u"NOTE: Telegram name and logo are copyright of Telegram LLC.", None))
    # retranslateUi


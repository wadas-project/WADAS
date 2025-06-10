# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ai_model_download.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
    QLabel, QLineEdit, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_AiModelDownloadDialog(object):
    def setupUi(self, AiModelDownloadDialog):
        if not AiModelDownloadDialog.objectName():
            AiModelDownloadDialog.setObjectName(u"AiModelDownloadDialog")
        AiModelDownloadDialog.resize(456, 227)
        self.gridLayoutWidget = QWidget(AiModelDownloadDialog)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 440, 201))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.checkBox_select_versions = QCheckBox(self.gridLayoutWidget)
        self.checkBox_select_versions.setObjectName(u"checkBox_select_versions")

        self.gridLayout.addWidget(self.checkBox_select_versions, 7, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 1, 1, 1)

        self.progressBar = QProgressBar(self.gridLayoutWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.gridLayout.addWidget(self.progressBar, 9, 1, 1, 2)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 4, 1, 1, 2)

        self.pushButton_select_model_version = QPushButton(self.gridLayoutWidget)
        self.pushButton_select_model_version.setObjectName(u"pushButton_select_model_version")

        self.gridLayout.addWidget(self.pushButton_select_model_version, 7, 2, 1, 1)

        self.label_welcome_message = QLabel(self.gridLayoutWidget)
        self.label_welcome_message.setObjectName(u"label_welcome_message")

        self.gridLayout.addWidget(self.label_welcome_message, 0, 1, 1, 2)

        self.pushButton_download = QPushButton(self.gridLayoutWidget)
        self.pushButton_download.setObjectName(u"pushButton_download")

        self.gridLayout.addWidget(self.pushButton_download, 10, 2, 1, 1)

        self.pushButton_cancel = QPushButton(self.gridLayoutWidget)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")

        self.gridLayout.addWidget(self.pushButton_cancel, 10, 1, 1, 1)

        self.lineEdit_token = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_token.setObjectName(u"lineEdit_token")
        self.lineEdit_token.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.lineEdit_token, 5, 1, 1, 2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 8, 1, 1, 1)


        self.retranslateUi(AiModelDownloadDialog)

        QMetaObject.connectSlotsByName(AiModelDownloadDialog)
    # setupUi

    def retranslateUi(self, AiModelDownloadDialog):
        AiModelDownloadDialog.setWindowTitle(QCoreApplication.translate("AiModelDownloadDialog", u"Download AI Models", None))
        self.checkBox_select_versions.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Select model(s) version (optional)", None))
        self.label.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Insert your Hugging Face access token:", None))
        self.pushButton_select_model_version.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Select version", None))
        self.label_welcome_message.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Ai Model files not found. Download is required to let WADAS work.", None))
        self.pushButton_download.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Download Models", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Cancel", None))
    # retranslateUi


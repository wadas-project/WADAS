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
    QGroupBox, QLabel, QProgressBar, QPushButton,
    QSizePolicy, QWidget)

class Ui_AiModelDownloadDialog(object):
    def setupUi(self, AiModelDownloadDialog):
        if not AiModelDownloadDialog.objectName():
            AiModelDownloadDialog.setObjectName(u"AiModelDownloadDialog")
        AiModelDownloadDialog.resize(456, 175)
        self.gridLayout_2 = QGridLayout(AiModelDownloadDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_cancel = QPushButton(AiModelDownloadDialog)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")

        self.gridLayout_2.addWidget(self.pushButton_cancel, 6, 0, 1, 1)

        self.groupBox_available_models = QGroupBox(AiModelDownloadDialog)
        self.groupBox_available_models.setObjectName(u"groupBox_available_models")

        self.gridLayout_2.addWidget(self.groupBox_available_models, 2, 0, 1, 2)

        self.pushButton_download = QPushButton(AiModelDownloadDialog)
        self.pushButton_download.setObjectName(u"pushButton_download")

        self.gridLayout_2.addWidget(self.pushButton_download, 6, 1, 1, 1)

        self.label = QLabel(AiModelDownloadDialog)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 2)

        self.checkBox_select_versions = QCheckBox(AiModelDownloadDialog)
        self.checkBox_select_versions.setObjectName(u"checkBox_select_versions")

        self.gridLayout_2.addWidget(self.checkBox_select_versions, 1, 0, 1, 2)

        self.label_download_status = QLabel(AiModelDownloadDialog)
        self.label_download_status.setObjectName(u"label_download_status")

        self.gridLayout_2.addWidget(self.label_download_status, 4, 0, 1, 2)

        self.progressBar = QProgressBar(AiModelDownloadDialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.gridLayout_2.addWidget(self.progressBar, 5, 0, 1, 2)


        self.retranslateUi(AiModelDownloadDialog)

        QMetaObject.connectSlotsByName(AiModelDownloadDialog)
    # setupUi

    def retranslateUi(self, AiModelDownloadDialog):
        AiModelDownloadDialog.setWindowTitle(QCoreApplication.translate("AiModelDownloadDialog", u"Download AI Models", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Cancel", None))
        self.groupBox_available_models.setTitle(QCoreApplication.translate("AiModelDownloadDialog", u"Available models:", None))
        self.pushButton_download.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Download Models", None))
        self.label.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Click Download Models to proceed with defaults WADAS model selection.", None))
        self.checkBox_select_versions.setText(QCoreApplication.translate("AiModelDownloadDialog", u"Select model(s) version manually (optional)", None))
        self.label_download_status.setText("")
    # retranslateUi


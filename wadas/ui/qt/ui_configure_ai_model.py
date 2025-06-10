# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_ai_model.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGridLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_DialogConfigureAi(object):
    def setupUi(self, DialogConfigureAi):
        if not DialogConfigureAi.objectName():
            DialogConfigureAi.setObjectName(u"DialogConfigureAi")
        DialogConfigureAi.resize(400, 317)
        self.buttonBox = QDialogButtonBox(DialogConfigureAi)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 280, 381, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.gridLayoutWidget = QWidget(DialogConfigureAi)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 381, 272))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_classificationThreshold = QLabel(self.gridLayoutWidget)
        self.label_classificationThreshold.setObjectName(u"label_classificationThreshold")

        self.gridLayout.addWidget(self.label_classificationThreshold, 4, 0, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 6, 0, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 7, 0, 1, 1)

        self.lineEdit_detectionThreshold = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_detectionThreshold.setObjectName(u"lineEdit_detectionThreshold")

        self.gridLayout.addWidget(self.lineEdit_detectionThreshold, 3, 1, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 5, 0, 1, 1)

        self.comboBox_classification_model_version = QComboBox(self.gridLayoutWidget)
        self.comboBox_classification_model_version.setObjectName(u"comboBox_classification_model_version")

        self.gridLayout.addWidget(self.comboBox_classification_model_version, 2, 1, 1, 1)

        self.lineEdit_classificationThreshold = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_classificationThreshold.setObjectName(u"lineEdit_classificationThreshold")

        self.gridLayout.addWidget(self.lineEdit_classificationThreshold, 4, 1, 1, 1)

        self.comboBox_class_dev = QComboBox(self.gridLayoutWidget)
        self.comboBox_class_dev.setObjectName(u"comboBox_class_dev")

        self.gridLayout.addWidget(self.comboBox_class_dev, 7, 1, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 8, 0, 1, 1)

        self.lineEdit_video_fps = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_video_fps.setObjectName(u"lineEdit_video_fps")

        self.gridLayout.addWidget(self.lineEdit_video_fps, 8, 1, 1, 1)

        self.comboBox_detection_dev = QComboBox(self.gridLayoutWidget)
        self.comboBox_detection_dev.setObjectName(u"comboBox_detection_dev")

        self.gridLayout.addWidget(self.comboBox_detection_dev, 6, 1, 1, 1)

        self.comboBox_detection_model_version = QComboBox(self.gridLayoutWidget)
        self.comboBox_detection_model_version.setObjectName(u"comboBox_detection_model_version")

        self.gridLayout.addWidget(self.comboBox_detection_model_version, 1, 1, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)

        self.label_detectionThreshold = QLabel(self.gridLayoutWidget)
        self.label_detectionThreshold.setObjectName(u"label_detectionThreshold")

        self.gridLayout.addWidget(self.label_detectionThreshold, 3, 0, 1, 1)

        self.comboBox_class_lang = QComboBox(self.gridLayoutWidget)
        self.comboBox_class_lang.setObjectName(u"comboBox_class_lang")

        self.gridLayout.addWidget(self.comboBox_class_lang, 5, 1, 1, 1)

        self.label_errorMEssage = QLabel(self.gridLayoutWidget)
        self.label_errorMEssage.setObjectName(u"label_errorMEssage")

        self.gridLayout.addWidget(self.label_errorMEssage, 9, 0, 1, 2)

        self.pushButton_download_models = QPushButton(self.gridLayoutWidget)
        self.pushButton_download_models.setObjectName(u"pushButton_download_models")

        self.gridLayout.addWidget(self.pushButton_download_models, 0, 1, 1, 1)

        self.label_7 = QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)


        self.retranslateUi(DialogConfigureAi)
        self.buttonBox.accepted.connect(DialogConfigureAi.accept)
        self.buttonBox.rejected.connect(DialogConfigureAi.reject)

        QMetaObject.connectSlotsByName(DialogConfigureAi)
    # setupUi

    def retranslateUi(self, DialogConfigureAi):
        DialogConfigureAi.setWindowTitle(QCoreApplication.translate("DialogConfigureAi", u"Configure Ai model", None))
#if QT_CONFIG(tooltip)
        self.label_classificationThreshold.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Min classification probability to trigger notification.", None))
#endif // QT_CONFIG(tooltip)
        self.label_classificationThreshold.setText(QCoreApplication.translate("DialogConfigureAi", u"Classification accuracy threshold (probability):", None))
#if QT_CONFIG(tooltip)
        self.label_2.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Device on which detection processing will run", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("DialogConfigureAi", u"Ai detection device:", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Device on which classification processing will run", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("DialogConfigureAi", u"Ai classification device:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_detectionThreshold.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Min detection probability to trigger notification.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Language to be applied to classification lables", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("DialogConfigureAi", u"Classification label language:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_classificationThreshold.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Min classification probability to trigger notification.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_4.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Video Frame Per Second to leverage for processing", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("DialogConfigureAi", u"Video FPS:", None))
#if QT_CONFIG(tooltip)
        self.label_6.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Select version of Ai classification model", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("DialogConfigureAi", u"Ai classification model version:", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Select version of Ai detection model", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("DialogConfigureAi", u"Ai detection model version:", None))
#if QT_CONFIG(tooltip)
        self.label_detectionThreshold.setToolTip(QCoreApplication.translate("DialogConfigureAi", u"Min detection probability to trigger notification.", None))
#endif // QT_CONFIG(tooltip)
        self.label_detectionThreshold.setText(QCoreApplication.translate("DialogConfigureAi", u"Detection accuracy threshold (probability):", None))
        self.label_errorMEssage.setText("")
        self.pushButton_download_models.setText(QCoreApplication.translate("DialogConfigureAi", u"Download Ai models", None))
        self.label_7.setText(QCoreApplication.translate("DialogConfigureAi", u"Check for new models release:", None))
    # retranslateUi


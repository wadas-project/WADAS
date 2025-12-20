# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_privacy.ui'
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
    QDialogButtonBox, QGridLayout, QGroupBox, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_DialogConfigurePrivacy(object):
    def setupUi(self, DialogConfigurePrivacy):
        if not DialogConfigurePrivacy.objectName():
            DialogConfigurePrivacy.setObjectName(u"DialogConfigurePrivacy")
        DialogConfigurePrivacy.resize(446, 302)
        self.gridLayout = QGridLayout(DialogConfigurePrivacy)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_classification = QGroupBox(DialogConfigurePrivacy)
        self.groupBox_classification.setObjectName(u"groupBox_classification")
        self.verticalLayout = QVBoxLayout(self.groupBox_classification)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.checkBox_remove_original_image = QCheckBox(self.groupBox_classification)
        self.checkBox_remove_original_image.setObjectName(u"checkBox_remove_original_image")

        self.verticalLayout.addWidget(self.checkBox_remove_original_image)

        self.checkBox_remove_detection_image = QCheckBox(self.groupBox_classification)
        self.checkBox_remove_detection_image.setObjectName(u"checkBox_remove_detection_image")

        self.verticalLayout.addWidget(self.checkBox_remove_detection_image)

        self.groupBox_custom_classification = QGroupBox(self.groupBox_classification)
        self.groupBox_custom_classification.setObjectName(u"groupBox_custom_classification")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_custom_classification)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBox_remove_classification_image = QCheckBox(self.groupBox_custom_classification)
        self.checkBox_remove_classification_image.setObjectName(u"checkBox_remove_classification_image")

        self.verticalLayout_2.addWidget(self.checkBox_remove_classification_image)


        self.verticalLayout.addWidget(self.groupBox_custom_classification)


        self.gridLayout.addWidget(self.groupBox_classification, 2, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(DialogConfigurePrivacy)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 1)

        self.label_2 = QLabel(DialogConfigurePrivacy)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)

        self.label = QLabel(DialogConfigurePrivacy)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.groupBox_blur = QGroupBox(DialogConfigurePrivacy)
        self.groupBox_blur.setObjectName(u"groupBox_blur")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_blur)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.checkBox_blur_non_animals = QCheckBox(self.groupBox_blur)
        self.checkBox_blur_non_animals.setObjectName(u"checkBox_blur_non_animals")

        self.verticalLayout_3.addWidget(self.checkBox_blur_non_animals)


        self.gridLayout.addWidget(self.groupBox_blur, 1, 0, 1, 1)


        self.retranslateUi(DialogConfigurePrivacy)
        self.buttonBox.accepted.connect(DialogConfigurePrivacy.accept)
        self.buttonBox.rejected.connect(DialogConfigurePrivacy.reject)

        QMetaObject.connectSlotsByName(DialogConfigurePrivacy)
    # setupUi

    def retranslateUi(self, DialogConfigurePrivacy):
        DialogConfigurePrivacy.setWindowTitle(QCoreApplication.translate("DialogConfigurePrivacy", u"Configure privacy", None))
        self.groupBox_classification.setTitle(QCoreApplication.translate("DialogConfigurePrivacy", u"Classification mode", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_original_image.setToolTip(QCoreApplication.translate("DialogConfigurePrivacy", u"If classification phase will not identify an animal, the original image received by wadas will be deleted.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_original_image.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Remove original image if no animal is classified.", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_detection_image.setToolTip(QCoreApplication.translate("DialogConfigurePrivacy", u"If classification phase will not recognize a species (or classification results below treshold, the detection image will be deteded.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_detection_image.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Remove detection image if no animal is classified.", None))
        self.groupBox_custom_classification.setTitle(QCoreApplication.translate("DialogConfigurePrivacy", u"Custom classification mode", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_classification_image.setToolTip(QCoreApplication.translate("DialogConfigurePrivacy", u"When in custom classification mode, the enablement of this option will triggere deletion of original and processed images if selected custom species is not classified.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_classification_image.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Remove classification image if selected species is not classified.", None))
        self.label_2.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"NOTE: WADAS always automatically deletes images where no animal is detected.", None))
        self.label.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Privacy enforcement options:", None))
        self.groupBox_blur.setTitle(QCoreApplication.translate("DialogConfigurePrivacy", u"Blur non-animals", None))
#if QT_CONFIG(tooltip)
        self.checkBox_blur_non_animals.setToolTip(QCoreApplication.translate("DialogConfigurePrivacy", u"<html><head/><body><p>Blur humans and cars when identified by IA model within the received pictures.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_blur_non_animals.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Blur humans and cars", None))
    # retranslateUi


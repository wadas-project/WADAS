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
    QDialogButtonBox, QGridLayout, QLabel, QSizePolicy,
    QWidget)

class Ui_DialogConfigurePrivacy(object):
    def setupUi(self, DialogConfigurePrivacy):
        if not DialogConfigurePrivacy.objectName():
            DialogConfigurePrivacy.setObjectName(u"DialogConfigurePrivacy")
        DialogConfigurePrivacy.resize(399, 142)
        self.gridLayout = QGridLayout(DialogConfigurePrivacy)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(DialogConfigurePrivacy)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.checkBox_remove_detection_image = QCheckBox(DialogConfigurePrivacy)
        self.checkBox_remove_detection_image.setObjectName(u"checkBox_remove_detection_image")

        self.gridLayout.addWidget(self.checkBox_remove_detection_image, 2, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(DialogConfigurePrivacy)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)

        self.checkBox_remove_original_image = QCheckBox(DialogConfigurePrivacy)
        self.checkBox_remove_original_image.setObjectName(u"checkBox_remove_original_image")

        self.gridLayout.addWidget(self.checkBox_remove_original_image, 1, 0, 1, 1)

        self.checkBox_remove_classification_image = QCheckBox(DialogConfigurePrivacy)
        self.checkBox_remove_classification_image.setObjectName(u"checkBox_remove_classification_image")

        self.gridLayout.addWidget(self.checkBox_remove_classification_image, 3, 0, 1, 1)


        self.retranslateUi(DialogConfigurePrivacy)
        self.buttonBox.accepted.connect(DialogConfigurePrivacy.accept)
        self.buttonBox.rejected.connect(DialogConfigurePrivacy.reject)

        QMetaObject.connectSlotsByName(DialogConfigurePrivacy)
    # setupUi

    def retranslateUi(self, DialogConfigurePrivacy):
        DialogConfigurePrivacy.setWindowTitle(QCoreApplication.translate("DialogConfigurePrivacy", u"Configure privacy", None))
        self.label.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Privacy enforcement options:", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_detection_image.setToolTip(QCoreApplication.translate("DialogConfigurePrivacy", u"If classification phase will not recognize a species (or classification results below treshold, the detection image will be deteded.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_detection_image.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Remove detection image if no animal is classified.", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_original_image.setToolTip(QCoreApplication.translate("DialogConfigurePrivacy", u"If classification phase will not identify an animal, the original image received by wadas will be deleted.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_original_image.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Remove original image if no animal is classified.", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_classification_image.setToolTip(QCoreApplication.translate("DialogConfigurePrivacy", u"When in custom classification mode a given species triggers actuation and notifiactions. With this option enabled, classification image will not be shown unless selected species is classified.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_classification_image.setText(QCoreApplication.translate("DialogConfigurePrivacy", u"Remove classification image if selected species is not classified.", None))
    # retranslateUi


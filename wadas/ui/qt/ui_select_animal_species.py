# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_animal_species.ui'
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
    QDialogButtonBox, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_DialogSelectAnimalSpecies(object):
    def setupUi(self, DialogSelectAnimalSpecies):
        if not DialogSelectAnimalSpecies.objectName():
            DialogSelectAnimalSpecies.setObjectName(u"DialogSelectAnimalSpecies")
        DialogSelectAnimalSpecies.resize(318, 113)
        self.buttonBox = QDialogButtonBox(DialogSelectAnimalSpecies)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 80, 301, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.verticalLayoutWidget = QWidget(DialogSelectAnimalSpecies)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 301, 61))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.comboBox_select_species = QComboBox(self.verticalLayoutWidget)
        self.comboBox_select_species.setObjectName(u"comboBox_select_species")

        self.verticalLayout_2.addWidget(self.comboBox_select_species)


        self.retranslateUi(DialogSelectAnimalSpecies)
        self.buttonBox.accepted.connect(DialogSelectAnimalSpecies.accept)
        self.buttonBox.rejected.connect(DialogSelectAnimalSpecies.reject)

        QMetaObject.connectSlotsByName(DialogSelectAnimalSpecies)
    # setupUi

    def retranslateUi(self, DialogSelectAnimalSpecies):
        DialogSelectAnimalSpecies.setWindowTitle(QCoreApplication.translate("DialogSelectAnimalSpecies", u"Select animal species", None))
        self.label.setText(QCoreApplication.translate("DialogSelectAnimalSpecies", u"Select animal species to classify:", None))
    # retranslateUi


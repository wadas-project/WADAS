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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGroupBox, QSizePolicy, QVBoxLayout, QWidget)

class Ui_DialogSelectAnimalSpecies(object):
    def setupUi(self, DialogSelectAnimalSpecies):
        if not DialogSelectAnimalSpecies.objectName():
            DialogSelectAnimalSpecies.setObjectName(u"DialogSelectAnimalSpecies")
        DialogSelectAnimalSpecies.resize(318, 258)
        self.verticalLayout = QVBoxLayout(DialogSelectAnimalSpecies)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_select_animal_species = QGroupBox(DialogSelectAnimalSpecies)
        self.groupBox_select_animal_species.setObjectName(u"groupBox_select_animal_species")

        self.verticalLayout.addWidget(self.groupBox_select_animal_species)

        self.buttonBox = QDialogButtonBox(DialogSelectAnimalSpecies)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DialogSelectAnimalSpecies)
        self.buttonBox.accepted.connect(DialogSelectAnimalSpecies.accept)
        self.buttonBox.rejected.connect(DialogSelectAnimalSpecies.reject)

        QMetaObject.connectSlotsByName(DialogSelectAnimalSpecies)
    # setupUi

    def retranslateUi(self, DialogSelectAnimalSpecies):
        DialogSelectAnimalSpecies.setWindowTitle(QCoreApplication.translate("DialogSelectAnimalSpecies", u"Select animal species", None))
        self.groupBox_select_animal_species.setTitle(QCoreApplication.translate("DialogSelectAnimalSpecies", u"Select animal species:", None))
    # retranslateUi


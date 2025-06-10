# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_mode.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QButtonGroup, QComboBox,
    QDialog, QDialogButtonBox, QGridLayout, QRadioButton,
    QSizePolicy, QWidget)

class Ui_DialogSelectMode(object):
    def setupUi(self, DialogSelectMode):
        if not DialogSelectMode.objectName():
            DialogSelectMode.setObjectName(u"DialogSelectMode")
        DialogSelectMode.resize(431, 251)
        self.buttonBox = QDialogButtonBox(DialogSelectMode)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 210, 411, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.verticalLayoutWidget = QWidget(DialogSelectMode)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 20, 411, 181))
        self.gridLayout = QGridLayout(self.verticalLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.radioButton_animal_det_mode = QRadioButton(self.verticalLayoutWidget)
        self.buttonGroup = QButtonGroup(DialogSelectMode)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButton_animal_det_mode)
        self.radioButton_animal_det_mode.setObjectName(u"radioButton_animal_det_mode")
        self.radioButton_animal_det_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_animal_det_mode, 1, 0, 1, 1)

        self.radioButton_test_model_mode = QRadioButton(self.verticalLayoutWidget)
        self.buttonGroup.addButton(self.radioButton_test_model_mode)
        self.radioButton_test_model_mode.setObjectName(u"radioButton_test_model_mode")
        self.radioButton_test_model_mode.setChecked(True)
        self.radioButton_test_model_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_test_model_mode, 0, 0, 1, 1)

        self.radioButton_animal_det_and_class_mode = QRadioButton(self.verticalLayoutWidget)
        self.buttonGroup.addButton(self.radioButton_animal_det_and_class_mode)
        self.radioButton_animal_det_and_class_mode.setObjectName(u"radioButton_animal_det_and_class_mode")
        self.radioButton_animal_det_and_class_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_animal_det_and_class_mode, 2, 0, 1, 1)

        self.radioButton_bear_det_mode = QRadioButton(self.verticalLayoutWidget)
        self.buttonGroup.addButton(self.radioButton_bear_det_mode)
        self.radioButton_bear_det_mode.setObjectName(u"radioButton_bear_det_mode")
        self.radioButton_bear_det_mode.setEnabled(True)
        self.radioButton_bear_det_mode.setCheckable(True)
        self.radioButton_bear_det_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_bear_det_mode, 4, 0, 1, 1)

        self.comboBox_select_species = QComboBox(self.verticalLayoutWidget)
        self.comboBox_select_species.setObjectName(u"comboBox_select_species")

        self.gridLayout.addWidget(self.comboBox_select_species, 5, 1, 1, 1)

        self.radioButton_tunnel_mode = QRadioButton(self.verticalLayoutWidget)
        self.buttonGroup.addButton(self.radioButton_tunnel_mode)
        self.radioButton_tunnel_mode.setObjectName(u"radioButton_tunnel_mode")
        self.radioButton_tunnel_mode.setEnabled(False)
        self.radioButton_tunnel_mode.setCheckable(False)
        self.radioButton_tunnel_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_tunnel_mode, 3, 0, 1, 1)

        self.radioButton_custom_species_class_mode = QRadioButton(self.verticalLayoutWidget)
        self.buttonGroup.addButton(self.radioButton_custom_species_class_mode)
        self.radioButton_custom_species_class_mode.setObjectName(u"radioButton_custom_species_class_mode")

        self.gridLayout.addWidget(self.radioButton_custom_species_class_mode, 5, 0, 1, 1)


        self.retranslateUi(DialogSelectMode)
        self.buttonBox.accepted.connect(DialogSelectMode.accept)
        self.buttonBox.rejected.connect(DialogSelectMode.reject)

        QMetaObject.connectSlotsByName(DialogSelectMode)
    # setupUi

    def retranslateUi(self, DialogSelectMode):
        DialogSelectMode.setWindowTitle(QCoreApplication.translate("DialogSelectMode", u"Select operation mode", None))
        self.radioButton_animal_det_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Animal detection mode", None))
        self.radioButton_test_model_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Test model mode", None))
        self.radioButton_animal_det_and_class_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Animal detection and classification mode", None))
        self.radioButton_bear_det_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Bear detection mode", None))
        self.radioButton_tunnel_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Tunnel mode", None))
        self.radioButton_custom_species_class_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Custom species classification mode", None))
    # retranslateUi


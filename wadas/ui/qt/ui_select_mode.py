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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QButtonGroup, QDialog,
    QDialogButtonBox, QGridLayout, QLabel, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QWidget)

class Ui_DialogSelectMode(object):
    def setupUi(self, DialogSelectMode):
        if not DialogSelectMode.objectName():
            DialogSelectMode.setObjectName(u"DialogSelectMode")
        DialogSelectMode.resize(431, 231)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DialogSelectMode.sizePolicy().hasHeightForWidth())
        DialogSelectMode.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(DialogSelectMode)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_select_species = QPushButton(DialogSelectMode)
        self.pushButton_select_species.setObjectName(u"pushButton_select_species")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_select_species.sizePolicy().hasHeightForWidth())
        self.pushButton_select_species.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.pushButton_select_species, 5, 2, 1, 1)

        self.label_custom_species = QLabel(DialogSelectMode)
        self.label_custom_species.setObjectName(u"label_custom_species")
        self.label_custom_species.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_custom_species.sizePolicy().hasHeightForWidth())
        self.label_custom_species.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_custom_species, 6, 1, 1, 2)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 6, 0, 1, 1)

        self.radioButton_custom_species_class_mode = QRadioButton(DialogSelectMode)
        self.buttonGroup = QButtonGroup(DialogSelectMode)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButton_custom_species_class_mode)
        self.radioButton_custom_species_class_mode.setObjectName(u"radioButton_custom_species_class_mode")

        self.gridLayout.addWidget(self.radioButton_custom_species_class_mode, 5, 0, 1, 2)

        self.radioButton_bear_det_mode = QRadioButton(DialogSelectMode)
        self.buttonGroup.addButton(self.radioButton_bear_det_mode)
        self.radioButton_bear_det_mode.setObjectName(u"radioButton_bear_det_mode")
        self.radioButton_bear_det_mode.setEnabled(True)
        self.radioButton_bear_det_mode.setCheckable(True)
        self.radioButton_bear_det_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_bear_det_mode, 4, 0, 1, 2)

        self.radioButton_tunnel_mode = QRadioButton(DialogSelectMode)
        self.buttonGroup.addButton(self.radioButton_tunnel_mode)
        self.radioButton_tunnel_mode.setObjectName(u"radioButton_tunnel_mode")
        self.radioButton_tunnel_mode.setEnabled(True)
        self.radioButton_tunnel_mode.setCheckable(True)
        self.radioButton_tunnel_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_tunnel_mode, 3, 0, 1, 2)

        self.radioButton_animal_det_and_class_mode = QRadioButton(DialogSelectMode)
        self.buttonGroup.addButton(self.radioButton_animal_det_and_class_mode)
        self.radioButton_animal_det_and_class_mode.setObjectName(u"radioButton_animal_det_and_class_mode")
        self.radioButton_animal_det_and_class_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_animal_det_and_class_mode, 2, 0, 1, 2)

        self.radioButton_animal_det_mode = QRadioButton(DialogSelectMode)
        self.buttonGroup.addButton(self.radioButton_animal_det_mode)
        self.radioButton_animal_det_mode.setObjectName(u"radioButton_animal_det_mode")
        self.radioButton_animal_det_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_animal_det_mode, 1, 0, 1, 2)

        self.radioButton_test_model_mode = QRadioButton(DialogSelectMode)
        self.buttonGroup.addButton(self.radioButton_test_model_mode)
        self.radioButton_test_model_mode.setObjectName(u"radioButton_test_model_mode")
        self.radioButton_test_model_mode.setChecked(True)
        self.radioButton_test_model_mode.setAutoExclusive(True)

        self.gridLayout.addWidget(self.radioButton_test_model_mode, 0, 0, 1, 2)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(DialogSelectMode)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi(DialogSelectMode)
        self.buttonBox.accepted.connect(DialogSelectMode.accept)
        self.buttonBox.rejected.connect(DialogSelectMode.reject)

        QMetaObject.connectSlotsByName(DialogSelectMode)
    # setupUi

    def retranslateUi(self, DialogSelectMode):
        DialogSelectMode.setWindowTitle(QCoreApplication.translate("DialogSelectMode", u"Select operation mode", None))
        self.pushButton_select_species.setText(QCoreApplication.translate("DialogSelectMode", u"Select species", None))
        self.label_custom_species.setText("")
        self.radioButton_custom_species_class_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Custom species classification mode", None))
        self.radioButton_bear_det_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Bear detection mode", None))
        self.radioButton_tunnel_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Tunnel mode", None))
        self.radioButton_animal_det_and_class_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Animal detection and classification mode", None))
        self.radioButton_animal_det_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Animal detection mode", None))
        self.radioButton_test_model_mode.setText(QCoreApplication.translate("DialogSelectMode", u"Test model mode", None))
    # retranslateUi


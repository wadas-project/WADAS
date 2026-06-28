# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_notification_areas.ui'
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
    QDialogButtonBox, QGridLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QWidget)

class Ui_ConfigureNotificationAreasDialog(object):
    def setupUi(self, ConfigureNotificationAreasDialog):
        if not ConfigureNotificationAreasDialog.objectName():
            ConfigureNotificationAreasDialog.setObjectName(u"ConfigureNotificationAreasDialog")
        ConfigureNotificationAreasDialog.resize(793, 421)
        self.gridLayout = QGridLayout(ConfigureNotificationAreasDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_add_area = QPushButton(ConfigureNotificationAreasDialog)
        self.pushButton_add_area.setObjectName(u"pushButton_add_area")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_add_area.sizePolicy().hasHeightForWidth())
        self.pushButton_add_area.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.pushButton_add_area, 1, 2, 1, 1)

        self.scrollArea_3 = QScrollArea(ConfigureNotificationAreasDialog)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_contacts = QWidget()
        self.scrollAreaWidgetContents_contacts.setObjectName(u"scrollAreaWidgetContents_contacts")
        self.scrollAreaWidgetContents_contacts.setGeometry(QRect(0, 0, 284, 297))
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_contacts)

        self.gridLayout.addWidget(self.scrollArea_3, 2, 4, 5, 1)

        self.buttonBox = QDialogButtonBox(ConfigureNotificationAreasDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 5)

        self.comboBox_select_notification_method = QComboBox(ConfigureNotificationAreasDialog)
        self.comboBox_select_notification_method.setObjectName(u"comboBox_select_notification_method")

        self.gridLayout.addWidget(self.comboBox_select_notification_method, 1, 4, 1, 1)

        self.label_errorMessage = QLabel(ConfigureNotificationAreasDialog)
        self.label_errorMessage.setObjectName(u"label_errorMessage")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_errorMessage.sizePolicy().hasHeightForWidth())
        self.label_errorMessage.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label_errorMessage, 8, 0, 1, 5)

        self.label_4 = QLabel(ConfigureNotificationAreasDialog)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 4, 1, 1)

        self.label_2 = QLabel(ConfigureNotificationAreasDialog)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_3 = QLabel(ConfigureNotificationAreasDialog)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 3, 1, 1)

        self.pushButton_remove_area = QPushButton(ConfigureNotificationAreasDialog)
        self.pushButton_remove_area.setObjectName(u"pushButton_remove_area")
        sizePolicy.setHeightForWidth(self.pushButton_remove_area.sizePolicy().hasHeightForWidth())
        self.pushButton_remove_area.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.pushButton_remove_area, 2, 2, 1, 1)

        self.scrollArea = QScrollArea(ConfigureNotificationAreasDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_notification_areas = QWidget()
        self.scrollAreaWidgetContents_notification_areas.setObjectName(u"scrollAreaWidgetContents_notification_areas")
        self.scrollAreaWidgetContents_notification_areas.setGeometry(QRect(0, 0, 108, 327))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_notification_areas)

        self.gridLayout.addWidget(self.scrollArea, 1, 0, 6, 2)

        self.scrollArea_2 = QScrollArea(ConfigureNotificationAreasDialog)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_cameras = QWidget()
        self.scrollAreaWidgetContents_cameras.setObjectName(u"scrollAreaWidgetContents_cameras")
        self.scrollAreaWidgetContents_cameras.setGeometry(QRect(0, 0, 284, 327))
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_cameras)

        self.gridLayout.addWidget(self.scrollArea_2, 1, 3, 6, 1)


        self.retranslateUi(ConfigureNotificationAreasDialog)
        self.buttonBox.accepted.connect(ConfigureNotificationAreasDialog.accept)
        self.buttonBox.rejected.connect(ConfigureNotificationAreasDialog.reject)

        QMetaObject.connectSlotsByName(ConfigureNotificationAreasDialog)
    # setupUi

    def retranslateUi(self, ConfigureNotificationAreasDialog):
        ConfigureNotificationAreasDialog.setWindowTitle(QCoreApplication.translate("ConfigureNotificationAreasDialog", u"Configure notification area(s)", None))
        self.pushButton_add_area.setText(QCoreApplication.translate("ConfigureNotificationAreasDialog", u"+", None))
        self.label_errorMessage.setText("")
        self.label_4.setText(QCoreApplication.translate("ConfigureNotificationAreasDialog", u"Notification contact(s)", None))
        self.label_2.setText(QCoreApplication.translate("ConfigureNotificationAreasDialog", u"Notification area(s):", None))
        self.label_3.setText(QCoreApplication.translate("ConfigureNotificationAreasDialog", u"Camera(s):", None))
        self.pushButton_remove_area.setText(QCoreApplication.translate("ConfigureNotificationAreasDialog", u"-", None))
    # retranslateUi


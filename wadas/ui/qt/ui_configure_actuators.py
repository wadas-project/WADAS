# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_actuators.ui'
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
    QGridLayout, QGroupBox, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_DialogConfigureActuators(object):
    def setupUi(self, DialogConfigureActuators):
        if not DialogConfigureActuators.objectName():
            DialogConfigureActuators.setObjectName(u"DialogConfigureActuators")
        DialogConfigureActuators.resize(640, 480)
        self.buttonBox = QDialogButtonBox(DialogConfigureActuators)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 440, 621, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.gridLayoutWidget = QWidget(DialogConfigureActuators)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 621, 421))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.gridLayoutWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_actuator_list = QWidget()
        self.tab_actuator_list.setObjectName(u"tab_actuator_list")
        self.pushButton_add_actuator = QPushButton(self.tab_actuator_list)
        self.pushButton_add_actuator.setObjectName(u"pushButton_add_actuator")
        self.pushButton_add_actuator.setGeometry(QRect(10, 340, 101, 24))
        self.pushButton_remove_actuator = QPushButton(self.tab_actuator_list)
        self.pushButton_remove_actuator.setObjectName(u"pushButton_remove_actuator")
        self.pushButton_remove_actuator.setGeometry(QRect(120, 340, 111, 24))
        self.verticalLayoutWidget = QWidget(self.tab_actuator_list)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 10, 611, 321))
        self.verticalLayout_actuators = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_actuators.setObjectName(u"verticalLayout_actuators")
        self.verticalLayout_actuators.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_actuator_list, "")
        self.tab_actuator = QWidget()
        self.tab_actuator.setObjectName(u"tab_actuator")
        self.gridLayoutWidget_4 = QWidget(self.tab_actuator)
        self.gridLayoutWidget_4.setObjectName(u"gridLayoutWidget_4")
        self.gridLayoutWidget_4.setGeometry(QRect(0, 10, 611, 351))
        self.gridLayout_4 = QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_actuator_timeout = QLineEdit(self.gridLayoutWidget_4)
        self.lineEdit_actuator_timeout.setObjectName(u"lineEdit_actuator_timeout")

        self.gridLayout_4.addWidget(self.lineEdit_actuator_timeout, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget_4)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)

        self.tabWidget.addTab(self.tab_actuator, "")
        self.tab_server = QWidget()
        self.tab_server.setObjectName(u"tab_server")
        self.groupBox = QGroupBox(self.tab_server)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(0, 10, 601, 80))
        self.gridLayoutWidget_2 = QWidget(self.groupBox)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(9, 10, 591, 71))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.gridLayoutWidget_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.lineEdit_server_port = QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_server_port.setObjectName(u"lineEdit_server_port")

        self.gridLayout_2.addWidget(self.lineEdit_server_port, 1, 1, 1, 1)

        self.label = QLabel(self.gridLayoutWidget_2)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QSize(100, 0))

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.lineEdit_server_ip = QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_server_ip.setObjectName(u"lineEdit_server_ip")

        self.gridLayout_2.addWidget(self.lineEdit_server_ip, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.groupBox_2 = QGroupBox(self.tab_server)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(0, 100, 601, 80))
        self.gridLayoutWidget_3 = QWidget(self.groupBox_2)
        self.gridLayoutWidget_3.setObjectName(u"gridLayoutWidget_3")
        self.gridLayoutWidget_3.setGeometry(QRect(10, 10, 581, 71))
        self.gridLayout_3 = QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.gridLayoutWidget_3)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 1, 0, 1, 1)

        self.label_key_file = QLabel(self.gridLayoutWidget_3)
        self.label_key_file.setObjectName(u"label_key_file")

        self.gridLayout_3.addWidget(self.label_key_file, 0, 1, 1, 1)

        self.label_cert_file = QLabel(self.gridLayoutWidget_3)
        self.label_cert_file.setObjectName(u"label_cert_file")

        self.gridLayout_3.addWidget(self.label_cert_file, 1, 1, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget_3)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMinimumSize(QSize(100, 0))

        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)

        self.pushButton_key_file = QPushButton(self.gridLayoutWidget_3)
        self.pushButton_key_file.setObjectName(u"pushButton_key_file")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_key_file.sizePolicy().hasHeightForWidth())
        self.pushButton_key_file.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.pushButton_key_file, 0, 2, 1, 1)

        self.pushButton_cert_file = QPushButton(self.gridLayoutWidget_3)
        self.pushButton_cert_file.setObjectName(u"pushButton_cert_file")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pushButton_cert_file.sizePolicy().hasHeightForWidth())
        self.pushButton_cert_file.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.pushButton_cert_file, 1, 2, 1, 1)

        self.groupBox_3 = QGroupBox(self.tab_server)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(0, 190, 601, 171))
        self.plainTextEdit_test_server_log = QPlainTextEdit(self.groupBox_3)
        self.plainTextEdit_test_server_log.setObjectName(u"plainTextEdit_test_server_log")
        self.plainTextEdit_test_server_log.setGeometry(QRect(10, 70, 581, 81))
        self.pushButton_start_server = QPushButton(self.groupBox_3)
        self.pushButton_start_server.setObjectName(u"pushButton_start_server")
        self.pushButton_start_server.setGeometry(QRect(10, 40, 281, 24))
        self.pushButton_stop_server = QPushButton(self.groupBox_3)
        self.pushButton_stop_server.setObjectName(u"pushButton_stop_server")
        self.pushButton_stop_server.setGeometry(QRect(300, 40, 291, 24))
        self.tabWidget.addTab(self.tab_server, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.label_status = QLabel(self.gridLayoutWidget)
        self.label_status.setObjectName(u"label_status")

        self.gridLayout.addWidget(self.label_status, 1, 0, 1, 1)


        self.retranslateUi(DialogConfigureActuators)
        self.buttonBox.accepted.connect(DialogConfigureActuators.accept)
        self.buttonBox.rejected.connect(DialogConfigureActuators.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DialogConfigureActuators)
    # setupUi

    def retranslateUi(self, DialogConfigureActuators):
        DialogConfigureActuators.setWindowTitle(QCoreApplication.translate("DialogConfigureActuators", u"Configure actuators", None))
        self.pushButton_add_actuator.setText(QCoreApplication.translate("DialogConfigureActuators", u"Add actuator", None))
        self.pushButton_remove_actuator.setText(QCoreApplication.translate("DialogConfigureActuators", u"Remove actuator", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_actuator_list), QCoreApplication.translate("DialogConfigureActuators", u"Actuators", None))
#if QT_CONFIG(tooltip)
        self.tab_actuator.setToolTip(QCoreApplication.translate("DialogConfigureActuators", u"Actuator configuration options", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.lineEdit_actuator_timeout.setToolTip(QCoreApplication.translate("DialogConfigureActuators", u"Actuator timeout in seconds", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("DialogConfigureActuators", u"Actuator timeout in seconds", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("DialogConfigureActuators", u"Actuator timeout (s)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_actuator), QCoreApplication.translate("DialogConfigureActuators", u"Actuator", None))
        self.groupBox.setTitle(QCoreApplication.translate("DialogConfigureActuators", u"Server", None))
        self.label_2.setText(QCoreApplication.translate("DialogConfigureActuators", u"Port", None))
        self.label.setText(QCoreApplication.translate("DialogConfigureActuators", u"IP", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("DialogConfigureActuators", u"SSL", None))
        self.label_4.setText(QCoreApplication.translate("DialogConfigureActuators", u"Certificate", None))
        self.label_key_file.setText("")
        self.label_cert_file.setText("")
        self.label_3.setText(QCoreApplication.translate("DialogConfigureActuators", u"Key", None))
        self.pushButton_key_file.setText(QCoreApplication.translate("DialogConfigureActuators", u"Select key file", None))
        self.pushButton_cert_file.setText(QCoreApplication.translate("DialogConfigureActuators", u"Select certificate file", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("DialogConfigureActuators", u"Test Server", None))
        self.pushButton_start_server.setText(QCoreApplication.translate("DialogConfigureActuators", u"Start actuator server", None))
        self.pushButton_stop_server.setText(QCoreApplication.translate("DialogConfigureActuators", u"Stop actuator server", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_server), QCoreApplication.translate("DialogConfigureActuators", u"Server", None))
        self.label_status.setText("")
    # retranslateUi


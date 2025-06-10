# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_db_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QButtonGroup, QCheckBox,
    QDialog, QDialogButtonBox, QFrame, QGridLayout,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QRadioButton, QSizePolicy, QWidget)

class Ui_ConfigureDBDialog(object):
    def setupUi(self, ConfigureDBDialog):
        if not ConfigureDBDialog.objectName():
            ConfigureDBDialog.setObjectName(u"ConfigureDBDialog")
        ConfigureDBDialog.resize(417, 472)
        self.buttonBox = QDialogButtonBox(ConfigureDBDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 440, 401, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.label_error = QLabel(ConfigureDBDialog)
        self.label_error.setObjectName(u"label_error")
        self.label_error.setGeometry(QRect(10, 410, 401, 20))
        self.gridLayoutWidget_2 = QWidget(ConfigureDBDialog)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(10, 10, 401, 381))
        self.gridLayout_mysql = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_mysql.setObjectName(u"gridLayout_mysql")
        self.gridLayout_mysql.setContentsMargins(0, 0, 0, 0)
        self.line = QFrame(self.gridLayoutWidget_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_mysql.addWidget(self.line, 14, 0, 1, 4)

        self.label_5 = QLabel(self.gridLayoutWidget_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_mysql.addWidget(self.label_5, 8, 0, 1, 1)

        self.radioButton_MySQL = QRadioButton(self.gridLayoutWidget_2)
        self.buttonGroup = QButtonGroup(ConfigureDBDialog)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButton_MySQL)
        self.radioButton_MySQL.setObjectName(u"radioButton_MySQL")

        self.gridLayout_mysql.addWidget(self.radioButton_MySQL, 2, 2, 1, 1)

        self.pushButton_test_db = QPushButton(self.gridLayoutWidget_2)
        self.pushButton_test_db.setObjectName(u"pushButton_test_db")

        self.gridLayout_mysql.addWidget(self.pushButton_test_db, 15, 1, 1, 2)

        self.plainTextEdit_db_test = QPlainTextEdit(self.gridLayoutWidget_2)
        self.plainTextEdit_db_test.setObjectName(u"plainTextEdit_db_test")

        self.gridLayout_mysql.addWidget(self.plainTextEdit_db_test, 16, 0, 1, 4)

        self.label_3 = QLabel(self.gridLayoutWidget_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_mysql.addWidget(self.label_3, 9, 0, 1, 1)

        self.lineEdit_db_host = QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_db_host.setObjectName(u"lineEdit_db_host")

        self.gridLayout_mysql.addWidget(self.lineEdit_db_host, 7, 2, 1, 1)

        self.label_host = QLabel(self.gridLayoutWidget_2)
        self.label_host.setObjectName(u"label_host")

        self.gridLayout_mysql.addWidget(self.label_host, 7, 0, 1, 1)

        self.lineEdit_db_password = QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_db_password.setObjectName(u"lineEdit_db_password")
        self.lineEdit_db_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout_mysql.addWidget(self.lineEdit_db_password, 10, 2, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_mysql.addWidget(self.label_4, 10, 0, 1, 1)

        self.radioButton_MariaDB = QRadioButton(self.gridLayoutWidget_2)
        self.buttonGroup.addButton(self.radioButton_MariaDB)
        self.radioButton_MariaDB.setObjectName(u"radioButton_MariaDB")

        self.gridLayout_mysql.addWidget(self.radioButton_MariaDB, 2, 3, 1, 1)

        self.lineEdit_db_username = QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_db_username.setObjectName(u"lineEdit_db_username")

        self.gridLayout_mysql.addWidget(self.lineEdit_db_username, 9, 2, 1, 1)

        self.label = QLabel(self.gridLayoutWidget_2)
        self.label.setObjectName(u"label")

        self.gridLayout_mysql.addWidget(self.label, 11, 0, 1, 1)

        self.checkBox_enable_db = QCheckBox(self.gridLayoutWidget_2)
        self.checkBox_enable_db.setObjectName(u"checkBox_enable_db")

        self.gridLayout_mysql.addWidget(self.checkBox_enable_db, 0, 0, 1, 3)

        self.label_6 = QLabel(self.gridLayoutWidget_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_mysql.addWidget(self.label_6, 12, 0, 1, 1)

        self.lineEdit_db_name = QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_db_name.setObjectName(u"lineEdit_db_name")

        self.gridLayout_mysql.addWidget(self.lineEdit_db_name, 11, 2, 1, 1)

        self.radioButton_SQLite = QRadioButton(self.gridLayoutWidget_2)
        self.buttonGroup.addButton(self.radioButton_SQLite)
        self.radioButton_SQLite.setObjectName(u"radioButton_SQLite")

        self.gridLayout_mysql.addWidget(self.radioButton_SQLite, 2, 0, 1, 1)

        self.label_db_version = QLabel(self.gridLayoutWidget_2)
        self.label_db_version.setObjectName(u"label_db_version")

        self.gridLayout_mysql.addWidget(self.label_db_version, 12, 2, 1, 1)

        self.lineEdit_db_port = QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_db_port.setObjectName(u"lineEdit_db_port")

        self.gridLayout_mysql.addWidget(self.lineEdit_db_port, 8, 2, 1, 1)

        self.line_3 = QFrame(self.gridLayoutWidget_2)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_mysql.addWidget(self.line_3, 6, 0, 1, 4)

        self.line_2 = QFrame(self.gridLayoutWidget_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_mysql.addWidget(self.line_2, 4, 0, 1, 4)

        self.checkBox_new_db = QCheckBox(self.gridLayoutWidget_2)
        self.checkBox_new_db.setObjectName(u"checkBox_new_db")

        self.gridLayout_mysql.addWidget(self.checkBox_new_db, 5, 0, 1, 4)

        self.label_error_2 = QLabel(ConfigureDBDialog)
        self.label_error_2.setObjectName(u"label_error_2")
        self.label_error_2.setGeometry(QRect(10, 390, 401, 20))
        QWidget.setTabOrder(self.checkBox_enable_db, self.radioButton_SQLite)
        QWidget.setTabOrder(self.radioButton_SQLite, self.radioButton_MySQL)
        QWidget.setTabOrder(self.radioButton_MySQL, self.radioButton_MariaDB)
        QWidget.setTabOrder(self.radioButton_MariaDB, self.lineEdit_db_host)
        QWidget.setTabOrder(self.lineEdit_db_host, self.lineEdit_db_port)
        QWidget.setTabOrder(self.lineEdit_db_port, self.lineEdit_db_username)
        QWidget.setTabOrder(self.lineEdit_db_username, self.lineEdit_db_password)
        QWidget.setTabOrder(self.lineEdit_db_password, self.lineEdit_db_name)
        QWidget.setTabOrder(self.lineEdit_db_name, self.pushButton_test_db)
        QWidget.setTabOrder(self.pushButton_test_db, self.plainTextEdit_db_test)

        self.retranslateUi(ConfigureDBDialog)
        self.buttonBox.accepted.connect(ConfigureDBDialog.accept)
        self.buttonBox.rejected.connect(ConfigureDBDialog.reject)

        QMetaObject.connectSlotsByName(ConfigureDBDialog)
    # setupUi

    def retranslateUi(self, ConfigureDBDialog):
        ConfigureDBDialog.setWindowTitle(QCoreApplication.translate("ConfigureDBDialog", u"Configure Database", None))
        self.label_error.setText("")
        self.label_5.setText(QCoreApplication.translate("ConfigureDBDialog", u"Port:", None))
        self.radioButton_MySQL.setText(QCoreApplication.translate("ConfigureDBDialog", u"MySQL", None))
        self.pushButton_test_db.setText(QCoreApplication.translate("ConfigureDBDialog", u"Test database connection", None))
        self.label_3.setText(QCoreApplication.translate("ConfigureDBDialog", u"Username:", None))
        self.label_host.setText(QCoreApplication.translate("ConfigureDBDialog", u"Host:", None))
        self.label_4.setText(QCoreApplication.translate("ConfigureDBDialog", u"Password:", None))
        self.radioButton_MariaDB.setText(QCoreApplication.translate("ConfigureDBDialog", u"MariaDB", None))
        self.label.setText(QCoreApplication.translate("ConfigureDBDialog", u"Database name:", None))
        self.checkBox_enable_db.setText(QCoreApplication.translate("ConfigureDBDialog", u"Enable database", None))
        self.label_6.setText(QCoreApplication.translate("ConfigureDBDialog", u"Version:", None))
        self.radioButton_SQLite.setText(QCoreApplication.translate("ConfigureDBDialog", u"SQLite", None))
        self.label_db_version.setText("")
        self.checkBox_new_db.setText(QCoreApplication.translate("ConfigureDBDialog", u"New database (triggers new db creation)", None))
        self.label_error_2.setText(QCoreApplication.translate("ConfigureDBDialog", u"NOTE: DB enablement will trigger autosave when modifying configuration.", None))
    # retranslateUi


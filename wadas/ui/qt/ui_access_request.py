# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'access_request.ui'
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
    QLineEdit, QPlainTextEdit, QPushButton, QSizePolicy,
    QWidget)

class Ui_DialogModelAccessRequest(object):
    def setupUi(self, DialogModelAccessRequest):
        if not DialogModelAccessRequest.objectName():
            DialogModelAccessRequest.setObjectName(u"DialogModelAccessRequest")
        DialogModelAccessRequest.resize(595, 462)
        self.gridLayout = QGridLayout(DialogModelAccessRequest)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(DialogModelAccessRequest)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 4)

        self.groupBox_login = QGroupBox(DialogModelAccessRequest)
        self.groupBox_login.setObjectName(u"groupBox_login")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_login.sizePolicy().hasHeightForWidth())
        self.groupBox_login.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(self.groupBox_login)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_2 = QLabel(self.groupBox_login)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_3 = QLabel(self.groupBox_login)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.label = QLabel(self.groupBox_login)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.lineEdit_token = QLineEdit(self.groupBox_login)
        self.lineEdit_token.setObjectName(u"lineEdit_token")
        self.lineEdit_token.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout_2.addWidget(self.lineEdit_token, 2, 1, 1, 1)

        self.lineEdit_email = QLineEdit(self.groupBox_login)
        self.lineEdit_email.setObjectName(u"lineEdit_email")

        self.gridLayout_2.addWidget(self.lineEdit_email, 1, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox_login, 0, 0, 1, 4)

        self.groupBox_new_request = QGroupBox(DialogModelAccessRequest)
        self.groupBox_new_request.setObjectName(u"groupBox_new_request")
        sizePolicy.setHeightForWidth(self.groupBox_new_request.sizePolicy().hasHeightForWidth())
        self.groupBox_new_request.setSizePolicy(sizePolicy)
        self.gridLayout_3 = QGridLayout(self.groupBox_new_request)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_status_title = QLabel(self.groupBox_new_request)
        self.label_status_title.setObjectName(u"label_status_title")
        self.label_status_title.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_status_title, 5, 0, 1, 1)

        self.pushButton_check_request = QPushButton(self.groupBox_new_request)
        self.pushButton_check_request.setObjectName(u"pushButton_check_request")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_check_request.sizePolicy().hasHeightForWidth())
        self.pushButton_check_request.setSizePolicy(sizePolicy1)

        self.gridLayout_3.addWidget(self.pushButton_check_request, 5, 2, 1, 1)

        self.label_6 = QLabel(self.groupBox_new_request)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_3.addWidget(self.label_6, 2, 0, 1, 1)

        self.lineEdit_organization = QLineEdit(self.groupBox_new_request)
        self.lineEdit_organization.setObjectName(u"lineEdit_organization")

        self.gridLayout_3.addWidget(self.lineEdit_organization, 1, 1, 1, 2)

        self.label_7 = QLabel(self.groupBox_new_request)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_3.addWidget(self.label_7, 3, 0, 1, 1)

        self.plainTextEdit_rationale = QPlainTextEdit(self.groupBox_new_request)
        self.plainTextEdit_rationale.setObjectName(u"plainTextEdit_rationale")

        self.gridLayout_3.addWidget(self.plainTextEdit_rationale, 3, 1, 1, 2)

        self.lineEdit_node_num = QLineEdit(self.groupBox_new_request)
        self.lineEdit_node_num.setObjectName(u"lineEdit_node_num")

        self.gridLayout_3.addWidget(self.lineEdit_node_num, 2, 1, 1, 2)

        self.lineEdit_name_surname = QLineEdit(self.groupBox_new_request)
        self.lineEdit_name_surname.setObjectName(u"lineEdit_name_surname")

        self.gridLayout_3.addWidget(self.lineEdit_name_surname, 0, 1, 1, 2)

        self.label_9 = QLabel(self.groupBox_new_request)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_3.addWidget(self.label_9, 7, 0, 1, 3)

        self.label_5 = QLabel(self.groupBox_new_request)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox_new_request)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.label_request_status = QLabel(self.groupBox_new_request)
        self.label_request_status.setObjectName(u"label_request_status")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_request_status.sizePolicy().hasHeightForWidth())
        self.label_request_status.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.label_request_status, 5, 1, 1, 1)

        self.label_8 = QLabel(self.groupBox_new_request)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_3.addWidget(self.label_8, 8, 0, 1, 3)


        self.gridLayout.addWidget(self.groupBox_new_request, 5, 0, 1, 4)

        self.checkBox_new_request = QCheckBox(DialogModelAccessRequest)
        self.checkBox_new_request.setObjectName(u"checkBox_new_request")

        self.gridLayout.addWidget(self.checkBox_new_request, 1, 0, 1, 3)

        self.pushButton_clear_request = QPushButton(DialogModelAccessRequest)
        self.pushButton_clear_request.setObjectName(u"pushButton_clear_request")

        self.gridLayout.addWidget(self.pushButton_clear_request, 1, 3, 1, 1)

        self.label_error = QLabel(DialogModelAccessRequest)
        self.label_error.setObjectName(u"label_error")

        self.gridLayout.addWidget(self.label_error, 6, 0, 1, 4)

        QWidget.setTabOrder(self.lineEdit_email, self.lineEdit_token)
        QWidget.setTabOrder(self.lineEdit_token, self.checkBox_new_request)
        QWidget.setTabOrder(self.checkBox_new_request, self.pushButton_clear_request)
        QWidget.setTabOrder(self.pushButton_clear_request, self.lineEdit_name_surname)
        QWidget.setTabOrder(self.lineEdit_name_surname, self.lineEdit_organization)
        QWidget.setTabOrder(self.lineEdit_organization, self.lineEdit_node_num)
        QWidget.setTabOrder(self.lineEdit_node_num, self.plainTextEdit_rationale)
        QWidget.setTabOrder(self.plainTextEdit_rationale, self.pushButton_check_request)

        self.retranslateUi(DialogModelAccessRequest)
        self.buttonBox.accepted.connect(DialogModelAccessRequest.accept)
        self.buttonBox.rejected.connect(DialogModelAccessRequest.reject)

        QMetaObject.connectSlotsByName(DialogModelAccessRequest)
    # setupUi

    def retranslateUi(self, DialogModelAccessRequest):
        DialogModelAccessRequest.setWindowTitle(QCoreApplication.translate("DialogModelAccessRequest", u"Ai models access request", None))
        self.groupBox_login.setTitle(QCoreApplication.translate("DialogModelAccessRequest", u"Login", None))
        self.label_2.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Email:", None))
        self.label_3.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Token:", None))
        self.label.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Insert your credentials to download the AI models:", None))
        self.groupBox_new_request.setTitle(QCoreApplication.translate("DialogModelAccessRequest", u"New model request", None))
        self.label_status_title.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Status of the request:", None))
        self.pushButton_check_request.setText(QCoreApplication.translate("DialogModelAccessRequest", u"check now", None))
        self.label_6.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Number of nodes:", None))
        self.lineEdit_organization.setPlaceholderText(QCoreApplication.translate("DialogModelAccessRequest", u"If you are part of an organization tell us which one", None))
        self.label_7.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Rationale:", None))
        self.plainTextEdit_rationale.setPlaceholderText(QCoreApplication.translate("DialogModelAccessRequest", u"Tell us why you want to use WADAS (E.g., development, wildlife conservation, other)", None))
        self.lineEdit_name_surname.setPlaceholderText("")
        self.label_9.setText(QCoreApplication.translate("DialogModelAccessRequest", u"By submitting AI model access request you have read, understood and accepted the WADAS Term of Use.", None))
        self.label_5.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Organization:", None))
        self.label_4.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Name and Surname:", None))
        self.label_request_status.setText("")
        self.label_8.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Click Ok to submit the request. If you wish to modify a submitted request contact us at info@wadas.it", None))
        self.checkBox_new_request.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Raise new AI modell access request", None))
        self.pushButton_clear_request.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Clear previous request", None))
        self.label_error.setText("")
    # retranslateUi


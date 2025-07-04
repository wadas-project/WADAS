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
    QLineEdit, QPlainTextEdit, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_DialogModelAccessRequest(object):
    def setupUi(self, DialogModelAccessRequest):
        if not DialogModelAccessRequest.objectName():
            DialogModelAccessRequest.setObjectName(u"DialogModelAccessRequest")
        DialogModelAccessRequest.resize(587, 546)
        self.gridLayout = QGridLayout(DialogModelAccessRequest)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_error = QLabel(DialogModelAccessRequest)
        self.label_error.setObjectName(u"label_error")

        self.gridLayout.addWidget(self.label_error, 7, 0, 1, 3)

        self.groupBox = QGroupBox(DialogModelAccessRequest)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.checkBox_terms_of_use = QCheckBox(self.groupBox)
        self.checkBox_terms_of_use.setObjectName(u"checkBox_terms_of_use")

        self.gridLayout_2.addWidget(self.checkBox_terms_of_use, 0, 0, 1, 1)

        self.pushButton_terms_of_use = QPushButton(self.groupBox)
        self.pushButton_terms_of_use.setObjectName(u"pushButton_terms_of_use")

        self.gridLayout_2.addWidget(self.pushButton_terms_of_use, 0, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 5, 0, 1, 3)

        self.groupBox_new_request = QGroupBox(DialogModelAccessRequest)
        self.groupBox_new_request.setObjectName(u"groupBox_new_request")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_new_request.sizePolicy().hasHeightForWidth())
        self.groupBox_new_request.setSizePolicy(sizePolicy)
        self.gridLayout_3 = QGridLayout(self.groupBox_new_request)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.lineEdit_node_num = QLineEdit(self.groupBox_new_request)
        self.lineEdit_node_num.setObjectName(u"lineEdit_node_num")

        self.gridLayout_3.addWidget(self.lineEdit_node_num, 4, 1, 1, 2)

        self.label_6 = QLabel(self.groupBox_new_request)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_3.addWidget(self.label_6, 4, 0, 1, 1)

        self.pushButton_check_request = QPushButton(self.groupBox_new_request)
        self.pushButton_check_request.setObjectName(u"pushButton_check_request")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_check_request.sizePolicy().hasHeightForWidth())
        self.pushButton_check_request.setSizePolicy(sizePolicy1)

        self.gridLayout_3.addWidget(self.pushButton_check_request, 7, 2, 1, 1)

        self.lineEdit_organization = QLineEdit(self.groupBox_new_request)
        self.lineEdit_organization.setObjectName(u"lineEdit_organization")

        self.gridLayout_3.addWidget(self.lineEdit_organization, 3, 1, 1, 2)

        self.lineEdit_name_surname = QLineEdit(self.groupBox_new_request)
        self.lineEdit_name_surname.setObjectName(u"lineEdit_name_surname")

        self.gridLayout_3.addWidget(self.lineEdit_name_surname, 2, 1, 1, 2)

        self.label_5 = QLabel(self.groupBox_new_request)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 3, 0, 1, 1)

        self.plainTextEdit_rationale = QPlainTextEdit(self.groupBox_new_request)
        self.plainTextEdit_rationale.setObjectName(u"plainTextEdit_rationale")

        self.gridLayout_3.addWidget(self.plainTextEdit_rationale, 5, 1, 1, 2)

        self.lineEdit_email = QLineEdit(self.groupBox_new_request)
        self.lineEdit_email.setObjectName(u"lineEdit_email")

        self.gridLayout_3.addWidget(self.lineEdit_email, 0, 1, 1, 2)

        self.label_status_title = QLabel(self.groupBox_new_request)
        self.label_status_title.setObjectName(u"label_status_title")
        self.label_status_title.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_status_title, 7, 0, 1, 1)

        self.label_request_status = QLabel(self.groupBox_new_request)
        self.label_request_status.setObjectName(u"label_request_status")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_request_status.sizePolicy().hasHeightForWidth())
        self.label_request_status.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.label_request_status, 7, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox_new_request)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox_new_request)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 2, 0, 1, 1)

        self.label_7 = QLabel(self.groupBox_new_request)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_3.addWidget(self.label_7, 5, 0, 1, 1)

        self.pushButton_clear_request = QPushButton(self.groupBox_new_request)
        self.pushButton_clear_request.setObjectName(u"pushButton_clear_request")

        self.gridLayout_3.addWidget(self.pushButton_clear_request, 9, 2, 1, 1)

        self.label_clear_request = QLabel(self.groupBox_new_request)
        self.label_clear_request.setObjectName(u"label_clear_request")

        self.gridLayout_3.addWidget(self.label_clear_request, 9, 0, 1, 2)


        self.gridLayout.addWidget(self.groupBox_new_request, 3, 0, 1, 3)

        self.buttonBox = QDialogButtonBox(DialogModelAccessRequest)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 3)

        self.label_8 = QLabel(DialogModelAccessRequest)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 8, 0, 1, 3)

        self.groupBox_gdpr = QGroupBox(DialogModelAccessRequest)
        self.groupBox_gdpr.setObjectName(u"groupBox_gdpr")
        self.gridLayout_4 = QGridLayout(self.groupBox_gdpr)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.checkBox_gdpr = QCheckBox(self.groupBox_gdpr)
        self.checkBox_gdpr.setObjectName(u"checkBox_gdpr")

        self.gridLayout_4.addWidget(self.checkBox_gdpr, 1, 0, 1, 1)

        self.scrollArea = QScrollArea(self.groupBox_gdpr)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 535, 298))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_4.addWidget(self.scrollArea, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox_gdpr, 6, 0, 1, 3)

        QWidget.setTabOrder(self.lineEdit_email, self.lineEdit_name_surname)
        QWidget.setTabOrder(self.lineEdit_name_surname, self.lineEdit_organization)
        QWidget.setTabOrder(self.lineEdit_organization, self.lineEdit_node_num)
        QWidget.setTabOrder(self.lineEdit_node_num, self.plainTextEdit_rationale)
        QWidget.setTabOrder(self.plainTextEdit_rationale, self.pushButton_check_request)
        QWidget.setTabOrder(self.pushButton_check_request, self.pushButton_clear_request)
        QWidget.setTabOrder(self.pushButton_clear_request, self.checkBox_terms_of_use)
        QWidget.setTabOrder(self.checkBox_terms_of_use, self.pushButton_terms_of_use)
        QWidget.setTabOrder(self.pushButton_terms_of_use, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.checkBox_gdpr)

        self.retranslateUi(DialogModelAccessRequest)
        self.buttonBox.accepted.connect(DialogModelAccessRequest.accept)
        self.buttonBox.rejected.connect(DialogModelAccessRequest.reject)

        QMetaObject.connectSlotsByName(DialogModelAccessRequest)
    # setupUi

    def retranslateUi(self, DialogModelAccessRequest):
        DialogModelAccessRequest.setWindowTitle(QCoreApplication.translate("DialogModelAccessRequest", u"Ai models access request", None))
        self.label_error.setText("")
        self.groupBox.setTitle(QCoreApplication.translate("DialogModelAccessRequest", u"Terms of Use and Privacy", None))
        self.checkBox_terms_of_use.setText(QCoreApplication.translate("DialogModelAccessRequest", u"I have read, understood and accepted the WADAS Ai models Terms of Use.", None))
        self.pushButton_terms_of_use.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Terms Of Use", None))
        self.groupBox_new_request.setTitle(QCoreApplication.translate("DialogModelAccessRequest", u"New model request", None))
        self.label_6.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Number of nodes:", None))
        self.pushButton_check_request.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Check status now", None))
        self.lineEdit_organization.setPlaceholderText(QCoreApplication.translate("DialogModelAccessRequest", u"If you are part of an organization tell us which one", None))
        self.lineEdit_name_surname.setPlaceholderText("")
        self.label_5.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Organization:", None))
        self.plainTextEdit_rationale.setPlaceholderText(QCoreApplication.translate("DialogModelAccessRequest", u"Tell us why you want to use WADAS (E.g., development, wildlife conservation, other)", None))
        self.label_status_title.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Status of the request:", None))
        self.label_request_status.setText("")
        self.label_2.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Email:", None))
        self.label_4.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Name and Surname:", None))
        self.label_7.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Rationale:", None))
        self.pushButton_clear_request.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Clear previous request", None))
        self.label_clear_request.setText(QCoreApplication.translate("DialogModelAccessRequest", u"If you want to submit a new request you must clear current one.", None))
        self.label_8.setText(QCoreApplication.translate("DialogModelAccessRequest", u"Click Ok to submit the request. If you wish to modify a submitted request contact us at info@wadas.it", None))
        self.groupBox_gdpr.setTitle(QCoreApplication.translate("DialogModelAccessRequest", u"Privacy", None))
        self.checkBox_gdpr.setText(QCoreApplication.translate("DialogModelAccessRequest", u"I give my consent to use my data for the purposed outlined above.", None))
        self.label.setText(QCoreApplication.translate("DialogModelAccessRequest", u"<html><head/><body><p><span style=\" font-weight:700;\">Privacy Disclaimer for WADAS (GDPR Compliance)</span><br/><br/>In accordance with the General Data Protection Regulation (EU) 2016/679 (GDPR), </p><p>we inform you that the personal data collected through the WADAS application \u2014 </p><p>specifically <span style=\" font-weight:700;\">Name</span>, <span style=\" font-weight:700;\">Surname</span>, <span style=\" font-weight:700;\">Email Address</span>, and <span style=\" font-weight:700;\">Organization</span> \u2014 are collected and</p><p>processed solely for the purpose of <span style=\" font-style:italic;\">identifying and contacting users of the application</span>.<br/><br/>Your data will <span style=\" font-weight:700;\">not be shared with third parties</span> under any circumstances and will be</p><p>treated with the utmost care and confidentiality.<br/><br/>By providing your information, you consent to its use for the purposes outlined above.</p><p>You have the right to access, rectify, or request"
                        " the deletion of your data at any time by</p><p>contacting the WADAS team at info@wadas.it. </p></body></html>", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configure_ftp_cameras.ui'
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

class Ui_DialogFTPCameras(object):
    def setupUi(self, DialogFTPCameras):
        if not DialogFTPCameras.objectName():
            DialogFTPCameras.setObjectName(u"DialogFTPCameras")
        DialogFTPCameras.resize(834, 533)
        self.buttonBox = QDialogButtonBox(DialogFTPCameras)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(430, 480, 371, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.label_errorMessage = QLabel(DialogFTPCameras)
        self.label_errorMessage.setObjectName(u"label_errorMessage")
        self.label_errorMessage.setGeometry(QRect(10, 470, 801, 16))
        self.gridLayoutWidget_5 = QWidget(DialogFTPCameras)
        self.gridLayoutWidget_5.setObjectName(u"gridLayoutWidget_5")
        self.gridLayoutWidget_5.setGeometry(QRect(20, 10, 791, 451))
        self.gridLayout_main = QGridLayout(self.gridLayoutWidget_5)
        self.gridLayout_main.setObjectName(u"gridLayout_main")
        self.gridLayout_main.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.gridLayoutWidget_5)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_FTPcameras = QWidget()
        self.tab_FTPcameras.setObjectName(u"tab_FTPcameras")
        self.pushButton_addFTPCamera = QPushButton(self.tab_FTPcameras)
        self.pushButton_addFTPCamera.setObjectName(u"pushButton_addFTPCamera")
        self.pushButton_addFTPCamera.setGeometry(QRect(10, 390, 131, 24))
        self.pushButton_removeFTPCamera = QPushButton(self.tab_FTPcameras)
        self.pushButton_removeFTPCamera.setObjectName(u"pushButton_removeFTPCamera")
        self.pushButton_removeFTPCamera.setGeometry(QRect(150, 390, 131, 24))
        self.verticalLayoutWidget = QWidget(self.tab_FTPcameras)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 781, 381))
        self.verticalLayout_FTPCameraTab = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_FTPCameraTab.setObjectName(u"verticalLayout_FTPCameraTab")
        self.verticalLayout_FTPCameraTab.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_FTPcameras, "")
        self.tab_FTPServer = QWidget()
        self.tab_FTPServer.setObjectName(u"tab_FTPServer")
        self.gridLayoutWidget_2 = QWidget(self.tab_FTPServer)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(10, 10, 771, 463))
        self.gridLayout = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_FTPServer = QGroupBox(self.gridLayoutWidget_2)
        self.groupBox_FTPServer.setObjectName(u"groupBox_FTPServer")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_FTPServer.sizePolicy().hasHeightForWidth())
        self.groupBox_FTPServer.setSizePolicy(sizePolicy)
        self.groupBox_FTPServer.setMinimumSize(QSize(0, 127))
        self.gridLayoutWidget_4 = QWidget(self.groupBox_FTPServer)
        self.gridLayoutWidget_4.setObjectName(u"gridLayoutWidget_4")
        self.gridLayoutWidget_4.setGeometry(QRect(10, 20, 741, 107))
        self.gridLayout_3 = QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.gridLayoutWidget_4)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget_4)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)

        self.lineEdit_max_conn_ip = QLineEdit(self.gridLayoutWidget_4)
        self.lineEdit_max_conn_ip.setObjectName(u"lineEdit_max_conn_ip")

        self.gridLayout_3.addWidget(self.lineEdit_max_conn_ip, 2, 3, 1, 1)

        self.pushButton_select_FTPserver_folder = QPushButton(self.gridLayoutWidget_4)
        self.pushButton_select_FTPserver_folder.setObjectName(u"pushButton_select_FTPserver_folder")

        self.gridLayout_3.addWidget(self.pushButton_select_FTPserver_folder, 4, 3, 1, 1)

        self.label_10 = QLabel(self.gridLayoutWidget_4)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_3.addWidget(self.label_10, 4, 0, 1, 1)

        self.lineEdit_port = QLineEdit(self.gridLayoutWidget_4)
        self.lineEdit_port.setObjectName(u"lineEdit_port")

        self.gridLayout_3.addWidget(self.lineEdit_port, 0, 3, 1, 1)

        self.label_FTPServer_path = QLabel(self.gridLayoutWidget_4)
        self.label_FTPServer_path.setObjectName(u"label_FTPServer_path")

        self.gridLayout_3.addWidget(self.label_FTPServer_path, 4, 1, 1, 2)

        self.lineEdit_max_conn = QLineEdit(self.gridLayoutWidget_4)
        self.lineEdit_max_conn.setObjectName(u"lineEdit_max_conn")

        self.gridLayout_3.addWidget(self.lineEdit_max_conn, 2, 1, 1, 1)

        self.lineEdit_ip = QLineEdit(self.gridLayoutWidget_4)
        self.lineEdit_ip.setObjectName(u"lineEdit_ip")

        self.gridLayout_3.addWidget(self.lineEdit_ip, 0, 1, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget_4)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_3.addWidget(self.label_6, 2, 2, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget_4)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 0, 2, 1, 1)

        self.label_7 = QLabel(self.gridLayoutWidget_4)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_3.addWidget(self.label_7, 3, 0, 1, 1)

        self.label_8 = QLabel(self.gridLayoutWidget_4)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_3.addWidget(self.label_8, 3, 2, 1, 1)

        self.lineEdit_passive_port_range_start = QLineEdit(self.gridLayoutWidget_4)
        self.lineEdit_passive_port_range_start.setObjectName(u"lineEdit_passive_port_range_start")

        self.gridLayout_3.addWidget(self.lineEdit_passive_port_range_start, 3, 1, 1, 1)

        self.lineEdit_passive_port_range_end = QLineEdit(self.gridLayoutWidget_4)
        self.lineEdit_passive_port_range_end.setObjectName(u"lineEdit_passive_port_range_end")

        self.gridLayout_3.addWidget(self.lineEdit_passive_port_range_end, 3, 3, 1, 1)


        self.gridLayout.addWidget(self.groupBox_FTPServer, 0, 0, 1, 1)

        self.groupBox_SSL = QGroupBox(self.gridLayoutWidget_2)
        self.groupBox_SSL.setObjectName(u"groupBox_SSL")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_SSL.sizePolicy().hasHeightForWidth())
        self.groupBox_SSL.setSizePolicy(sizePolicy1)
        self.groupBox_SSL.setMinimumSize(QSize(0, 40))
        self.groupBox_SSL.setMaximumSize(QSize(16777215, 16777213))
        self.gridLayoutWidget_3 = QWidget(self.groupBox_SSL)
        self.gridLayoutWidget_3.setObjectName(u"gridLayoutWidget_3")
        self.gridLayoutWidget_3.setGeometry(QRect(9, 29, 741, 62))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pushButton_sekectCertificateKey = QPushButton(self.gridLayoutWidget_3)
        self.pushButton_sekectCertificateKey.setObjectName(u"pushButton_sekectCertificateKey")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_sekectCertificateKey.sizePolicy().hasHeightForWidth())
        self.pushButton_sekectCertificateKey.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.pushButton_sekectCertificateKey, 1, 2, 1, 1)

        self.label_key_file_path = QLabel(self.gridLayoutWidget_3)
        self.label_key_file_path.setObjectName(u"label_key_file_path")

        self.gridLayout_2.addWidget(self.label_key_file_path, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.label_certificate_file_path = QLabel(self.gridLayoutWidget_3)
        self.label_certificate_file_path.setObjectName(u"label_certificate_file_path")

        self.gridLayout_2.addWidget(self.label_certificate_file_path, 1, 1, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget_3)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.label = QLabel(self.gridLayoutWidget_3)
        self.label.setObjectName(u"label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.pushButton_selectKeyFile = QPushButton(self.gridLayoutWidget_3)
        self.pushButton_selectKeyFile.setObjectName(u"pushButton_selectKeyFile")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButton_selectKeyFile.sizePolicy().hasHeightForWidth())
        self.pushButton_selectKeyFile.setSizePolicy(sizePolicy4)

        self.gridLayout_2.addWidget(self.pushButton_selectKeyFile, 0, 2, 1, 1)


        self.gridLayout.addWidget(self.groupBox_SSL, 1, 0, 1, 1)

        self.groupBox_TestFTPServer = QGroupBox(self.gridLayoutWidget_2)
        self.groupBox_TestFTPServer.setObjectName(u"groupBox_TestFTPServer")
        self.groupBox_TestFTPServer.setMinimumSize(QSize(0, 190))
        self.gridLayoutWidget_6 = QWidget(self.groupBox_TestFTPServer)
        self.gridLayoutWidget_6.setObjectName(u"gridLayoutWidget_6")
        self.gridLayoutWidget_6.setGeometry(QRect(10, 20, 751, 111))
        self.gridLayout_4 = QGridLayout(self.gridLayoutWidget_6)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.pushButton_testFTPServer = QPushButton(self.gridLayoutWidget_6)
        self.pushButton_testFTPServer.setObjectName(u"pushButton_testFTPServer")

        self.gridLayout_4.addWidget(self.pushButton_testFTPServer, 0, 0, 1, 1)

        self.pushButton_stopFTPServer = QPushButton(self.gridLayoutWidget_6)
        self.pushButton_stopFTPServer.setObjectName(u"pushButton_stopFTPServer")

        self.gridLayout_4.addWidget(self.pushButton_stopFTPServer, 0, 1, 1, 1)

        self.plainTextEdit_FTPserver_log = QPlainTextEdit(self.gridLayoutWidget_6)
        self.plainTextEdit_FTPserver_log.setObjectName(u"plainTextEdit_FTPserver_log")

        self.gridLayout_4.addWidget(self.plainTextEdit_FTPserver_log, 1, 0, 1, 2)


        self.gridLayout.addWidget(self.groupBox_TestFTPServer, 2, 0, 1, 1)

        self.tabWidget.addTab(self.tab_FTPServer, "")

        self.gridLayout_main.addWidget(self.tabWidget, 1, 0, 1, 1)

        QWidget.setTabOrder(self.tabWidget, self.pushButton_addFTPCamera)
        QWidget.setTabOrder(self.pushButton_addFTPCamera, self.pushButton_removeFTPCamera)
        QWidget.setTabOrder(self.pushButton_removeFTPCamera, self.lineEdit_max_conn)
        QWidget.setTabOrder(self.lineEdit_max_conn, self.lineEdit_ip)
        QWidget.setTabOrder(self.lineEdit_ip, self.lineEdit_max_conn_ip)
        QWidget.setTabOrder(self.lineEdit_max_conn_ip, self.lineEdit_port)
        QWidget.setTabOrder(self.lineEdit_port, self.pushButton_sekectCertificateKey)
        QWidget.setTabOrder(self.pushButton_sekectCertificateKey, self.pushButton_selectKeyFile)
        QWidget.setTabOrder(self.pushButton_selectKeyFile, self.pushButton_testFTPServer)
        QWidget.setTabOrder(self.pushButton_testFTPServer, self.pushButton_stopFTPServer)

        self.retranslateUi(DialogFTPCameras)
        self.buttonBox.accepted.connect(DialogFTPCameras.accept)
        self.buttonBox.rejected.connect(DialogFTPCameras.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DialogFTPCameras)
    # setupUi

    def retranslateUi(self, DialogFTPCameras):
        DialogFTPCameras.setWindowTitle(QCoreApplication.translate("DialogFTPCameras", u"Configure FTP Server and Cameras", None))
        self.label_errorMessage.setText("")
#if QT_CONFIG(accessibility)
        self.tabWidget.setAccessibleName(QCoreApplication.translate("DialogFTPCameras", u"FTP Server", None))
#endif // QT_CONFIG(accessibility)
        self.pushButton_addFTPCamera.setText(QCoreApplication.translate("DialogFTPCameras", u"Add FTP Camera", None))
        self.pushButton_removeFTPCamera.setText(QCoreApplication.translate("DialogFTPCameras", u"Remove FTP Camera", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_FTPcameras), QCoreApplication.translate("DialogFTPCameras", u"FTP Cameras", None))
        self.groupBox_FTPServer.setTitle(QCoreApplication.translate("DialogFTPCameras", u"FTP Server", None))
        self.label_5.setText(QCoreApplication.translate("DialogFTPCameras", u"Max connections:", None))
        self.label_3.setText(QCoreApplication.translate("DialogFTPCameras", u"IP:", None))
        self.pushButton_select_FTPserver_folder.setText(QCoreApplication.translate("DialogFTPCameras", u"Select FTP folder", None))
        self.label_10.setText(QCoreApplication.translate("DialogFTPCameras", u"FTP folder:", None))
        self.label_FTPServer_path.setText("")
        self.label_6.setText(QCoreApplication.translate("DialogFTPCameras", u"Max connections per IP", None))
        self.label_4.setText(QCoreApplication.translate("DialogFTPCameras", u"Port:", None))
        self.label_7.setText(QCoreApplication.translate("DialogFTPCameras", u"Passive ports (range start)", None))
        self.label_8.setText(QCoreApplication.translate("DialogFTPCameras", u"Passive ports (range end)", None))
        self.groupBox_SSL.setTitle(QCoreApplication.translate("DialogFTPCameras", u"SSL", None))
        self.pushButton_sekectCertificateKey.setText(QCoreApplication.translate("DialogFTPCameras", u"Select certificate file", None))
        self.label_key_file_path.setText("")
        self.label_certificate_file_path.setText("")
        self.label_2.setText(QCoreApplication.translate("DialogFTPCameras", u"Certificate file:", None))
        self.label.setText(QCoreApplication.translate("DialogFTPCameras", u"Key file:", None))
        self.pushButton_selectKeyFile.setText(QCoreApplication.translate("DialogFTPCameras", u"Select key file", None))
        self.groupBox_TestFTPServer.setTitle(QCoreApplication.translate("DialogFTPCameras", u"Test FTP Server", None))
        self.pushButton_testFTPServer.setText(QCoreApplication.translate("DialogFTPCameras", u"test FTP Server", None))
        self.pushButton_stopFTPServer.setText(QCoreApplication.translate("DialogFTPCameras", u"Stop FTP server", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_FTPServer), QCoreApplication.translate("DialogFTPCameras", u"FTP Server", None))
    # retranslateUi


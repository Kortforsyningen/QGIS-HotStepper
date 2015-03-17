# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\anfla\.qgis2\python\plugins\HotStepper\ui_HotStepper_settings.ui'
#
# Created: Tue Mar 03 15:57:42 2015
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_HotStepper_settings(object):
    def setupUi(self, HotStepper_settings):
        HotStepper_settings.setObjectName(_fromUtf8("HotStepper_settings"))
        HotStepper_settings.resize(396, 518)
        self.button_box = QtGui.QDialogButtonBox(HotStepper_settings)
        self.button_box.setGeometry(QtCore.QRect(30, 470, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.inShapeA = QtGui.QComboBox(HotStepper_settings)
        self.inShapeA.setGeometry(QtCore.QRect(110, 210, 261, 22))
        self.inShapeA.setObjectName(_fromUtf8("inShapeA"))
        self.inTableName = QtGui.QLineEdit(HotStepper_settings)
        self.inTableName.setGeometry(QtCore.QRect(110, 180, 261, 20))
        self.inTableName.setObjectName(_fromUtf8("inTableName"))
        self.textEdit = QtGui.QTextEdit(HotStepper_settings)
        self.textEdit.setGeometry(QtCore.QRect(110, 330, 171, 111))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.label_2 = QtGui.QLabel(HotStepper_settings)
        self.label_2.setGeometry(QtCore.QRect(40, 180, 61, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(HotStepper_settings)
        self.label_3.setGeometry(QtCore.QRect(40, 210, 46, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.radioButton_2 = QtGui.QRadioButton(HotStepper_settings)
        self.radioButton_2.setGeometry(QtCore.QRect(30, 150, 121, 17))
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.label = QtGui.QLabel(HotStepper_settings)
        self.label.setGeometry(QtCore.QRect(110, 310, 71, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.useSelectedA = QtGui.QCheckBox(HotStepper_settings)
        self.useSelectedA.setGeometry(QtCore.QRect(160, 270, 181, 17))
        self.useSelectedA.setObjectName(_fromUtf8("useSelectedA"))
        self.inField1 = QtGui.QComboBox(HotStepper_settings)
        self.inField1.setGeometry(QtCore.QRect(110, 240, 261, 22))
        self.inField1.setObjectName(_fromUtf8("inField1"))
        self.label_4 = QtGui.QLabel(HotStepper_settings)
        self.label_4.setGeometry(QtCore.QRect(40, 240, 46, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.radioButton = QtGui.QRadioButton(HotStepper_settings)
        self.radioButton.setGeometry(QtCore.QRect(30, 30, 121, 17))
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.inTableA = QtGui.QComboBox(HotStepper_settings)
        self.inTableA.setGeometry(QtCore.QRect(40, 60, 331, 22))
        self.inTableA.setObjectName(_fromUtf8("inTableA"))
        self.checkBoxGCP = QtGui.QCheckBox(HotStepper_settings)
        self.checkBoxGCP.setGeometry(QtCore.QRect(30, 470, 171, 17))
        self.checkBoxGCP.setObjectName(_fromUtf8("checkBoxGCP"))

        self.retranslateUi(HotStepper_settings)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), HotStepper_settings.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), HotStepper_settings.reject)
        QtCore.QMetaObject.connectSlotsByName(HotStepper_settings)

    def retranslateUi(self, HotStepper_settings):
        HotStepper_settings.setWindowTitle(_translate("HotStepper_settings", "HotStepper", None))
        self.label_2.setText(_translate("HotStepper_settings", "Table name", None))
        self.label_3.setText(_translate("HotStepper_settings", "Shape", None))
        self.radioButton_2.setText(_translate("HotStepper_settings", "Create new QC DB", None))
        self.label.setText(_translate("HotStepper_settings", "Errorcodes", None))
        self.useSelectedA.setText(_translate("HotStepper_settings", "Use only selected features", None))
        self.label_4.setText(_translate("HotStepper_settings", "ID field", None))
        self.radioButton.setText(_translate("HotStepper_settings", "Use existing QC DB", None))
        self.checkBoxGCP.setText(_translate("HotStepper_settings", "Prepare DB for GCP check", None))


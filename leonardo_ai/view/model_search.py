# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './leonardo_ai/view/model_search.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ModelSearch(object):
    def setupUi(self, ModelSearch):
        ModelSearch.setObjectName("ModelSearch")
        ModelSearch.resize(610, 475)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ModelSearch)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_2 = QtWidgets.QFrame(ModelSearch)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnModelPlattform = QtWidgets.QPushButton(self.frame)
        self.btnModelPlattform.setEnabled(False)
        self.btnModelPlattform.setObjectName("btnModelPlattform")
        self.horizontalLayout_2.addWidget(self.btnModelPlattform)
        self.btnModelYour = QtWidgets.QPushButton(self.frame)
        self.btnModelYour.setObjectName("btnModelYour")
        self.horizontalLayout_2.addWidget(self.btnModelYour)
        self.btnModelFavorite = QtWidgets.QPushButton(self.frame)
        self.btnModelFavorite.setObjectName("btnModelFavorite")
        self.horizontalLayout_2.addWidget(self.btnModelFavorite)
        self.btnModelCommunity = QtWidgets.QPushButton(self.frame)
        self.btnModelCommunity.setObjectName("btnModelCommunity")
        self.horizontalLayout_2.addWidget(self.btnModelCommunity)
        self.verticalLayout.addWidget(self.frame)
        self.frame_3 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.inSearchQuery = QtWidgets.QLineEdit(self.frame_3)
        self.inSearchQuery.setObjectName("inSearchQuery")
        self.horizontalLayout_3.addWidget(self.inSearchQuery)
        self.btnSearch = QtWidgets.QPushButton(self.frame_3)
        self.btnSearch.setObjectName("btnSearch")
        self.horizontalLayout_3.addWidget(self.btnSearch)
        self.verticalLayout.addWidget(self.frame_3)
        self.frame_4 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy)
        self.frame_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.cmbOrder = QtWidgets.QComboBox(self.frame_4)
        self.cmbOrder.setObjectName("cmbOrder")
        self.cmbOrder.addItem("")
        self.cmbOrder.addItem("")
        self.cmbOrder.addItem("")
        self.cmbOrder.addItem("")
        self.horizontalLayout_4.addWidget(self.cmbOrder)
        self.label_2 = QtWidgets.QLabel(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.cmbCategory = QtWidgets.QComboBox(self.frame_4)
        self.cmbCategory.setObjectName("cmbCategory")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.cmbCategory.addItem("")
        self.horizontalLayout_4.addWidget(self.cmbCategory)
        self.verticalLayout.addWidget(self.frame_4)
        self.verticalLayout_2.addWidget(self.frame_2)
        self.scrollResults = QtWidgets.QScrollArea(ModelSearch)
        self.scrollResults.setWidgetResizable(True)
        self.scrollResults.setObjectName("scrollResults")
        self.frmResults = QtWidgets.QWidget()
        self.frmResults.setGeometry(QtCore.QRect(0, 0, 590, 362))
        self.frmResults.setObjectName("frmResults")
        self.gridLayout = QtWidgets.QGridLayout(self.frmResults)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollResults.setWidget(self.frmResults)
        self.verticalLayout_2.addWidget(self.scrollResults)

        self.retranslateUi(ModelSearch)
        QtCore.QMetaObject.connectSlotsByName(ModelSearch)

    def retranslateUi(self, ModelSearch):
        _translate = QtCore.QCoreApplication.translate
        ModelSearch.setWindowTitle(_translate("ModelSearch", "Dialog"))
        self.btnModelPlattform.setText(_translate("ModelSearch", "Plattform"))
        self.btnModelYour.setText(_translate("ModelSearch", "Your"))
        self.btnModelFavorite.setText(_translate("ModelSearch", "Favorite"))
        self.btnModelCommunity.setText(_translate("ModelSearch", "Community"))
        self.inSearchQuery.setPlaceholderText(_translate("ModelSearch", "Search gallery"))
        self.btnSearch.setText(_translate("ModelSearch", "Search"))
        self.label.setText(_translate("ModelSearch", "Sort By"))
        self.cmbOrder.setItemText(0, _translate("ModelSearch", "Newest - Oldest"))
        self.cmbOrder.setItemText(1, _translate("ModelSearch", "Oldest - Newest"))
        self.cmbOrder.setItemText(2, _translate("ModelSearch", "Name (A-Z)"))
        self.cmbOrder.setItemText(3, _translate("ModelSearch", "Name (Z-A)"))
        self.label_2.setText(_translate("ModelSearch", "Category"))
        self.cmbCategory.setItemText(0, _translate("ModelSearch", "All"))
        self.cmbCategory.setItemText(1, _translate("ModelSearch", "General"))
        self.cmbCategory.setItemText(2, _translate("ModelSearch", "Buildings"))
        self.cmbCategory.setItemText(3, _translate("ModelSearch", "Characters"))
        self.cmbCategory.setItemText(4, _translate("ModelSearch", "Environments"))
        self.cmbCategory.setItemText(5, _translate("ModelSearch", "Fashion"))
        self.cmbCategory.setItemText(6, _translate("ModelSearch", "Illustrations"))
        self.cmbCategory.setItemText(7, _translate("ModelSearch", "Game Items"))
        self.cmbCategory.setItemText(8, _translate("ModelSearch", "Graphical Elements"))
        self.cmbCategory.setItemText(9, _translate("ModelSearch", "Photography"))
        self.cmbCategory.setItemText(10, _translate("ModelSearch", "Pixel Art"))
        self.cmbCategory.setItemText(11, _translate("ModelSearch", "Product Design"))
        self.cmbCategory.setItemText(12, _translate("ModelSearch", "Textures"))
        self.cmbCategory.setItemText(13, _translate("ModelSearch", "UI Elements"))
        self.cmbCategory.setItemText(14, _translate("ModelSearch", "Vector"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ModelSearch = QtWidgets.QDialog()
    ui = Ui_ModelSearch()
    ui.setupUi(ModelSearch)
    ModelSearch.show()
    sys.exit(app.exec_())

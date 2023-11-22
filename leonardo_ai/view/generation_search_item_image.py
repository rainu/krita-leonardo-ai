# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './leonardo_ai/view/generation_search_item_image.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GenerationSearchItemImage(object):
    def setupUi(self, GenerationSearchItemImage):
        GenerationSearchItemImage.setObjectName("GenerationSearchItemImage")
        GenerationSearchItemImage.resize(400, 300)
        self.horizontalLayout = QtWidgets.QHBoxLayout(GenerationSearchItemImage)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(GenerationSearchItemImage)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, -1, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnGfxLoad = QtWidgets.QCommandLinkButton(self.frame_2)
        icon = QtGui.QIcon.fromTheme("edit-copy")
        self.btnGfxLoad.setIcon(icon)
        self.btnGfxLoad.setCheckable(True)
        self.btnGfxLoad.setObjectName("btnGfxLoad")
        self.horizontalLayout_3.addWidget(self.btnGfxLoad)
        self.lblLikeCount = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblLikeCount.sizePolicy().hasHeightForWidth())
        self.lblLikeCount.setSizePolicy(sizePolicy)
        self.lblLikeCount.setText("")
        self.lblLikeCount.setObjectName("lblLikeCount")
        self.horizontalLayout_3.addWidget(self.lblLikeCount)
        self.verticalLayout_6.addWidget(self.frame_2)
        self.tabVariations = QtWidgets.QTabWidget(self.frame)
        self.tabVariations.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabVariations.sizePolicy().hasHeightForWidth())
        self.tabVariations.setSizePolicy(sizePolicy)
        self.tabVariations.setTabPosition(QtWidgets.QTabWidget.South)
        self.tabVariations.setTabsClosable(True)
        self.tabVariations.setMovable(False)
        self.tabVariations.setTabBarAutoHide(False)
        self.tabVariations.setObjectName("tabVariations")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.gfx = QtWidgets.QLabel(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gfx.sizePolicy().hasHeightForWidth())
        self.gfx.setSizePolicy(sizePolicy)
        self.gfx.setAlignment(QtCore.Qt.AlignCenter)
        self.gfx.setObjectName("gfx")
        self.horizontalLayout_7.addWidget(self.gfx)
        self.tabVariations.addTab(self.tab, "")
        self.verticalLayout_6.addWidget(self.tabVariations)
        self.horizontalLayout.addWidget(self.frame)

        self.retranslateUi(GenerationSearchItemImage)
        self.tabVariations.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GenerationSearchItemImage)

    def retranslateUi(self, GenerationSearchItemImage):
        _translate = QtCore.QCoreApplication.translate
        GenerationSearchItemImage.setWindowTitle(_translate("GenerationSearchItemImage", "Form"))
        self.btnGfxLoad.setText(_translate("GenerationSearchItemImage", "Load"))
        self.gfx.setText(_translate("GenerationSearchItemImage", "loading..."))
        self.tabVariations.setTabText(self.tabVariations.indexOf(self.tab), _translate("GenerationSearchItemImage", "#1"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    GenerationSearchItemImage = QtWidgets.QWidget()
    ui = Ui_GenerationSearchItemImage()
    ui.setupUi(GenerationSearchItemImage)
    GenerationSearchItemImage.show()
    sys.exit(app.exec_())

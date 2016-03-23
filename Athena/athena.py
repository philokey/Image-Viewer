from imageContainer import ImageContainer
from deleteDialog import DeleteDialog
from PyQt5 import QtWidgets, QtCore, QtGui, QtNetwork

import sys
import os
import os.path as osp
import datetime
import time
import subprocess
import requests
import pickle

FILE_TYPE = ['jpg', 'jpeg', 'tif', 'bmp', 'gif', 'png']
CIRC = 0
ELLI = 1

class MainWindow(QtWidgets.QMainWindow):
    # _signal = QtCore.pyqtSignal()
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Athena 0.8")
        self.resize(1280, 800)

        self.settings = QtCore.QSettings('setting.ini', QtCore.QSettings.IniFormat)
        # 读入路径
        self.imageFolder = self.showFileDialog()
        # self.imageFolder = '/Users/philokey/Comic'  #调试方便

        # 屏幕居中
        self.screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.size = self.geometry()
        self.move((self.screen.width()-self.size.width())/2, (self.screen.height()-self.size.height())/2)

        # exit = QtWidgets.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        # exit.setShortcut('Ctrl+Q')
        # exit.setStatusTip('Exit application')
        # exit.triggered.connect(self.close)
        # menubar = self.menuBar()
        # file = menubar.addMenu('&File')
        # file.addAction(exit)



        # 文件, 图片, 按钮 三部分
        # self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout = QtWidgets.QHBoxLayout()

        # 文件夹列表model
        self.dirModel = QtWidgets.QDirModel(self)

        # 只显示文件夹
        # self.dirModel.setFilter(QtCore.QDir.Dirs|QtCore.QDir.NoDotAndDotDot)
        # self.fileSystemModel.setFilter(QtCore.QDir.Dirs|QtCore.QDir.NoDotAndDotDot)
        self.dirModel.setSorting(QtCore.QDir.Name)


        # 文件列表view
        self.dirTreeView = QtWidgets.QTreeView()

        # 绑定model
        self.dirTreeView.setModel(self.dirModel)
        # self.dirTreeView.setModel(self.fileSystemModel)
        self.dirTreeView.setRootIndex(self.dirModel.index(self.imageFolder))

        self.dirTreeView.hideColumn(1)
        self.dirTreeView.hideColumn(2)
        self.dirTreeView.hideColumn(3)

        # DirTree事件响应
        self.dirTreeView.selectionModel().selectionChanged.connect(self.dirTreeClicked)

        # self.mainLayout.addWidget(self.dirTreeView, 0, 0)
        self.mainLayout.addWidget(self.dirTreeView)
        # self.mainLayout.setColumnMinimumWidth(1, 800)

        self.imageContainer = ImageContainer()
        # self.mainLayout.addWidget(self.imageContainer, 0, 1)
        # print(self.geometry().width())
        self.imageContainer.setMinimumWidth(self.geometry().width()*0.6)
        print(self.geometry().width()*0.6)
        self.mainLayout.addWidget(self.imageContainer)
        self.initButton()
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.mainLayout)
        self.setCentralWidget(self.widget)
        # self.setLayout(self.mainLayout)
        self.show()
        self.restoreState()


    def initButton(self):
        buttonLayout = QtWidgets.QVBoxLayout()

        # box shape
        slGroup = QtWidgets.QButtonGroup(self)
        slButtonLayout = QtWidgets.QHBoxLayout()
        self.smlRad = QtWidgets.QRadioButton("Small")
        self.smlRad.clicked.connect(self.clickSmlRad)
        self.smlRad.setChecked(True)
        self.larRad = QtWidgets.QRadioButton("Large")

        self.larRad.clicked.connect(self.clickLarRad)
        slButtonLayout.addWidget(self.smlRad)
        slButtonLayout.addWidget(self.larRad)
        slGroup.addButton(self.smlRad)
        slGroup.addButton(self.larRad)
        buttonLayout.addLayout(slButtonLayout)

        # box shape
        rpGroup = QtWidgets.QButtonGroup(self)
        rpradButtonLayout = QtWidgets.QHBoxLayout()
        self.recRad = QtWidgets.QRadioButton("Circle")
        self.recRad.clicked.connect(self.clickRecRad)
        self.recRad.setChecked(True)
        self.polyRad = QtWidgets.QRadioButton("Polygon")
        self.polyRad.clicked.connect(self.clickPolyRad)
        rpradButtonLayout.addWidget(self.recRad)
        rpradButtonLayout.addWidget(self.polyRad)
        rpGroup.addButton(self.recRad)
        rpGroup.addButton(self.polyRad)
        buttonLayout.addLayout(rpradButtonLayout)


        self.deleteBtn = QtWidgets.QPushButton('Delete')
        self.deleteBtn.clicked.connect(self.clickDeleteBtnBtn)
        buttonLayout.addWidget(self.deleteBtn)

        crButtonLayout = QtWidgets.QHBoxLayout()
        self.clearBtn = QtWidgets.QPushButton('Clear!')
        self.clearBtn.clicked.connect(self.clickClearBtn)
        crButtonLayout.addWidget(self.clearBtn)
        self.reloadBtn = QtWidgets.QPushButton('Reload')
        self.reloadBtn.clicked.connect(self.clickReloadBtn)
        crButtonLayout.addWidget(self.reloadBtn)
        buttonLayout.addLayout(crButtonLayout)

        pnButtonLayout = QtWidgets.QHBoxLayout()
        self.preBtn = QtWidgets.QPushButton('Previous')
        self.preBtn.clicked.connect(self.clickPreBtn)
        pnButtonLayout.addWidget(self.preBtn)
        self.nextBtn = QtWidgets.QPushButton('  Next  ')
        self.nextBtn.clicked.connect(self.clickNextBtn)
        pnButtonLayout.addWidget(self.nextBtn)
        buttonLayout.addLayout(pnButtonLayout)

        self.quitBtn = QtWidgets.QPushButton('Quit')
        self.quitBtn.clicked.connect(self.close)
        buttonLayout.addWidget(self.quitBtn)

        # self.mainLayout.addLayout(buttonLayout, 0, 2)
        self.mainLayout.addLayout(buttonLayout)

    def clickSmlRad(self):
        self.imageContainer.isLarge = False
        self.imageContainer.loadImage(self.imageContainer.imagePath)

    def clickLarRad(self):
        self.imageContainer.isLarge = True
        self.imageContainer.loadImage(self.imageContainer.imagePath)

    def clickRecRad(self):
        self.imageContainer.boxShape = 0

    def clickPolyRad(self):
        self.imageContainer.boxShape = 1

    def clickClearBtn(self):
        self.imageContainer.clearImage()

    def clickReloadBtn(self):
        self.imageContainer.loadImage(self.imageContainer.imagePath)


    def clickDeleteBtnBtn(self):
        tp = self.imageContainer.type
        checkedList, isok = DeleteDialog.getInfo(len(self.imageContainer.result[tp]), tp)
        if isok:
            self.imageContainer.deleteBoxes(checkedList)

    def clickNextBtn(self):
        index = self.dirTreeView.currentIndex()
        parent = index.parent()
        rowCnt = self.dirModel.rowCount(parent)
        self.imageContainer.saveResult()
        if index.row() + 1 < rowCnt:
            nextIndex = self.dirModel.index(index.row() + 1, 0, index.parent())
            self.dirTreeView.setCurrentIndex(nextIndex)

    def clickPreBtn(self):
        index = self.dirTreeView.currentIndex()
        parent = index.parent()
        self.imageContainer.saveResult()
        if index.row() - 1 >= 0:
            nextIndex = self.dirModel.index(index.row() - 1, 0, index.parent())
            self.dirTreeView.setCurrentIndex(nextIndex)

    def dirTreeClicked(self):
        #获取选择的路径
        pathSelected = self.dirModel.filePath(self.dirTreeView.selectedIndexes()[0])
        self.imageContainer.setMinimumWidth(self.geometry().width()*0.6)
        if os.path.isfile(pathSelected) and pathSelected.split('.')[-1].lower() in FILE_TYPE:
            self.imageContainer.loadImage(pathSelected)

            resultDir, r0 = self.imageContainer.getOutputFileName(0)
            resultDir, r1 = self.imageContainer.getOutputFileName(1)

    def showFileDialog(self):   # 获取标注图片的文件夹
        # fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        return QtWidgets.QFileDialog.getExistingDirectory(self, 'Open file', self.settings.value("imageFolder"))

    def restoreState(self):
        imageFolder = self.settings.value('imageFolder')
        if imageFolder == self.imageFolder:
            selectedFile = self.settings.value('selected')
            # print(imageFolder, selectedFile)
            index = self.dirModel.index(selectedFile)
            if index.isValid():
                # self.dirTreeView.expand(index)
                self.dirTreeView.setCurrentIndex(index)


    def saveState(self):
        states = []
        for index in self.dirModel.persistentIndexList():
            if self.dirTreeView.isExpanded(index):
                # print(index.data())
                states.append(index.data())
        self.settings.setValue("selected", self.dirModel.filePath(self.dirTreeView.selectedIndexes()[0]))
        self.settings.setValue("imageFolder", self.imageFolder)
        # print(self.dirTreeView.selectedIndexes()[0].row())
        # self.settings.setValue("Path", self.dirTreeView.selectedIndexes()[0])

    def closeEvent(self, event):        #关闭窗口触发以下事件
        print("exit")
        self.saveState()
        # pickle.dump({'view' : self.dirTreeView, 'model' : self.dirModel}, open(osp.join(os.getcwd(), 'config'), 'wb'))
        # reply = QtWidgets.QMessageBox.question(self, '消息框标题', '你确定要退出吗?',  QtWidgets.QMessageBox.Yes |  QtWidgets.QMessageBox.No,  QtWidgets.QMessageBox.No)
        # if reply ==  QtWidgets.QMessageBox.Yes:
        #     event.accept()        #接受关闭事件
        # else:
        #     event.ignore()        #忽略关闭事件


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_show = MainWindow()
    my_show.show()
    sys.exit(app.exec_())
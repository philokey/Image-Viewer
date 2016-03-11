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
RECT = 0
POLY = 1

class MainWindow(QtWidgets.QWidget):
    # _signal = QtCore.pyqtSignal()
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Athena(beta)")
        self.resize(1280, 800)

        self.settings = QtCore.QSettings('setting.ini', QtCore.QSettings.IniFormat)
        # 读入路径
        # imageFolder = self.showFileDialog()
        self.imageFolder = '/Users/philokey/Comic'  #调试方便

        # 屏幕居中
        self.screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.size = self.geometry()
        self.move((self.screen.width()-self.size.width())/2, (self.screen.height()-self.size.height())/2)

        self.show()

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
        print(self.geometry().width())
        self.imageContainer.setMinimumWidth(self.geometry().width()*0.6)
        self.mainLayout.addWidget(self.imageContainer)
        self.initButton()
        self.setLayout(self.mainLayout)
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


        # radio group
        fbGroup = QtWidgets.QButtonGroup(self)
        fbradButtonLayout = QtWidgets.QHBoxLayout()
        self.frameRad = QtWidgets.QRadioButton("Frame")
        self.frameRad.clicked.connect(self.clickFrameRad)
        self.ballRad = QtWidgets.QRadioButton("Balloon")
        self.ballRad.clicked.connect(self.clickBallRad)
        self.frameRad.setChecked(True)
        fbradButtonLayout.addWidget(self.frameRad)
        fbradButtonLayout.addWidget(self.ballRad)
        fbGroup.addButton(self.frameRad)
        fbGroup.addButton(self.ballRad)
        buttonLayout.addLayout(fbradButtonLayout)

        # box shape
        rpGroup = QtWidgets.QButtonGroup(self)
        rpradButtonLayout = QtWidgets.QHBoxLayout()
        self.recRad = QtWidgets.QRadioButton("Rectangle")
        self.recRad.clicked.connect(self.clickRecRad)
        self.recRad.setChecked(True)
        self.polyRad = QtWidgets.QRadioButton("Polygon")
        self.polyRad.clicked.connect(self.clickPolyRad)
        rpradButtonLayout.addWidget(self.recRad)
        rpradButtonLayout.addWidget(self.polyRad)
        rpGroup.addButton(self.recRad)
        rpGroup.addButton(self.polyRad)
        buttonLayout.addLayout(rpradButtonLayout)

        # checkBox
        self.confusedCheckBox = QtWidgets.QCheckBox("Confused")
        self.confusedCheckBox.clicked.connect(self.clickConfusedCheckBox)
        buttonLayout.addWidget(self.confusedCheckBox)

        # detect
        self.detectOfflineBox = QtWidgets.QCheckBox("Detect Offline")
        # self.detectModeBox.clicked.connect(self.clickDetectModeBox)
        buttonLayout.addWidget(self.detectOfflineBox)

        decLayout = QtWidgets.QVBoxLayout()
        self.detectBtn = QtWidgets.QPushButton('Auto Detect')
        self.detectBtn.clicked.connect(self.clickDetectBtn)
        decLayout.addWidget(self.detectBtn)
        self.dectState = QtWidgets.QLabel('')
        self.dectState.setMaximumHeight(10)
        decLayout.addWidget(self.dectState)
        buttonLayout.addLayout(decLayout)

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

    def clickFrameRad(self):
        self.imageContainer.type = 0

    def clickBallRad(self):
        self.imageContainer.type = 1

    def clickRecRad(self):
        self.imageContainer.boxShape = 0

    def clickPolyRad(self):
        self.imageContainer.boxShape = 1

    def clickConfusedCheckBox(self):
        if self.confusedCheckBox.isChecked():
            self.imageContainer.isConfused = True
        else:
            self.imageContainer.isConfused = False

    def clickClearBtn(self):
        self.imageContainer.clearImage()

    def clickReloadBtn(self):
        self.imageContainer.loadImage(self.imageContainer.imagePath)

    def clickDetectBtn(self):
        if self.imageContainer.imagePath == '':
            print("Where is image?")
            return
        exeDir = osp.join(os.getcwd(), 'Storyboard')
        if self.detectOfflineBox.isChecked():
            if osp.isfile(exeDir):
                print("local")
                self.dectState.setText("detecting...")
                self.repaint()
                resultDir, resultName = self.imageContainer.getOutputFileName(0)  # 0 is frame
                fullPath = os.path.join(resultDir, resultName)
                # print(exeDir+' ' + self.imageContainer.imagePath + ' ' + fullPath)
                subprocess.run([exeDir, self.imageContainer.imagePath, fullPath])
                # os.system(exeDir+' ' + self.imageContainer.imagePath + ' ' + fullPath)
                text = open(fullPath).read()
                self.dectState.setText("")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Local detecting program is NOT FOUND!")
                return
        else:
            url = 'http://10.1.89.8:8080/'
            img = {'file':open(self.imageContainer.imagePath, 'rb')}
            self.dectState.setText("detecting...")
            self.repaint()
            try:
                # print(url)
                r = requests.post(url, files=img)
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to establish connection.")
                return
            text = r.text
        self.repaint()
        self.imageContainer.parseDetectedResult(text, 0)
        self.imageContainer.paintTotalResult()
        self.imageContainer.isModified = True

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
        if os.path.isfile(pathSelected) and pathSelected.split('.')[-1].lower() in FILE_TYPE:
            self.confusedCheckBox.setChecked(False)
            self.imageContainer.loadImage(pathSelected)

            resultDir, r0 = self.imageContainer.getOutputFileName(0)
            resultDir, r1 = self.imageContainer.getOutputFileName(1)
            if not os.path.isfile(os.path.join(resultDir, r0)) and not os.path.isfile(os.path.join(resultDir, r1)):
                self.dectState.setText("Not Detected")
            else:
                self.dectState.setText("")
            if self.frameRad.isChecked():
                self.imageContainer.type = 0
            else:
                self.imageContainer.type = 1

    def showFileDialog(self):   # 获取标注图片的文件夹
        # fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        return QtWidgets.QFileDialog.getExistingDirectory(self, 'Open file', '/User/Philokey')

    def restoreState(self):
        imageFolder = self.settings.value('imageFolder')
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
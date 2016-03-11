from imageContainer import ImageContainer
from deleteDialog import DeleteDialog
from PyQt5 import QtWidgets, QtCore, QtGui, QtNetwork

import sys
import os
import datetime
import time
import subprocess
import requests

FILE_TYPE = ['jpg', 'jpeg', 'tif', 'bmp', 'gif', 'png']
RECT = 0
POLY = 1

class MainWindow(QtWidgets.QWidget):
    # _signal = QtCore.pyqtSignal()
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Athena(beta)")
        self.resize(1280, 800)

        # 读入路径
        # imageFolder = self.showFileDialog()
        imageFolder = '/Users/philokey/Comic'  #调试方便

        # 屏幕居中
        self.screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.size = self.geometry()
        self.move((self.screen.width()-self.size.width())/2, (self.screen.height()-self.size.height())/2)

        self.show()

        # 文件, 图片, 按钮 三部分
        self.mainLayout = QtWidgets.QGridLayout()

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
        self.dirTreeView.setRootIndex(self.dirModel.index(imageFolder))

        self.dirTreeView.hideColumn(1)
        self.dirTreeView.hideColumn(2)
        self.dirTreeView.hideColumn(3)

        # DirTree事件响应
        self.dirTreeView.selectionModel().selectionChanged.connect(self.dirTreeClicked)

        self.mainLayout.addWidget(self.dirTreeView, 0, 0)
        self.mainLayout.setColumnMinimumWidth(1, 800)

        self.imageContainer = ImageContainer()
        self.mainLayout.addWidget(self.imageContainer, 0, 1)

        self.initButton()

        self.mainLayout.setColumnMinimumWidth(2, 200)
        self.mainLayout.setColumnMinimumWidth(0, 200)

        self.setLayout(self.mainLayout)

    def initButton(self):
        buttonLayout = QtWidgets.QVBoxLayout()
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

        self.mainLayout.addLayout(buttonLayout, 0, 2)

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
        exeDir = os.path.join(os.getcwd(), 'Storyboard')
        if self.detectOfflineBox.isChecked():
            if os.path.isfile(exeDir):
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
        print('fileSelected   ', pathSelected)
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_show = MainWindow()
    my_show.show()
    sys.exit(app.exec_())
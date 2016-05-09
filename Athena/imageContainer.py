from PyQt5 import QtWidgets, QtCore, QtGui
import os

MAXWIDTH = 750
MAXHEIGHT = 600

RECT = 0
POLY = 1

class ImageContainer(QtWidgets.QFrame):
    def __init__(self, widgets = None):
        super(ImageContainer, self).__init__()
        containerLayout = QtWidgets.QVBoxLayout()

        self.graphicsView = QtWidgets.QGraphicsView()
        self.graphicsView.setCursor(QtCore.Qt.CrossCursor)
        self.graphicsView.setObjectName("graphicsView")
        # self.image can be painted
        self.image = QtGui.QPixmap()
        # self.oriImage is the original image
        self.oriImage = QtGui.QPixmap()

        containerLayout.addWidget(self.graphicsView)
        self.setLayout(containerLayout)
        # 当前绘制的多边形的顶点
        self.vertexes = []
        # frames and balloons
        self.result = [[], []]

        self.isModified = False
        self.isConfused = False
        self.isLarge = False
        # 0 for rectangle, 1 for polygon
        self.boxShape = 0
        self.scale = 1
        self.imagePath = ''
        self.preImagePath = ''
        self.type = 0  # 0 frame, 1 Balloon
        self.boxColor = (QtCore.Qt.blue, QtCore.Qt.red)
        self.typeName = ('Frame', 'Balloon')
        self.typeId = (0, 1)

    def loadImage(self, path):
        self.vertexes = []
        self.result = [[], []]
        self.isModified = False
        self.isConfused = False
        print(path)
        self.image.load(path, '1') #read image
        self.imagePath = path
        imgSize = self.image.size()
        # print(self.image, imgSize)
        print(self.geometry())
        MAXWIDTH = self.geometry().width()*0.9
        MAXHEIGHT = self.geometry().height()*0.9
        if self.isLarge:
            # if image is too wide, it should be resize to width = MAXWIDTH
            if imgSize.width() > MAXWIDTH:
                self.scale = imgSize.width() / MAXWIDTH
                imgSize /= self.scale
                self.image = self.image.scaled(imgSize, transformMode = QtCore.Qt.SmoothTransformation)
            else:
                self.scale = 1
            self.oriImage = self.image.copy()
            self.loadExistResult(path)
        else:
            # if image is too wide, it should be resize to width = MAXWIDTH
            if imgSize.height() > MAXHEIGHT:
                self.scale = imgSize.height() / MAXHEIGHT
                imgSize /= self.scale
                self.image = self.image.scaled(imgSize, transformMode = QtCore.Qt.SmoothTransformation)
            else:
                self.scale = 1
        self.oriImage = self.image.copy()
        self.loadExistResult(path)

    def loadExistResult(self, path):
        splitedPath = self.imagePath.split('/')
        baseDir = '/'.join(splitedPath[:-1])
        imageName = splitedPath[-1]
        resultDir = os.path.join(baseDir, 'result')
        for t in (0, 1):
            resultName = self.typeName[t] + '_' + imageName + '.txt'
            fullPath = os.path.join(resultDir, resultName)
            if os.path.isfile(fullPath):
                resultTxt = open(fullPath).read()
                self.parseDetectedResult(resultTxt, t)
        self.paintTotalResult()

    def clearImage(self):
        if self.imagePath != '':
            self.isModified = True
            self.result = [[], []]
            self.vertexes.clear()
            self.image = self.oriImage.copy()
            scene = QtWidgets.QGraphicsScene()
            scene.addPixmap(self.image)
            self.graphicsView.setScene(scene)
        else:
            print("Nothing to clear")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.paintVertex(event)
            if self.boxShape == POLY:
                self.paintLine(True)

        elif event.button() == QtCore.Qt.RightButton:
            self.isModified = True
            if len(self.vertexes) < 2:
                return
            if self.boxShape == RECT:
                if len(self.vertexes) == 2:
                    self.paintRectangle()
                else:
                    self.paintPolygon()
            else:
                self.paintLine(False)

    def paintLine(self, isLeft):
        n = len(self.vertexes)
        if n < 2: return
        tp = self.type
        painter = self.initMyPainter(tp)
        if isLeft:
            painter.drawLine(self.vertexes[n - 2], self.vertexes[n - 1])
        else:
            mx = sum(v.x() for v in self.vertexes) / n
            my = sum(v.y() for v in self.vertexes) / n
            self.result[tp].append(self.vertexes[:])
            painter.drawLine(self.vertexes[-1], self.vertexes[0])
            painter.drawText(QtCore.QPoint(mx, my), str(len(self.result[tp])))
            self.vertexes.clear()
        scene = QtWidgets.QGraphicsScene()
        # scene.addPixmap(QtGui.QPixmap.fromImage(self.image))
        scene.addPixmap(self.image)
        self.graphicsView.setScene(scene)

    def paintVertex(self, event):
        painter = QtGui.QPainter(self.image)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(QtCore.Qt.black))
        pen.setWidth(3)
        painter.setPen(pen)

        # 转化成图片坐标, 并不知道为什么还会有个小的偏移值
        p = self.graphicsView.mapToScene(event.pos()) - self.graphicsView.pos() - QtCore.QPoint(2, 1)
        p = QtCore.QPoint(p.x(), p.y())
        painter.drawPoint(p)

        # print('maptosence: ', p)
        self.vertexes.append(p)
        scene = QtWidgets.QGraphicsScene()
        # scene.addPixmap(QtGui.QPixmap.fromImage(self.image))
        scene.addPixmap(self.image)
        self.graphicsView.setScene(scene)

    def initMyPainter(self, tp):
        painter = QtGui.QPainter(self.image)
        pen = QtGui.QPen()
        pen.setColor(self.boxColor[tp])
        pen.setWidth(3)
        painter.setPen(pen)
        font = QtGui.QFont()
        font.setPointSize(40)
        font.setBold(True)
        painter.setFont(font)
        return painter

    def paintRectangle(self):
        painter = self.initMyPainter(self.type)
        topLeft = QtCore.QPoint(min(self.vertexes[0].x(), self.vertexes[1].x()),
                                min(self.vertexes[0].y(), self.vertexes[1].y()))
        topRight = QtCore.QPoint(min(self.vertexes[0].x(), self.vertexes[1].x()),
                                 max(self.vertexes[0].y(), self.vertexes[1].y()))
        bottomleft = QtCore.QPoint(max(self.vertexes[0].x(), self.vertexes[1].x()),
                                   min(self.vertexes[0].y(), self.vertexes[1].y()))
        bottomRight = QtCore.QPoint(max(self.vertexes[0].x(), self.vertexes[1].x()),
                                    max(self.vertexes[0].y(), self.vertexes[1].y()))
        self.result[self.type].append([topLeft, topRight, bottomRight, bottomleft])
        rect = QtCore.QRect(topLeft, bottomRight)
        painter.drawRect(rect)
        mx = (self.vertexes[0].x() + self.vertexes[1].x()) / 2
        my = (self.vertexes[0].y() + self.vertexes[1].y()) / 2
        painter.drawText(QtCore.QPoint(mx, my), str(len(self.result[self.type])))
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(self.image)
        self.graphicsView.setScene(scene)
        self.vertexes.clear()

    def paintPolygon(self):
        self.result[self.type].append(self.vertexes[:])
        n = len(self.vertexes)
        painter = self.initMyPainter(self.type)
        mx = sum(v.x() for v in self.vertexes) / n
        my = sum(v.y() for v in self.vertexes) / n
        painter.drawPolygon(QtGui.QPolygon(self.vertexes))

        painter.drawText(QtCore.QPoint(mx, my), str(len(self.result[self.type])))
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(self.image)
        self.graphicsView.setScene(scene)
        self.vertexes.clear()

    def parseDetectedResult(self, result, tp):
        lines = result.strip().split('\n')
        self.result[tp].clear()
        try:
            n = int(lines[0])
            for i in range(1, n + 1):
                points = list(map(int, lines[i].strip().split()))
                m = points[0] * 2 + 1
                if self.scale != 1:
                    points = [p / self.scale for p in points]
                vs = []
                for j in range(1, m, 2):
                    vs.append(QtCore.QPoint(points[j], points[j + 1]))
                self.result[tp].append(vs)
        except:
            print("Parse Error! Result's format is wrong!")

    def paintTotalResult(self):
        # print("after delete.........................")
        for tp in self.typeId:
            painter = self.initMyPainter(tp)
            for id, vertexes in enumerate(self.result[tp]):
                n = len(vertexes)
                mx = sum(v.x() for v in vertexes) / n
                my = sum(v.y() for v in vertexes) / n
                painter.drawPolygon(QtGui.QPolygon(vertexes))
                painter.drawText(QtCore.QPoint(mx, my), str(id + 1))
            painter.end()
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(self.image)
        self.graphicsView.setScene(scene)
        # self.repaint()
        # self.graphicsView.repaint()

    def deleteBoxes(self, dlst):
        # A naive way to delete boxes. To be update.
        l = []
        tp = self.type
        n = len(self.result[tp])
        for i in range(n):
            if i not in dlst:
                l.append(self.result[tp][i])

        self.result[tp] = l
        self.image = self.oriImage.copy()
        self.paintTotalResult()
        self.isModified = True
        # self.paintTotalResult(tp ^ 1)

    def getOutputFileName(self, t):
        splitedPath = self.imagePath.split('/')
        baseDir = '/'.join(splitedPath[:-1])
        imageName = splitedPath[-1]
        resultDir = os.path.join(baseDir, 'result')
        if os.path.exists(resultDir) == False:
            os.mkdir(resultDir)
        resultName = self.typeName[t] + '_' + imageName + '.txt'
        return resultDir, resultName

    def saveResult(self):
        if self.isModified:
            for t in (0, 1):
                n = len(self.result[t])
                resultDir, resultName = self.getOutputFileName(t)
                outFile = open(os.path.join(resultDir, resultName), 'w')
                outFile.write(str(n)+'\n')
                for res in self.result[t]:
                    m = len(res)
                    outFile.write(str(m))
                    if self.scale != 1:
                        res = [p * self.scale for p in res]
                    for i in range(m):
                        outFile.write(' ' + str(res[i].x()) + ' ' + str(res[i].y()))
                    outFile.write('\n')
                outFile.close()
        else:
            print("Nothing to save!")

        if self.isConfused:
            splitedPath = self.imagePath.split('/')
            baseDir = '/'.join(splitedPath[:-1])
            resultDir = os.path.join(baseDir, 'result')
            if os.path.exists(resultDir) == False:
                os.mkdir(resultDir)
            outFile = open(os.path.join(resultDir, 'confused.txt'), 'a+', encoding='utf-8')
            outFile.write(self.imagePath + '\n')
            outFile.close()



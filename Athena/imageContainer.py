from PyQt5 import QtWidgets, QtCore, QtGui
import os
import math
import cv2
import numpy as np

MAXWIDTH = 750
MAXHEIGHT = 600

CIRC = 0
ELLI = 1

class ImageContainer(QtWidgets.QFrame):
    def __init__(self, widgets = None):
        super(ImageContainer, self).__init__()
        containerLayout = QtWidgets.QVBoxLayout()

        self.graphicsView = QtWidgets.QGraphicsView()
        # self.graphicsView.setCursor(QtCore.Qt.CrossCursor)
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
        self.result = []

        self.isModified = False
        self.isLarge = False
        # 0 for rectangle, 1 for polygon
        self.boxShape = ELLI
        self.scale = 1
        self.imagePath = ''
        self.preImagePath = ''
        self.boxColor = (QtCore.Qt.blue, QtCore.Qt.red)
        self.typeId = (0, 1)

    def loadImage(self, path):
        self.vertexes = []
        self.result = []
        self.isModified = False
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
        # self.loadExistResult(path)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(self.image)
        self.graphicsView.setScene(scene)

    def loadExistResult(self, path):
        '''
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
        '''
        pass

    def clearImage(self):
        if self.imagePath != '':
            self.isModified = True
            self.result = []
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

        elif event.button() == QtCore.Qt.RightButton:
            self.isModified = True
            if len(self.vertexes) < 2:
                return
            if self.boxShape == CIRC:
                self.paintCircle()
            elif self.boxShape == ELLI:
                self.fitEllipse()

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
        print(p)
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

    def fitCircle(self):
        p1x, p1y = self.vertexes[-3].x(), self.vertexes[-3].y()
        p2x, p2y = self.vertexes[-2].x(), self.vertexes[-2].y()
        p3x, p3y = self.vertexes[-1].x(), self.vertexes[-1].y()

        midP1x = (p2x + p1x) / 2
        midP1y = (p2y + p1y) / 2

        midP2x = (p3x + p1x) / 2
        midP2y = (p3y + p1y) / 2

        k1 = -(p2x - p1x) / (p2y - p1y)
        k2 = -(p3x - p1x) / (p3y - p1y)
        cx = (midP2y - midP1y - k2 * midP2x + k1 * midP1x) / (k1 - k2)
        cy = midP1y + k1 * (midP2y - midP1y - k2 * midP2x + k2 * midP1x) / (k1 - k2)
        r = math.sqrt((cx - p1x)*(cx - p1x) + (cy - p1y) * (cy - p1y))
        print(cx, cy, r)
        return cx, cy, r

    def fitEllipse(self):
        points = []
        for v in self.vertexes:
            x, y = v.x(), v.y()
            points.append((x, y))
        points = np.array(points)
        # print(points)
        ell = cv2.fitEllipse(points)
        print("%.6f %.6f %.6f %.6f %.3f" % (ell[0][0], ell[0][1], ell[1][0] / 2, ell[1][1] / 2, ell[2]))
        self.vertexes.clear()
        self.result.append((ell[0][0], ell[0][1], ell[1][0] / 2, ell[1][1] / 2, ell[2]))

    def paintCircle(self):
        circle = self.fitCircle()
        self.result.append(circle)
        painter = self.initMyPainter(self.boxShape)
        cx, cy, r = circle[0], circle[1], circle[2]
        painter.drawEllipse(cx - r, cy - r, r*2, r*2)
        # painter.drawText(QtCore.QPoint(mx, my), str(len(self.result[self.type])))
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(self.image)
        self.graphicsView.setScene(scene)
        self.vertexes.clear()

    def parseDetectedResult(self, result, tp):
        lines = result.strip().split('\n')
        self.result.clear()
        try:
            n = int(lines[0])
            for i in range(1, n + 1):
                points = list(map(int, lines[i].strip().split()))

                if self.scale != 1:
                    points = [p / self.scale for p in points]
                vs = []
                for j in range(3):
                    vs.append(points[j])
                self.result.append(vs)
        except:
            print("Parse Error! Result's format is wrong!")

    # def paintTotalResult(self):
    #     for tp in self.typeId:
    #         painter = self.initMyPainter(tp)
    #         for id, vertexes in enumerate(self.result[tp]):
    #             n = len(vertexes)
    #             mx = sum(v.x() for v in vertexes) / n
    #             my = sum(v.y() for v in vertexes) / n
    #             painter.drawPolygon(QtGui.QPolygon(vertexes))
    #             painter.drawText(QtCore.QPoint(mx, my), str(id + 1))
    #         painter.end()
    #     scene = QtWidgets.QGraphicsScene()
    #     scene.addPixmap(self.image)
    #     self.graphicsView.setScene(scene)

    # def deleteBoxes(self, dlst):
    #     # A naive way to delete boxes. To be update.
    #     l = []
    #     tp = self.type
    #     n = len(self.result[tp])
    #     for i in range(n):
    #         if i not in dlst:
    #             l.append(self.result[tp][i])
    #
    #     self.result[tp] = l
    #     self.image = self.oriImage.copy()
    #     self.paintTotalResult()
    #     self.isModified = True
    #     # self.paintTotalResult(tp ^ 1)

    def getOutputFileName(self, t):
        splitedPath = self.imagePath.split('/')
        baseDir = '/'.join(splitedPath[:-1])
        imageName = splitedPath[-1]
        resultDir = os.path.join(baseDir, 'result')
        if os.path.exists(resultDir) == False:
            os.mkdir(resultDir)
        resultName = 'circle' + '_' + imageName + '.txt'
        return resultDir, resultName

    def saveResult(self):
        if self.isModified:
            for t in (0, 1):
                n = len(self.result)
                resultDir, resultName = self.getOutputFileName(t)
                outFile = open(os.path.join(resultDir, resultName), 'w')
                outFile.write(str(n)+'\n')
                print(self.result)
                for res in self.result:
                    if self.scale != 1:
                        res = [p * self.scale for p in res]
                        # print(res)
                    outFile.write(' '.join(str(round(r, 5)) for r in res) + '\n')
                    # outFile.write(str(res[0]) + ' ' + str(res[1]) + ' ' + str(res[2]) + '\n')
                outFile.close()
        else:
            print("Nothing to save!")





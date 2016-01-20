from PyQt5 import QtWidgets, QtCore
import math

class DeleteDialog(QtWidgets.QDialog):
    def __init__(self, n, tp):
        super(DeleteDialog, self).__init__()
        layout = QtWidgets.QGridLayout()
        if tp == 0:
            self.label = QtWidgets.QLabel('Frame')
        else:
            self.label = QtWidgets.QLabel('Balloon')
        layout.addWidget(self.label, 0, 0)

        self.n = n
        self.checkBoxList = []
        for i in range(n):
            box = QtWidgets.QCheckBox(str(i + 1))
            self.checkBoxList.append(box)
            layout.addWidget(self.checkBoxList[-1], int(i / 2) + 1, i % 2)
        self.setLayout(layout)
        # OK and Cancel buttons
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal)
        # 怎么样才能把按钮放好看点,丑哭
        layout.addWidget(self.buttons, math.ceil((n + 1) / 2) + 1, 0)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def getChecked(self):
        ret = []
        for i, box in enumerate(self.checkBoxList):
            if box.isChecked():
                ret.append(i)
        return ret

    @staticmethod
    def getInfo(n, tp):
        dialog = DeleteDialog(n, tp)
        result = dialog.exec_()
        ret = dialog.getChecked()
        return ret, result == QtWidgets.QDialog.Accepted
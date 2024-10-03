from functools import partial
from Qt import QtCore
from Qt import QtWidgets as QtWid


class DynamicTable(QtWid.QScrollArea):
    def __init__(self, parent, **kwargs):
        """
        Initialises the widget and adds it to the parent widget

        args:
            parent, required, pass your main widget "self"
        kwargs:

            numColumns,     (int), The number of columns that you need to have in the table,
            columnWidths,   ([int,int..]), list of column widths, set to 0 to set column to stretch to available size,
            columnsVisible, ([bool,bool..]), sets each columns visibility,
            height,         (int), height of the widget,
            width,          (int), width of the widget,
            headers,        ([str,str..]), the name for each column, shown in the header row,
            alternateRows,  (bool), to alternate the rows background colour, set this to True
            useCustomAlternateRows,  (bool), set this to True if you want to define when the rows alternate
                                Using this will disable sorting
            setWidgetBG,    (bool), to force the background colour, set this to True, **OVERRIDES** alternateRows
            columnAlignment,([str,str..]), side to align each column: [left, right, top, bottom], defaults to left
            disableHeaderSortText, (bool), if set will remove the "(a-z)" or "(z-a)" from the header text!
            rowBorder,      (bool), if set will add a border around each row, default is True
        """
        QtWid.QScrollArea.__init__(self, parent)
        self.rowIndexs = []
        self.currentRowIndex = 0
        self.rows = {}
        self.cellWidgets = {}
        self.rowVisibility = {}
        self.parent = parent
        self.wdth = kwargs.get("width", 300)
        self.hght = kwargs.get("height", 300)
        self.numColumns = kwargs.get("numColumns", 1)
        self.altRows = kwargs.get("alternateRows", False)
        self.useCustomAltRows = kwargs.get("useCustomAlternateRows", False)
        self.rowBorder = kwargs.get("rowBorder", True)
        self.setWidgetBG = kwargs.get("setWidgetBG", True)
        self.columnWidths = kwargs.get("columnWidths", [0 for x in range(0, self.numColumns)])
        self.columnAlignment = kwargs.get("columnAlignment", ["left" for x in range(0, self.numColumns)])
        self.columnsVisible = kwargs.get("columnsVisible", [True for x in range(0, self.numColumns)])
        self.headers = kwargs.get("headers", None)
        self.disableHeaderSortText = kwargs.get("disableHeaderSortText", None)
        self.QValueFunctionDict = {
            "QToolButton": ".text()",
            "QPushButton": ".text()",
            "QLabel": ".text()",
            "QLinEdit": ".text()",
            "QSpinBox": ".value()",
            "QSlider": ".value()",
            "QComboBox": ".currentText()",
        }
        self.mainWidget = QtWid.QWidget()
        self.setWidget(self.mainWidget)
        sizePolicy = QtWid.QSizePolicy(QtWid.QSizePolicy.Minimum, QtWid.QSizePolicy.Fixed)
        self.mainWidget.setSizePolicy(sizePolicy)
        self.setSizePolicy(QtWid.QSizePolicy.Minimum, QtWid.QSizePolicy.Minimum)
        self.setAutoFillBackground(False)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sLayout = QtWid.QVBoxLayout(self.widget())
        self.mLayout = QtWid.QVBoxLayout()
        self.sLayout.setContentsMargins(2, 2, 2, 2)
        self.widget().setObjectName("scrollWidgetBG")
        self.setGeometry(0, 0, self.wdth, self.hght)
        self.setObjectName("scrollWidgetBG")
        self.sortData = {}
        self.sorted = False
        self.AlignmentDict = {
            "left": QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
            "right": QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
            "center": QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
            "top": QtCore.Qt.AlignTop | QtCore.Qt.AlignVCenter,
            "bottom": QtCore.Qt.AlignBottom | QtCore.Qt.AlignVCenter,
        }
        self.setWidgetResizable(True)
        if self.headers:
            self.headerFrame = QtWid.QFrame(self)
            self.headerFrame.setFrameShape(QtWid.QFrame.StyledPanel)
            self.headerFrame.setFrameShadow(QtWid.QFrame.Raised)
            self.headerRow = QtWid.QHBoxLayout(self.headerFrame)
            self.headerRow.setSpacing(0)
            self.headerItems = {}
            self.mLayout.addLayout(self.headerRow, QtCore.Qt.AlignTop)
            self.headerRow.setContentsMargins(0, 0, 0, 0)
            self.mLayout.setContentsMargins(0, 23, 0, 0)
            self.setHorizontalHeaderLabels(self.headers)
        else:
            self.mLayout.setContentsMargins(0, 0, 0, 0)
        self.mLayout.setSpacing(0)

        self.sLayout.addLayout(self.mLayout)
        self.sLayout.addStretch(1)
        self.alternateRowState = False
        self.currentRowColour = "widgetBG"

    def addRow(self, height=26, rowWidgets=None, data={}, isAlternateRow=False):
        """
        Add row of widgets to the table

        args:
            height, (int), optional, the height if the new row, defaults to 26
            data, (dict), optional, dictionary of any custom data that you want to store per row

        returns: (int), rowId
        """
        rowId = int(self.currentRowIndex)
        self.rowIndexs.append(self.currentRowIndex)
        self.rows[rowId] = {
            "data": data,
            "widget": QtWid.QWidget(self),
            "layout": QtWid.QHBoxLayout(),
            "height": height,
        }
        self.mLayout.addWidget(self.rows[rowId]["widget"], QtCore.Qt.AlignTop)
        self.rows[rowId]["widget"].setLayout(self.rows[rowId]["layout"])
        self.rowVisibility[rowId] = True
        self.cellWidgets[rowId] = []
        self.currentRowIndex += 1

        self.rows[rowId]["widget"].setMinimumHeight(height)
        self.rows[rowId]["widget"].setContentsMargins(0, 0, 0, 0)
        self.rows[rowId]["layout"].setSpacing(0)
        self.rows[rowId]["layout"].setContentsMargins(0, 0, 0, 0)

        if rowWidgets:
            self.addWidgetToRow(rowId, rowWidgets, height)

        rowBGColour = "widgetBG"
        if self.altRows:
            if self.useCustomAltRows and isAlternateRow:
                if self.alternateRowState:
                    self.alternateRowState = False
                    if self.rowBorder:
                        rowBGColour = "alternateBorderBG"
                    else:
                        rowBGColour = "AlternateBG"
                else:
                    self.alternateRowState = True
                    if self.rowBorder:
                        rowBGColour = "tabBorderBG"
                    else:
                        rowBGColour = "tabBG"
                self.currentRowColour = rowBGColour
            elif self.useCustomAltRows:
                rowBGColour = self.currentRowColour
            else:
                if self.alternateRowState:
                    self.alternateRowState = False
                    if self.rowBorder:
                        rowBGColour = "alternateBorderBG"
                    else:
                        rowBGColour = "AlternateBG"
                else:
                    self.alternateRowState = True
                    if self.rowBorder:
                        rowBGColour = "tabBorderBG"
                    else:
                        rowBGColour = "tabBG"
        elif self.rowBorder:
            rowBGColour = "widgetBorderBG"

        self.rows[rowId]["widget"].setObjectName(rowBGColour)
        for widg in rowWidgets:
            widg.setObjectName(rowBGColour)

        return rowId

    def addWidgetToRow(self, rowId, item, minHeight=28):
        """
        Adds the given widget to the given row

        args:
            rowId, (int), required, The ID of the row that you want to widget added to
            item, (QWidget), required, the widget you wish to add to the row

        returns: item, (QWidget), the newly added widget you passed in
        """
        if isinstance(item, list):
            Items = []
            for it in item:
                Items.append(self.addWidgetToRow(rowId, it, minHeight))
            return Items

        if self.setWidgetBG:
            item.setObjectName("widgetBG")
        colNum = len(self.cellWidgets[rowId])
        alignment = self.AlignmentDict[self.columnAlignment[colNum]]
        self.rows[rowId]["layout"].addWidget(item, alignment)
        item.setMinimumHeight(minHeight)
        item.setVisible(self.columnsVisible[colNum])
        try:
            item.setAlignment(alignment)
        except:
            pass
        colWidth = self.columnWidths[colNum]

        if not colWidth == 0:
            item.setMaximumWidth(colWidth)
        self.cellWidgets[rowId].append(item)
        return item

    def setRowVisibility(self, rowId, visible=True):
        """
        Sets row visibility for the given rowId

        args:
            rowId, (int), required, The ID of the row that you want to widget added to
            visible, (bool), optional, default is true
        """
        self.rowVisibility[rowId] = visible
        for widget in self.cellWidgets[rowId]:
            widget.setVisible(self.rowVisibility[rowId])

    def removeRow(self, rowId):
        if self.cellWidgets[rowId]:
            for widget in self.cellWidgets[rowId]:
                self.rows[rowId]["layout"].removeWidget(widget)
                widget.deleteLater()
            self.cellWidgets[rowId] = None
            self.rows[rowId]["layout"].deleteLater()
            self.mLayout.removeWidget(self.rows[rowId]["widget"])
            self.rows[rowId]["widget"].deleteLater()
        if "layout" in self.rows[rowId]:
            del self.rows[rowId]["layout"]
        if "widget" in self.rows[rowId]:
            del self.rows[rowId]["widget"]
        if rowId in self.rowIndexs:
            self.rowIndexs.remove(rowId)

    def clearTable(self):
        """
        Removes all rows and all widgets and clears out the dictionaries holding them
        """
        for rowId in self.rows.keys():
            self.removeRow(rowId)
        self.rows = {}
        self.rowIndexs = []
        self.cellWidgets = {}
        self.currentRowIndex = 0

    def setHorizontalHeaderLabels(self, headers):
        """
        Sets the row headers

        args:
            headers, ([str, str, ..]), required, the name of the headers in a list of all the columns
        """
        for widg in self.headerItems:
            widg.deleteLater()
            self.headerRow.removeWidget(widg)
        self.headerItems = {}
        for colId, header in enumerate(headers):
            self.headerItems[colId] = QtWid.QPushButton()
            self.headerItems[colId].setText(header)
            self.headerItems[colId].setFlat(True)
            self.headerItems[colId].clicked.connect(partial(self.sortColumns, colId, True, True))
            self.headerItems[colId].setObjectName("headerLabels")
            self.headerItems[colId].setVisible(self.columnsVisible[colId])
            colWidth = self.columnWidths[colId]
            if not colWidth == 0:
                self.headerItems[colId].setFixedWidth(colWidth)
            self.headerRow.addWidget(self.headerItems[colId])

    def sortColumns(self, colId=None, swap=False, switchColumns=False):
        """
        sorts all the rows by the given column

        args:
            colId, (int), optional, the index of the column
            swap, (bool), optional, if True will swap the sort direction, defaults to False
            switchColumns, (bool), optional, if True will switch to a different column, defaults to False
        """
        if not self.useCustomAltRows:
            for cId in self.sortData.keys():
                if not self.disableHeaderSortText:
                    self.headerItems[cId].setText(
                        self.headerItems[cId].text().replace(" (z-a)", "").replace(" (a-z)", "")
                    )
            if isinstance(colId, int) and len(self.rows.keys()) > 1:
                if switchColumns:
                    self.sorted = colId
                if colId not in self.Data.keys():
                    self.sortData[colId] = {}
                if "descending" not in self.sortData[colId]:
                    self.sortData[colId]["descending"] = True
            elif self.sorted:
                colId = self.sorted
            else:
                return

            ReOrderList = []
            for qType, rowId in [[type(self.cellWidgets[rowId][colId]), rowId] for rowId in self.rows.keys()]:
                qType = str(qType).rsplit(".", 1)[1][:-2]
                value = eval("self.cellWidgets[{}][{}]{}".format(rowId, colId, self.QValueFunctionDict[qType]))
                ReOrderList.append([value, rowId])
            cleanedTitle = self.headerItems[colId].text().replace(" (z-a)", "").replace(" (a-z)", "")
            if self.sortData[colId]["descending"]:
                self.headeerItems[colId].setText(cleanedTitle + " (a-z)")
            else:
                self.headeerItems[colId].setText(cleanedTitle + " (z-a)")
            if swap:
                self.sortData[colId]["descending"] = not self.sortData[colId]["descending"]
            self.sortData[colId]["newOrder"] = [
                rId[1] for rId in sorted(ReOrderList, reverse=self.sortData[colId]["descending"])
            ]
            [self.mLayout.removeWidget(self.rows[rowId]["widget"]) for rowId in self.rows.keys()]
            [self.mLayout.addWidget(self.rows[rowId]["widget"]) for rowId in self.sortData[colId]["newOrder"]]

    def setColumnVisibility(self, columnsVisList):
        """
        Sets column visibility for all the columns

        args:
            columnsVisList, ([bool, bool, ..]), required, a list of the visibility for every column
        """
        self.columnsVisible = columnsVisList
        for col, visibility in enumerate(columnsVisList):
            for rowId in self.rows.keys():
                self.cellWidgets[rowId][col].setVisible(visibility)
            self.headerItems[col].setVisible(visibility)

    def setOneColumnVisibility(self, state, columnNumber):
        for rowId in self.rows.keys():
            self.cellWidgets[rowId][columnNumber].setVisible(state)
        self.headerItems[columnNumber].setVisible(state)

    def resizeEvent(self, event):
        """
        Event automatically called each time the use resizes the window to adjust the custom QScrollArea

        args:
            event
        """
        if self.headers:
            self.headerFrame.resize(self.width(), 24)
        QtWid.QScrollArea.resizeEvent(self, event)

    def getWidget(self, rowId, colId):
        """
        Gets the widget in the given row, in the given column

        args:
            rowId, (int), required, id of the row the widget is in
            colId, (int), required, id of the column the widget is in

        returns: (QWidget)
        """
        return self.cellWidgets[rowId][colId]

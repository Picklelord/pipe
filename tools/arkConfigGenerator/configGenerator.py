"""
Ark Config File Generator 

I built this to automate the tedious process of modding the Ark:SE server config files.
It allows you to:
    - customize the Supply Drop items
    - override or add creatures to spawn and in which region you want them in


Current State of Tool:
    - Supply Drop is working
    - custom spawning is not working

ToDo: Setup Spawn Code!! 


Future Features:
    - add "Save to File" button instead of require copying

"""
import sys
import os
import importlib
from Qt import QtWidgets as QtWid
from QtUtils import styles
from functools import partial
from utils import dataUtils
from QtUtils.widgets import mainWindows as MW
from QtUtils.widgets import dynamicWidgetTable as DWT

importlib.reload(MW)
importlib.reload(DWT)

BOOL_OPTIONS = ["True", "False"]
ROOT = __file__.rsplit("\\", 1)[0]

ITEMS = dataUtils.readJson("{}\\itemId.json".format(ROOT))
CREATURES = dataUtils.readJson("{}\\creatures.json".format(ROOT))
SPAWNREGIONS = dataUtils.readJson("{}\\spawnRegions.json".format(ROOT))


class ConfigGenUI(MW.TabWindow):
    def load(self):
        """ loads all required data and shows the Config Generator UI """
        print("Loading")

        kwargs = {
            "title": "Ark Config Generator",
            "layoutType": "vertical",
            "tabLayoutType": "vertical",
            "left": -400,
            "height": 900,
            "width": 900,
        }
        self.initUI(**kwargs)
        styles.setStyle("default", self)

        self.windowHeaderRow = QtWid.QHBoxLayout(self)
        self.mapLabel = QtWid.QLabel("Server Map: ")
        self.mapCombo = QtWid.QComboBox()
        self.mapCombo.addItems(SPAWNREGIONS.keys())
        self.windowHeaderRow.addWidget(self.mapLabel)
        self.windowHeaderRow.addWidget(self.mapCombo)
        self.mainLayout.insertLayout(0, self.windowHeaderRow)

        self.setupSupplyDropTab()

        self.setupSpawnTab()

        self.show()

    def setupSupplyDropTab(self):
        """ Sets up the Supply Drop UI Tab interface parts """
        self.addTab("CSD", "Custom Supply Drop")

        self.sdFirstRow = QtWid.QHBoxLayout()
        self.minItemsLabel = QtWid.QLabel("Min Item Sets Spawn:")
        self.minItemsLabel.setObjectName("tabBG")
        self.sdFirstRow.addWidget(self.minItemsLabel)
        self.minItemsSpin = QtWid.QSpinBox()
        self.minItemsSpin.setValue(1)
        self.sdFirstRow.addWidget(self.minItemsSpin)
        self.maxItemsLabel = QtWid.QLabel("Max Item Sets Spawn:")
        self.maxItemsLabel.setObjectName("tabBG")
        self.sdFirstRow.addWidget(self.maxItemsLabel)
        self.maxItemsSpin = QtWid.QSpinBox()
        self.maxItemsSpin.setValue(1)
        self.sdFirstRow.addWidget(self.maxItemsSpin)
        self.tabs["CSD"]["layout"].addLayout(self.sdFirstRow)

        self.sdSecondRow = QtWid.QHBoxLayout()
        self.sDropLabel = QtWid.QLabel("SupplyDrop:")
        self.sDropLabel.setObjectName("tabBG")
        self.sdSecondRow.addWidget(self.sDropLabel)
        self.sdText = QtWid.QLineEdit()
        self.sdText.setMaximumWidth(400)
        self.sdSecondRow.addWidget(self.sdText)
        self.addSetBtn = QtWid.QPushButton("Add New Item Set")
        self.addSetBtn.clicked.connect(partial(self.addSupplyDropSetRow))
        self.sdSecondRow.addWidget(self.addSetBtn)
        self.addItemBtn = QtWid.QPushButton("Add Item To Current Set")
        self.addItemBtn.clicked.connect(partial(self.addSupplyDropItemRow))
        self.sdSecondRow.addWidget(self.addItemBtn)
        self.tabs["CSD"]["layout"].addLayout(self.sdSecondRow)

        self.sdTableRow = QtWid.QHBoxLayout()
        self.tabs["CSD"]["layout"].addLayout(self.sdTableRow)

        sdConfigGenKwargs = {
            "numColumns": 10,
            "columnWidths": [130, 200, 70, 70, 70, 70, 70, 0, 70, 60],
            "columnsVisible": [
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
            ],
            "height": 840,
            "width": 900,
            "headers": [
                "Category",
                "Item",
                "Chance",
                "Min Quantity",
                "Max Quantity",
                "Min Quality",
                "Max Quality",
                "Force Blueprint",
                "Blueprint Chance",
                "DEL",
            ],
        }

        self.sdConfigTable = DWT.DynamicTable(self, **sdConfigGenKwargs)
        self.sdTableRow.addWidget(self.sdConfigTable)

        self.sdThirdRow = QtWid.QHBoxLayout()
        self.sdGenCodeBtn = QtWid.QPushButton("Generate Code")
        self.sdGenCodeBtn.clicked.connect(partial(self.generateSupplyDropCode))
        self.sdThirdRow.addWidget(self.sdGenCodeBtn)
        self.sdCodeBox = QtWid.QLineEdit()
        self.sdThirdRow.addWidget(self.sdCodeBox)
        self.tabs["CSD"]["layout"].addLayout(self.sdThirdRow)

    def addSupplyDropSetRow(self):
        """ creates and sets up a new row for a Set on the sdConfigTable """
        data = {"type": "set"}
        rowId = self.sdConfigTable.addRow(data=data)
        row = [
            QtWid.QLabel("New Item Set :"),
            QtWid.QLabel("  "),
            QtWid.QDoubleSpinBox(),
            QtWid.QSpinBox(),
            QtWid.QSpinBox(),
            QtWid.QLabel("  "),
            QtWid.QLabel("  "),
            QtWid.QLabel("  "),
            QtWid.QLabel("  "),
            QtWid.QPushButton("DEL"),
        ]
        row[0].setMinimumWidth(130)
        row[1].setMinimumWidth(200)
        row[2].setValue(30.0)
        row[2].setMinimum(0.01)
        row[2].setMaximum(100.0)
        row[3].setValue(1.0)
        row[4].setValue(1.0)
        row[9].clicked.connect(partial(self.sdConfigTable.removeRow, rowId))
        self.sdConfigTable.addWidgetToRow(rowId, row, 26)

    def addSupplyDropItemRow(self):
        """ creates and sets up a new row for an Item on the sdConfigTable """
        data = {"type": "item"}
        rowId = self.sdConfigTable.addRow(data=data)
        row = [
            QtWid.QComboBox(),
            QtWid.QComboBox(),
            QtWid.QDoubleSpinBox(),
            QtWid.QSpinBox(),
            QtWid.QSpinBox(),
            QtWid.QDoubleSpinBox(),
            QtWid.QDoubleSpinBox(),
            QtWid.QComboBox(),
            QtWid.QDoubleSpinBox(),
            QtWid.QPushButton("DEL"),
        ]
        row[0].addItems(ITEMS.keys())
        row[0].currentIndexChanged.connect(
            partial(self.toggleSupplyDropCategory, rowId)
        )
        row[0].setMinimumWidth(130)
        row[1].setMinimumWidth(200)
        row[2].setValue(30.0)
        row[2].setMinimum(0.01)
        row[2].setMaximum(100.0)
        row[3].setValue(1.0)
        row[3].setMaximum(10000.0)
        row[4].setValue(1.0)
        row[4].setMaximum(10000.0)
        row[5].setValue(1.0)
        row[6].setValue(1.0)
        row[7].addItems(BOOL_OPTIONS)
        row[7].setCurrentIndex(1)
        row[8].setValue(0.3)
        row[2].setMaximumWidth(63)
        row[3].setMaximumWidth(63)
        row[4].setMaximumWidth(63)
        row[5].setMaximumWidth(63)
        row[6].setMaximumWidth(63)
        row[7].setMaximumWidth(80)
        row[8].setMaximumWidth(63)
        row[9].clicked.connect(partial(self.sdConfigTable.removeRow, rowId))
        self.sdConfigTable.addWidgetToRow(rowId, row, 26)
        self.toggleSupplyDropCategory(rowId)

    def toggleSupplyDropCategory(self, rowId):
        """
        replaces the options that are in the given rows Category ComboBox

        Args:
        rowId (int): id of the row that was altered
        """
        catCombo = self.sdConfigTable.cellWidgets[rowId][0]
        itemCombo = self.sdConfigTable.cellWidgets[rowId][1]
        cat = catCombo.currentText()
        print(cat)
        itemCombo.clear()
        itemCombo.addItems(ITEMS[cat].keys())

    def generateSupplyDropCode(self):
        """ 
            Based on the state of the UI fields that the user has set, this will
            generate the line of code that will be added to the config file
        """
        Code = "ConfigOverrideSupplyCrateItems=("
        Code += 'SupplyCrateClassString="{}",MinItemSets={},MaxItemSets={},'.format(
            self.sdText.text(), self.minItemsSpin.value(), self.maxItemsSpin.value()
        )
        Code += "NumItemSetsPower-1.0,bSetsRandomWithoutReplacement=true,ItemSets=("
        rowData = self.sdConfigTable.rows
        cellData = self.sdConfigTable.cellWidgets
        inSet = False
        for rowId in rowData.keys():
            if rowData[rowId]["data"]["type"] == "set":
                if inSet:
                    Code = Code[:-1] + ")),"
                else:
                    inSet = True
                Code += "(MinNumItems={},MaxNumItems={},NumItemsPower=1.0,SetWeight={},".format(
                    cellData[rowId][3].value(),
                    cellData[rowId][4].value(),
                    cellData[rowId][2].value() / 100.0,
                )

                Code += "bItemsRandomWithoutReplacement=true,ItemEntries=("

            if rowData[rowId]["data"]["type"] == "item":
                Code += '(EntryWeight={},ItemClassStrings=("{}"),ItemsWeight=(1.0),MinQuantity={},MaxQuantity={},'.format(
                    cellData[rowId][2].value() / 100.0,
                    ITEMS[cellData[rowId][0].currentText()][
                        cellData[rowId][1].currentText()
                    ],
                    cellData[rowId][3].value(),
                    cellData[rowId][4].value(),
                )
                Code += "MinQuality={},MaxQuality={},bForceBlueprint={},ChanceToBeBlueprintOverride={}),".format(
                    cellData[rowId][5].value(),
                    cellData[rowId][6].value(),
                    cellData[rowId][7].currentText(),
                    cellData[rowId][8].value(),
                )

        Code = Code[:-1] + "))))"
        print(Code)
        self.sdCodeBox.setText(Code)

    def setupSpawnTab(self):
        """ Sets up the Supply Drop UI Tab interface parts """
        self.addTab("CDS", "Custom Dino Spawns")

        self.cdsFirstRow = QtWid.QHBoxLayout()
        typeLabel = QtWid.QLabel("Type:")
        typeLabel.setObjectName("tabBG")
        self.cdsTypeCombo = QtWid.QComboBox()
        self.cdsTypeCombo.addItems(["Add to Default Spawns", "Override Default Spawns"])
        self.cdsAddSpawnBtn = QtWid.QPushButton("Add Spawn Zone")
        self.cdsAddDinoBtn = QtWid.QPushButton("Add Dino to Spawn Zone")
        self.cdsAddSpawnBtn.clicked.connect(partial(self.addSpawnZone))
        self.cdsAddDinoBtn.clicked.connect(partial(self.addDinoToSpawn))
        self.cdsFirstRow.addWidget(typeLabel)
        self.cdsFirstRow.addWidget(self.cdsTypeCombo)
        self.cdsFirstRow.addWidget(self.cdsAddSpawnBtn)
        self.cdsFirstRow.addWidget(self.cdsAddDinoBtn)
        self.tabs["CDS"]["layout"].addLayout(self.cdsFirstRow)

        self.cdsTableRow = QtWid.QHBoxLayout()
        self.tabs["CDS"]["layout"].addLayout(self.cdsTableRow)

        cdsConfigGenKwargs = {
            "numColumns": 6,
            "columnWidths": [0, 0, 0, 100, 100, 60],
            "columnsVisible": [True, True, True, True, True, True],
            "height": 840,
            "width": 900,
            "headers": [
                "Spawn",
                "SpawnName",
                "Dino to Spawn",
                "Spawn Weight",
                "Max Spawns %",
                "DEL",
            ],
        }

        self.cdsConfigTable = DWT.DynamicTable(self, **cdsConfigGenKwargs)
        self.cdsTableRow.addWidget(self.cdsConfigTable)

        self.cdsThirdRow = QtWid.QHBoxLayout()
        self.cdsGenCodeBtn = QtWid.QPushButton("Generate Code")
        self.cdsGenCodeBtn.clicked.connect(partial(self.generateSpawnCode))
        self.cdsThirdRow.addWidget(self.cdsGenCodeBtn)
        self.cdsCodeBox = QtWid.QLineEdit()
        self.cdsThirdRow.addWidget(self.cdsCodeBox)
        self.tabs["CDS"]["layout"].addLayout(self.cdsThirdRow)

    def addSpawnZone(self):
        """ Sets up a new spawn zone row """
        data = {"type": "spawn"}
        rowId = self.cdsConfigTable.addRow(data=data)
        row = [
            QtWid.QComboBox(),
            QtWid.QLabel("  "),
            QtWid.QLabel("  "),
            QtWid.QLabel("  "),
            QtWid.QLabel("  "),
            QtWid.QPushButton("DEL"),
        ]
        row[0].addItems(SPAWNREGIONS[self.mapCombo.currentText()])
        row[5].clicked.connect(partial(self.cdsConfigTable.removeRow, rowId))
        self.cdsConfigTable.addWidgetToRow(rowId, row, 26)

    def addDinoToSpawn(self):
        """ Sets up a new Dino row that will be added to the SpawnZone above it """
        data = {"type": "dino"}
        rowId = self.cdsConfigTable.addRow(data=data)
        row = [
            QtWid.QLabel("  "),
            QtWid.QLineEdit(),
            QtWid.QComboBox(),
            QtWid.QDoubleSpinBox(),
            QtWid.QDoubleSpinBox(),
            QtWid.QPushButton("DEL"),
        ]
        row[1].setPlaceholderText("UniqueNameForThisDino")
        row[2].addItems(CREATURES.keys())
        row[3].setMaximum(99999)
        row[4].setMaximum(100)
        row[4].setSingleStep(0.01)
        row[5].clicked.connect(partial(self.cdsConfigTable.removeRow, rowId))
        self.cdsConfigTable.addWidgetToRow(rowId, row, 26)

    def generateSpawnCode(self):
        """
            Not implemented yet!
            This will generate the line of code to generate the spawnZone and define the
            dino's that will spawn in it.
        """
        pass


if __name__ == "__main__":
    app = QtWid.QApplication(sys.argv)
    cgUI = ConfigGenUI()
    cgUI.load()
    sys.exit(app.exec_())

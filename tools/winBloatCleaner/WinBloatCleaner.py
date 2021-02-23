"""
Windows Bloatware Cleaner

I built this to automate uninstalling all the bloatware that windows 10 automatically 
reinstalls after EVERY windows update (--_--)

It allows you to:
    - automatically uninstall all selected apps
    - create a Scheduled Task that will re-run the selected app uninstallation 


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
import subprocess
from Qt import QtWidgets as QtWid
from QtUtils import styles
from functools import partial
from utils import dataUtils
from QtUtils.widgets import mainWindows as MW
from QtUtils.widgets import dynamicWidgetTable as DWT

importlib.reload(MW)
importlib.reload(DWT)


class WinBloatwareCleaner(MW.Window):
    def load(self):
        print("Loading")

        kwargs = {
            "title": "Windows Bloatware Cleaner",
            "layoutType": "vertical",
            "tabLayoutType": "vertical",
            "left": 400,
            "height": 850,
            "width": 680,
        }
        self.initUI(**kwargs)
        styles.setStyle("default", self)

        tableKwargs = {
            "numColumns": 4,
            "columnWidths": [110, 0, 120, 80],
            "columnsVisible": [True, True, True, True],
            "height": 400,
            "width": 450,
            "headers": ["Type", "Name", "Function", "Run?"],
        }

        self.optionsTable = DWT.DynamicTable(self, **tableKwargs)
        self.mainLayout.addWidget(self.optionsTable)

        self.buttonsRow = QtWid.QHBoxLayout()
        self.cleanBtn = QtWid.QPushButton("Run Cleaner")
        self.cleanBtn.clicked.connect(partial(self.createDataFileAndRun))
        self.buttonsRow.addWidget(self.cleanBtn)
        self.mainLayout.addLayout(self.buttonsRow)

        self.data = {
            # custom Microsoft Edge Uninstall process
            "Forced App Microsoft Edge": {
                "type": "Software",
                "function": "Uninstall",
                "qType": "QCheckBox",
                "command": None,
                "pythonFunc": uninstallMicrofartEdge,
            },
            # Custom task scheduler generation process
            "Create task to repeat these settings": {
                "type": "Task Scheduler",
                "function": "Add Task",
                "qType": "QComboBox",
                "qOptions": [
                    "Don't Create",
                    "HOURLY",
                    "DAILY",
                    "WEEKLY",
                    "MONTHLY",
                    "ONLOGON",
                ],
                "command": None,
                "pythonFunc": createTask,
            },
        }
        dataFile = "{}\\genericTasks.json".format(os.path.dirname(__file__))
        genericTasksData = dataUtils.readJson(dataFile)
        self.data.update(genericTasksData)

        self.addOptions()
        self.show()
        print(__file__)

    def createDataFileAndRun(self):
        print("clean")
        dataFile = "{}\\selectedOptions.json".format(os.path.dirname(__file__))
        data = {}
        for rowId in self.optionsTable.rows:
            rowKey = self.optionsTable.cellWidgets[rowId][1].text()
            data.update({rowKey: self.data[rowKey]})

        dataUtils.writeJson(data, dataFile)

        runBloatwareCleanup(True)

    def addOptions(self):
        for name in self.data.keys():
            rowId = self.optionsTable.addRow()
            row = [
                QtWid.QLabel(),
                QtWid.QLabel(),
                QtWid.QLabel(),
                eval("QtWid.{}()".format(self.data[name]["qType"])),
            ]
            if self.data[name]["qType"] == "QComboBox":
                row[3].addItems(self.data[name]["qOptions"])
            else:
                row[3].setStyleSheet(
                    "QCheckBox::indicator { width: 70px; height: 23px;}"
                )  # .setObjectName("large")
            row[0].setText(self.data[name]["type"])
            row[1].setText(name)
            row[2].setText(self.data[name]["function"])

            self.optionsTable.addWidgetToRow(rowId, row, 26)
        """
        Click the Start button, type cmd, right-click Command Prompt and select Run as administrator
        Type C:\Program Files (x86)\Microsoft\Edge\Application\83.0.478.58\Installer and press Enter
        Type setup.exe --uninstall --system-level --verbose-logging --force-uninstall and press Enter

        @rem Remove Apps
        create task Scheduler task to run this each week?
        """


def runBloatwareCleanup(removeTaskScheduler=False):
    dataFile = "{}\\selectedOptions.json".format(os.path.dirname(__file__))
    data = dataUtils.readJson(dataFile)
    for taskName in data:
        if taskData["command"]:
            print("running: ", data["command"])
            subprocess.popen(data["command"])
        else:
            eval("{}()".format(data["pythonFunc"]))

    if "Create task to repeat these settings" in data.keys():
        data.pop("Create task to repeat these settings", None)
        dataUtils.writeJson(data, dataFile)


def uninstallMicrofartEdge():
    print("uninstall Microfart Edge")
    appDefaultDir = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\"
    folders = os.listdir(appDefaultDir)
    for folder in folders:
        cmd = "cd {}\\Installer\\{}".format(appDefaultDir, folder)
        if os.path.exists(cmd[3:]):
            cmd += ";setup.exe --uninstall --system-level --verbose-logging --force-uninstall"
            os.system(cmd)
            time.sleep(10)


def createTask(option):
    print("create Task")
    # option = self.optionsTable.cellWidgets[rowId][3].currentText()
    taskRunCommand = "python.exe {}".format(__file__)
    cmd = "schtasks.exe /Create /U {user} /SC {opt} /TN {tn} /TR {tr}".format(
        user=os.environ["USER"],
        opt=option,
        tn='"Bloatware Cleaner ReRun"',
        tr=taskRunCommand,
    )

    os.system(cmd)


if __name__ == "__main__":
    app = QtWid.QApplication(sys.argv)
    cgUI = WinBloatwareCleaner()
    cgUI.load()
    sys.exit(app.exec_())

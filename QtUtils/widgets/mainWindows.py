from Qt import QtWidgets as QtWid


class Window(QtWid.QMainWindow):
    def __init__(sf):
        super(Window, sf).__init__()

    def initUI(sf, **kwargs):
        """
        initialises the UI and sets up base UI elements for a Window with a tab Widget

        kwargs: title,            (str),      title text for the UI
        kwargs: left,             (int),      UI default position left point
        kwargs: top,              (int),      UI default position top point
        kwargs: width,            (int),      UI default width
        kwargs: height,           (int),      UI default height
        kwargs: setCentralWidget, (bool),     if true will set the main widget as the central widget
        kwargs: setMainWidget,    (QWidget),  pass your QWidget to be used as the main widget
        kwargs: layoutType,       (str enum), sets layout type: vertical or horizontal
        kwargs: menu,             (bool),     if true will add a menuBar to the UI
        kwargs: statusBar,        (bool),     if true will add a statusBar to the UI

        """
        title = kwargs.pop("title", "TITLE MISSING!")
        left = kwargs.pop("left", 0)
        top = kwargs.pop("top", 0)
        initwidth = kwargs.pop("width", 290)
        initheight = kwargs.pop("height", 80)
        setCentralWidget = kwargs.pop("setCentralWidget", True)
        setMainWidget = kwargs.pop("setMainWidget", QtWid.QWidget(sf))
        layoutType = kwargs.pop("layoutType", "vertical")
        menuBool = kwargs.pop("menu", False)
        statusBarBool = kwargs.pop("statusBar", False)

        sf.setWindowTitle(title)
        sf.setObjectName(title.replace(" ", "_"))
        sf.setMinimumSize(initwidth, initheight)
        if menuBool:
            sf.menubar = sf.menuBar()

        if statusBarBool:
            sf.statusbar = sf.statusBar()

        sf.main = setMainWidget
        if setCentralWidget:
            sf.setCentralWidget(sf.main)

        if layoutType:
            if layoutType == "vertical":
                sf.mainLayout = QtWid.QVBoxLayout(sf)

            elif layoutType == "horizontal":
                sf.mainLayout = QtWid.QHBoxLayout(sf)
            sf.main.setLayout(sf.mainLayout)

    def run(sf):
        """runs/shows the UI"""
        sf.show()


class TabWindow(QtWid.QMainWindow):
    def __init__(sf):
        super(TabWindow, sf).__init__()

    def initUI(sf, **kwargs):
        """
        initialises the UI and sets up base UI elements for a Window with a tab Widget

        kwargs: title,            (str),      title text for the UI
        kwargs: left,             (int),      UI default position left point
        kwargs: top,              (int),      UI default position top point
        kwargs: width,            (int),      UI default width
        kwargs: height,           (int),      UI default height
        kwargs: setCentralWidget, (bool),     if true will set the main widget as the central widget
        kwargs: setMainWidget,    (QWidget),  pass your QWidget to be used as the main widget
        kwargs: layoutType,       (str enum), sets layout type: vertical or horizontal
        kwargs: tabLayoutType,    (str enum), sets tab page layout type: vertical or horizontal
        kwargs: menu,             (bool),     if true will add a menuBar to the UI
        kwargs: statusBar,        (bool),     if true will add a statusBar to the UI

        """
        title = kwargs.pop("title", "TITLE MISSING!")
        left = kwargs.pop("left", 200)
        top = kwargs.pop("top", 200)
        initwidth = kwargs.pop("width", 290)
        initheight = kwargs.pop("height", 80)
        setCentralWidget = kwargs.pop("setCentralWidget", True)
        setMainWidget = kwargs.pop("setMainWidget", QtWid.QWidget(sf))
        layoutType = kwargs.pop("layoutType", "vertical")
        sf.tabLayoutType = kwargs.pop("tabLayoutType", "vertical")
        menuBool = kwargs.pop("menu", False)
        statusBarBool = kwargs.pop("statusBar", False)
        setMinimumSizeBool = kwargs.pop("setMinimumSize", True)

        sf.setWindowTitle(title)
        sf.setObjectName(title.replace(" ", "_"))
        if setMinimumSizeBool:
            sf.setMinimumSize(initwidth, initheight)
        sf.setGeometry(left, top, initwidth, initheight)
        if menuBool:
            sf.menubar = sf.menuBar()

        if statusBarBool:
            sf.statusbar = sf.statusBar()

        sf.main = setMainWidget
        if setCentralWidget:
            sf.setCentralWidget(sf.main)

        if layoutType:
            if layoutType == "vertical":
                sf.mainLayout = QtWid.QVBoxLayout(sf)

            elif layoutType == "horizontal":
                sf.mainLayout = QtWid.QHBoxLayout(sf)
            sf.main.setLayout(sf.mainLayout)
        sf.tabWidget = QtWid.QTabWidget()
        sf.mainLayout.addWidget(sf.tabWidget)
        sf.tabs = {}
        sf.tabIdToKey = {}

    def run(sf):
        """runs/shows the UI"""
        sf.show()

    def addTab(sf, key="dft", name="default", widget=QtWid.QWidget):
        """
        adds a new tab and creates the base widget and layout

        args:
            key, (str), optional, this is the key that will be used to access it in the tabs dict
            name, (str), optional, this is the title of the tab, shown in the UI
            widget, (QWidget), optional, this is the main widget that is used in the Tab Page

        returns: sf.tabs[key], the tabs UI elements dict

        """
        if key not in sf.tabs:
            sf.tabs[key] = {}
        sf.tabs[key]["widget"] = widget()
        sf.tabs[key]["widget"].setObjectName("tabBG")
        sf.tabs[key]["tabId"] = sf.tabWidget.addTab(sf.tabs[key]["widget"], name)
        sf.tabIdToKey[sf.tabs[key]["tabId"]] = key
        if sf.tabLayoutType == "vertical":
            sf.tabs[key]["layout"] = QtWid.QVBoxLayout()
        else:
            sf.tabs[key]["layout"] = QtWid.QHBoxLayout()
        sf.tabs[key]["widget"].setLayout(sf.tabs[key]["layout"])
        return sf.tabs[key]

    def removeTab(sf, key):
        """
        Removes the given tab from the UI and data dict
        """
        sf.tabWidget.removeTab(sf.tabs[key]["tabId"])
        sf.tabs[key]["layout"].deleteLater()
        sf.tabs[key]["widget"].deleteLater()
        del sf.tabs[key]["layout"]
        del sf.tabs[key]["widget"]
        sf.tabs[key] = {}
        sf.tabIdToKey[sf.tabs[key]["tabId"]] = None

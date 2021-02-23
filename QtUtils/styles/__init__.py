import os
import json


def setStyle(styleName, ui):
    styleDir = os.path.dirname(__file__)

    with open("{}/{}.qss".format(styleDir, styleName), "r") as sf, open(
        "{}/{}Vars.json".format(styleDir, styleName), "r"
    ) as jf:
        strStyle, vData = sf.read(), json.load(jf)
        for var in vData:
            value = vData[var]
            if "IMAGE_DIR" in value:
                value = value.replace(
                    "IMAGE_DIR", __file__.rsplit("\\", 2)[0] + "\\images\\"
                )
            strStyle = strStyle.replace(var, value)
        ui.setStyleSheet(strStyle)

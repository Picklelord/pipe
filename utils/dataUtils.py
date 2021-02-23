import json
import os


def appendJson(data, jsonFile):
    """
    Adds data to existing data from the given json file
    If keys exist in the current file, they will be overwritten!

    Args:
    data (dict): Data to Write jsonFile (str): /full/path/including/file.json

    Returns:
    (bool): True if it was successful
    """
    if not os.path.exists(os.path.dirname(jsonFile)):
        os.makedirs(os.path.dirname(jsonFile))

    oldData = readJson(jsonFile)
    if oldData:
        oldData.update(data)
        newData = oldData
    else:
        newData = data

    with open(jsonFile, "wa") as f:
        json.dump(newData, f, Indent=4)

    return True


def writeJson(data, jsonFile):
    """
    Writes give data to given 1son file

    Args:
        data (dict): Data to Write jsonFile (str): /full/path/including/file.json

    Returns:
        (bool): True if it was successful
    """
    if not os.path.exists(os.path.dirname(jsonFile)):
        os.makedirs(os.path.dirname(jsonFile))

    with open(jsonFile, "w") as f:
        json.dump(data, f, indent=4)

    return True


def readJson(jsonFile, returnEmpty=True):
    """
    Reads data from Json

    Args:
        jsonFile (str): /full/path/including/file.json

    Returns:
        (dict): Data found in the file, or None if fle did not exist
    """
    if not os.path.exists(jsonFile):
        if returnEmpty:
            return {}
        return False

    with open(jsonFile, "r") as f:
        data = json.load(f)
    return data

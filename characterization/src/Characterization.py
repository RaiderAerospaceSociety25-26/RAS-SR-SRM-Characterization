# ------------------ IMPORT ----------------
import pandas as pd
from TestFire import TestFire


# ----------------------------- GLOBAL VARIABLES ----------------------------
configFilename = '../dat/test_config.txt' #INPUT: MUST SET THIS FILENAME TO THE NAME OF THE CONFIGURATION FILE
dataFilenameBase = '../dat/' #filename for the Excel sheet; leave as a blank string except for any required prefix
testFires = [] #array to use to hold TestFire objects


# ---------------- READ DATA AND CREATE TESTFIRE OBJECTS ------------------------
def throwParseError():
    print("There is a configuration file formatting problem.")
    raise SystemExit(1)

def readImportOptions():
    #read import options from .txt file
    configFile = open(configFilename, 'r') #open config file to read
    configLines = [] #define array to store the config file data
    configLinesEdited = [] #define array (2D) to store the edited config file data
    i = 0
    for line in configFile:
        configLines.append(line.strip()) #add each file line to the configLines array
    configFile.close() #close file
    startIndices = []
    endIndices = []
    i = 0
    for line in configLines:
        if line == "!CONFIGSTART": startIndices.append(i) #index of the array where "!CONFIGSTART" is stored
        if line == "!CONFIGEND": endIndices.append(i) #index of the array where "!CONFIGEND" is stored
        i += 1
    if (len(startIndices) != len(endIndices)) or (len(startIndices) == 0) or (len(endIndices) == 0): throwParseError()
    for j in range(len(startIndices)):
        configLinesEdited.append(configLines[startIndices[j]+1:endIndices[j]]) #stores the configuration data without the !CONFIGSTART and !CONFIGEND tags
    #results in configLines being an array of strings with each element being a line of the file
    return configLinesEdited

#creates each TestFire object and sets the import options for each using the allConfigs array
def setImportOptions(allConfigs):
    for x in range(len(allConfigs)):
        fileEntry = allConfigs[x][0].split(" ")
        geomEntry = allConfigs[x][1].split(" ")
        throatEntry = allConfigs[x][2].split(" ")
        arr = []
        for y in range(len(throatEntry)-2): #for each fire, set filename, pressure units, thrust units, geometry units, geometry, throat units, and throat
            testFire = TestFire()
            testFire.set_fireIndex(y)
            if (fileEntry[0] == "filename"):
                testFire.set_filename(fileEntry[1])
                #set sheetnames
                excelFile = pd.ExcelFile(dataFilenameBase + testFire.get_filename()) #define pandas ExcelFile object
                sheetnames = excelFile.sheet_names #get sheet names (and by proxy number of sheets) in Excel workbook
                testFire.set_sheetnames(sheetnames)
                testFire.set_pressUnits(fileEntry[2])
                testFire.set_thrustUnits(fileEntry[3])
            else: throwParseError()
            if (geomEntry[0] == "geometry"):
                testFire.set_geomUnits(geomEntry[1])
                geometryArr = geomEntry[2].split("||")
                geometryArrFinal = []
                for list in geometryArr:
                    numArr = []
                    for num in list.split(","):
                        numArr.append(num)
                    geometryArrFinal.append(numArr)
                testFire.set_geometry(geometryArrFinal) #geometry array is of the format [[grain length, core diameter, grain OD]] from forwardmost grain to aftmost grain
            else: throwParseError()
            if(throatEntry[0] == "throat"):
                testFire.set_throatUnits(throatEntry[1])
                testFire.set_throat(float(throatEntry[y+2]))
            else: throwParseError()
            arr.append(testFire)
        testFires.append(arr)

#reads data from Excel and adds it to each TestFire object
def readExcelData(allConfigs):
    x = 0
    for tfList in testFires:
        y = 0
        for tf in tfList:
            tfObj = testFires[x][y]
            testFires[x][y].set_dat(pd.read_excel((dataFilenameBase + tfObj.get_filename()), tfObj.get_sheetnames()[y]))
            y += 1
        x += 1


# --------------------- CHARACTERIZATION --------------------------
#start characterization functions here
def characterization():
    pass


# --------------------- MAIN ---------------------
def printAllTestFireListAttributes():
    x = 0
    for tfList in testFires:
        y = 0
        for tf in tfList:
            TestFire.printAllAttributes(tf)
            y += 1
        x += 1

def main():
    #import data
    allConfigs = readImportOptions()
    setImportOptions(allConfigs)
    readExcelData(allConfigs)
    printAllTestFireListAttributes()

    #characterization calculations
    #start here



main()
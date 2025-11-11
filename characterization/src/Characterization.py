#import statements
import pandas as pd
from enum import Enum
import TestFire


#global variables
configFilename = '../dat/test_config.txt' #INPUT: MUST SET THIS FILENAME TO THE NAME OF THE CONFIGURATION FILE
dataFilename = '../dat/test_data.xlsx' #filename for the Excel sheet; leave blank!
testFires = [] #array to use to hold TestFire objects


#read data from Excel file
excelFile = pd.ExcelFile(dataFilename) #define pandas ExcelFile object
sheetnames = excelFile.sheet_names #get sheet names (and by proxy number of sheets) in Excel workbook
#dataArr = [] #define array for the DataFrame objects to be added to
i = 0
for sn in sheetnames: #iterates through each sheet
    testFires.append(TestFire.TestFire())
    testFires[i].set_dat(pd.read_excel(dataFilename, sn))
    testFires[i].set_fireIndex(i)
    print(testFires[i].get_dat())
    i += 1
#results in dataArr being an array of DataFrame objects, with each DataFrame object being the result of reading a sheet from the Excel workbook


#read import options from .txt file
configFile = open(configFilename, 'r') #open config file to read
configLines = [] #define array to store the config file data
i = 0
for line in configFile:
    configLines.append(line.strip()) #add each file line to the configLines array
configFile.close() #close file
print(configLines)
#results in configLines being an array of strings with each element being a line of the file


#parse config file
#for line in configLines:
#    if (line == "!CONFIGSTART"):


def throwParseError():
    print("Configuration file formatting error.")
    raise SystemExit(1)





# ------------------ IMPORT ----------------
import pandas as pd
from TestFire import TestFire
from Calculation import Calculation
from scipy.optimize import fsolve
import numpy as np
import math


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
        massEntry = allConfigs[x][3].split(" ")
        densityEntry = allConfigs[x][4].split(" ")
        arr = []
        for y in range(len(throatEntry)-2): #for each fire, set filename, pressure units, thrust units, geometry units, geometry, throat units, and throat
            testFire = TestFire()
            testFire.set_fireIndex(y)
            if (fileEntry[0] == "filename"):
                testFire.set_filename(fileEntry[1])
                #set sheetnames
                excelFile = pd.ExcelFile(dataFilenameBase + testFire.get_filename()) #define pandas ExcelFile object
                sheetnames = excelFile.sheet_names #get sheet names in Excel workbook
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
            if(massEntry[0] == "mass"):
                testFire.set_massUnits(massEntry[1])
                testFire.set_mass(float(massEntry[y+2]))
            else: throwParseError()
            if(densityEntry[0] == "density"):
                testFire.set_densityUnits(densityEntry[1])
                testFire.set_density(float(densityEntry[y+2]))
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
#take the data associated with each TestFire object and do necessary conversions and calculations to define a Calculation object, adding it to the TestFire object
#a Calculation object contains all the data necessary for characterization. in addition, all data is in metric units so there is no unit confusion during the characterization calculations.
def conversionsAndDefinitions():
    x = 0
    for tfList in testFires:
        y = 0
        for tf in tfList:
            data = testFires[x][y].get_dat()

            #burn_time
            burn_time = data.iloc[len(data.iloc[:,0])-1,0]

            #time
            time = data.iloc[:,0]

            #pressure
            if (tf.get_pressUnits() == "psig"): press = data.iloc[:,1]*6894.76 #convert psi to Pa
            elif (tf.get_pressUnits() == "kPa"): press = data.iloc[:,1]*1000 #convert kPa to Pa
            else: throwParseError()
            
            #thrust
            if (tf.get_thrustUnits() == "N"): thrust = data.iloc[:,2]
            elif (tf.get_thrustUnits() == "lbf"): thrust = data.iloc[:,2]*4.44822 #convert lbf to N
            else: throwParseError()

            #mass
            if (tf.get_thrustUnits() == "N"): mass = tf.get_mass()
            elif (tf.get_massUnits() == "lb"): mass = tf.get_mass()*0.453592 #convert lbm to kg
            else: throwParseError()

            #density
            if (tf.get_densityUnits() == "kg/m3"): density = tf.get_density()
            elif (tf.get_densityUnits() == "lb/in3"): density = tf.get_density()*27679.9 #convert lbm/in^3 to kg/m^3
            else: throwParseError()
            
            #throat_area
            if (tf.get_throatUnits() == "m"): throat_area = math.pi*(math.pow(tf.get_throat(),2)/4)
            elif (tf.get_throatUnits() == "in"): throat_area = math.pi*(math.pow((tf.get_throat()*0.0254),2)/4) #convert to m^2
            else: throwParseError()

            #grain_length
            grain_len = []
            for grain in tf.get_geometry():
                if (tf.get_geomUnits() == "m"): grain_len.append(float(grain[0]))
                elif (tf.get_geomUnits() == "in"): grain_len.append(float(grain[0])*0.0254) #convert to m
                else: throwParseError()

            #grain_init_core
            grain_init_core = []
            for grain in tf.get_geometry():
                if (tf.get_geomUnits() == "m"): grain_init_core.append(float(grain[1]))
                elif (tf.get_geomUnits() == "in"): grain_init_core.append(float(grain[1])*0.0254) #convert to m
                else: throwParseError()

            #grain_OD
            grain_OD = []
            for grain in tf.get_geometry():
                if (tf.get_geomUnits() == "m"): grain_OD.append(float(grain[2]))
                elif (tf.get_geomUnits() == "in"): grain_OD.append(float(grain[2])*0.0254) #convert to m
                else: throwParseError()

            #impulse
            impulse = np.trapezoid(thrust, time)

            #press_integral
            press_integral = np.trapezoid(press, time)

            #c_star
            c_star = (throat_area/mass)*press_integral

            #isp
            isp = impulse/mass

            #make Calculation object
            calc = Calculation(time, press, thrust, mass, density, throat_area, grain_len, grain_init_core, grain_OD, burn_time, impulse, press_integral, c_star, isp)
            testFires[x][y].set_calculation(calc)

            #increment i
            y += 1
        x += 1


#function to perform all characterization calculations
#probably use either scipy.optimize.root_scalar() or scipy.optimize.fsolve()
def characterization():
    """
    function arguments:
    ds: instantaneous change in surface regression (variable that is changed to solve the equation)
    D: grain outer diameter
    d_0: grain initial core diameter
    L_0 = grain initial length
    rho_b = propellant density
    A_t = throat area
    dt = time step
    P = instantaneous pressure
    s_prev = the s value for the previous iteration of the function
    c_star = C*
    """
    def characterizationEqns(ds, D, d_0, L_0, rho_b, A_t, dt, P, s_prev, c_star):
        """
        additional variables:
        A_b = instantaneous burn area
        s = surface regression amount
        """
        #note: not exactly sure how to take into account changing the number of grains (bc that would require parameterizing the equation?). I'm sure there's a way to do it though.
        s = s_prev + ds
        A_b = 0.0
        i = 0
        for num in D:
            A_b += math.pi*((0.5*(math.pow(D[i],2))-math.pow((d_0[i]+(2*s)),2) + (L_0[i]-(2*s))*(d_0[i]+(2*s)))) #SOMETHING IS THROWING AN ARRAY-RELATED ERROR HERE!!!
            i += 1
        #print(A_b)
        zero_func = ds - ((A_t*P*dt)/(A_b*rho_b*c_star))
        return zero_func

    x = 0
    for tfList in testFires:
        y = 0
        for tf in tfList:
            calc = testFires[x][y].get_calculation()
            dsArr = [] #array for ds
            sArr = [] #array for s
            i = 0
            for line in calc.get_time():
                s_initial = 0.001 #initial guess for s
                D = calc.get_grain_OD()
                d_0 = calc.get_grain_init_core()
                L_0 = calc.get_grain_len()
                rho_b = calc.get_density()
                A_t = calc.get_throat_area()
                dt = 0
                s_prev = 0
                if (i != 0):
                    dt = calc.get_time().iloc[i] - calc.get_time().iloc[i-1]
                    s_prev = sArr[i-1]
                P = calc.get_press().iloc[i] # instantaneous pressure
                c_star = calc.get_c_star()
                if (i != 0):
                    ds_new = fsolve(characterizationEqns, s_initial, args=(D, d_0, L_0, rho_b, A_t, dt, P, s_prev, c_star))
                    #print("solved")
                    dsArr.append(float(ds_new))
                    sArr.append(sArr[i-1] + float(ds_new))
                else:
                    sArr.append(0)
                    dsArr.append(0)
                i += 1
            print(sArr)
            print(dsArr)
            y += 1
        x += 1


#function to perform conversions of important output data back to imperial and output to an Excel sheet
def output():
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
    conversionsAndDefinitions()
    characterization()


main()
# ------------------ IMPORT ----------------
import os
import pandas as pd
from TestFire import TestFire
from Calculation import Calculation
from scipy.optimize import fsolve
import numpy as np
import math
import matplotlib.pyplot as plt
import openpyxl
from openpyxl import Workbook

# ----------------------------- GLOBAL VARIABLES ----------------------------
configFilename = '../dat/test_config.txt' #INPUT: MUST SET THIS FILENAME TO THE NAME OF THE CONFIGURATION FILE
dataFilenameBase = '../dat/' #filename base for the Excel sheet; leave as a blank string except for any required prefix (default: '../dat/')
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
    if (len(startIndices) != len(endIndices)) or (len(startIndices) == 0) or (len(endIndices) == 0): throwParseError() #this means that the number of !CONFIGSTART or !CONFIGEND entries is wrong
    for j in range(len(startIndices)):
        configLinesEdited.append(configLines[startIndices[j]+1:endIndices[j]]) #stores the configuration data without the !CONFIGSTART and !CONFIGEND tags
    #results in configLinesEdited being an array of an array of strings with each string element being a line of options
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
                testFire.set_geometry(geometryArrFinal) #geometry array is of the format [[grain length, core diameter, grain OD], [grain length, core diameter, grain OD]] from forwardmost grain to aftmost grain
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

            #make Calculation object and add it to the proper TestFire object
            calc = Calculation(time, press, thrust, mass, density, throat_area, grain_len, grain_init_core, grain_OD, burn_time, impulse, press_integral, c_star, isp)
            testFires[x][y].set_calculation(calc)

            #increment
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
        s = s_prev + ds
        A_b = 0.0
        i = 0
        for num in D:
            A_b += math.pi*((0.5*((math.pow(D[i],2))-math.pow((d_0[i]+(2*s)),2)) + (L_0[i]-(2*s))*(d_0[i]+(2*s)))) #SOMETHING IS THROWING AN ARRAY-RELATED ERROR HERE!!!
            i += 1
        zero_func = ds - ((A_t*P*dt)/(A_b*rho_b*c_star))
        #print(zero_func)
        return zero_func

    x = 0
    for tfList in testFires:
        y = 0
        for tf in tfList:
            calc = testFires[x][y].get_calculation()
            dsArr = [] #array for ds
            sArr = [] #array for s
            A_bArr = [] #array for A_b
            ds_dt_arr = [] #array for ds/dt
            i = 0
            for line in calc.get_time():
                s_initial = 0.05 #initial guess for s
                D = calc.get_grain_OD()
                d_0 = calc.get_grain_init_core()
                L_0 = calc.get_grain_len()
                rho_b = calc.get_density()
                A_t = calc.get_throat_area()
                P = calc.get_press().iloc[i] # instantaneous pressure
                c_star = calc.get_c_star()
                dt = 0
                s_prev = 0
                if (i != 0):
                    dt = calc.get_time().iloc[i] - calc.get_time().iloc[i-1]
                    s_prev = sArr[i-1]
                    ds_new = fsolve(characterizationEqns, s_initial, args=(D, d_0, L_0, rho_b, A_t, dt, P, s_prev, c_star))
                    dsArr.append(float(ds_new))
                    sArr.append(sArr[i-1] + float(ds_new))
                    ds_dt_arr.append(float(ds_new/dt))
                else:
                    sArr.append(0)
                    dsArr.append(0)
                    ds_dt_arr.append(0)
                A_b = 0.0
                j = 0
                for num in D:
                    A_b += math.pi*((0.5*(math.pow(D[j],2))-math.pow((d_0[j]+(2*sArr[i])),2)) + ((L_0[j]-(2*sArr[i]))*(d_0[j]+(2*sArr[i])))) #SOMETHING IS THROWING AN ARRAY-RELATED ERROR HERE!!!
                    j += 1
                A_bArr.append(A_b)
                i += 1
            #add s, ds, A_b, and ds/dt to the calculation object
            testFires[x][y].get_calculation().set_A_bArr(A_bArr)
            testFires[x][y].get_calculation().set_sArr(sArr)
            testFires[x][y].get_calculation().set_dsArr(dsArr)
            testFires[x][y].get_calculation().set_ds_dtArr(ds_dt_arr)
            # print("sArr:")
            # print(sArr)
            # print("dsArr:")
            # print(dsArr)
            # print("A_bArr:")
            # print(A_bArr)
            # print("ds/dt:")
            # print(ds_dt_arr)
            y += 1
        x += 1

#function to perform conversions of important output data back to imperial and output to an Excel sheet
def outputResults():
    """
    figures to output (in both sets of units):
    thrust vs time and pressure vs time
    burn rate vs time and burn area vs time
    
    columns to output to excel sheet (original):
    time (original)
    thrust (original)
    pressure (original)

    more columns to output to excel sheet (from Calculation object, in both sets of units):
    time
    thrust
    pressure
    s
    ds
    A_b
    ds/dt

    additional info to output to excel sheet (in both sets of units):
    grain info: outer diameters, initial core diameters, grain initial lengths
    propellant density
    propellant mass
    throat diameter
    throat area
    pressure integral
    thrust integral
    C*
    ISP
    """
    #create folder for output files:
    #make "out1", "out2", etc., but back one folder, so you'll have three folders: "src", "dat", and "out1" after running
    outputFolderNum = 1
    outputFileBase = "../out/out"
    outputFileDir = ""
    while os.path.exists(outputFileBase + str(outputFolderNum)):
        outputFolderNum += 1
    outputFileDir = outputFileBase + str(outputFolderNum)
    os.makedirs(outputFileDir)

    x = 0
    for tfList in testFires:
        #create Excel file and ExcelWriter object
        wb = Workbook()
        file_path = outputFileDir + "/out"+str(x)+".xlsx"
        wb.save(file_path)
        excelWriter = pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') #REQUIRES OPENPYXL LIBRARY!!!

        #lists for average pressure and average burn rate for characterization
        avgPress = []
        avgBurnrate = []

        y = 0
        for tf in tfList:
            calc = testFires[x][y].get_calculation()
            outputFileBase2 = outputFileDir + "/" + str(x) + "," + str(y) + "_"

            time = calc.get_time() #sec
            thrust = calc.get_thrust() #N
            press = calc.get_press()/1000000 #convert to MPa
            s = calc.get_sArr()
            ds = calc.get_dsArr()
            A_b = calc.get_A_bArr()
            ds_dt = [i * 1000 for i in calc.get_ds_dtArr()] #convert to mm/sec
            thrust_imperial = calc.get_thrust()*0.224809 #convert to lbf
            press_imperial = calc.get_press()*0.000145038 #convert to psig
            s_imperial = [i * 39.3701 for i in calc.get_sArr()] #convert to inches
            ds_imperial = [i * 39.3701 for i in calc.get_dsArr()] #convert to inches
            A_b_imperial = [i * 1550.0031 for i in calc.get_A_bArr()] #convert to in^2
            ds_dt_imperial = [i * 39.3701 for i in calc.get_ds_dtArr()] #convert to in/sec
            #note that everything other than time, thrust, pressure is in an array. time, thrust, and pressure are in DataFrames.

            #TODO: DEFINE ALL EXTRA DATA LIKE PRESSURE AND THRUST INTEGRALS, C*, ISP, ETC. SO THEY CAN BE WRITTEN TO EXCEL FILE TOO
            #also calculate average pressure and average thrust and add it to the arrays

            #thrust vs time and pressure vs time (metric)
            fig, ax1 = plt.subplots(figsize=(13, 8))
            #plot thrust
            ax1.plot(time, thrust, marker='o', linestyle='-', color="b", label="Thrust")
            ax1.set_xlabel("Time (sec)")
            ax1.set_ylabel("Thrust (N)")
            handles1, labels1 = ax1.get_legend_handles_labels()
            #plot pressure
            ax2 = ax1.twinx() #creates another axis that shares the x-axis
            ax2.plot(time, press, marker='^', linestyle='-', color="r", label="Pressure")
            ax2.set_ylim(top=max(press)*1.6) #sets max for the ylim to be a bit higher
            ax2.set_ylabel("Pressure (MPa)")
            handles2, labels2 = ax2.get_legend_handles_labels()
            #show
            #plt.legend(ax1, ax2)
            all_handles = handles1 + handles2
            all_labels = labels1 + labels2
            plt.legend(all_handles, all_labels)
            plt.savefig(outputFileBase2 + "_thrust-pressure_metric")
            plt.close()

            #thrust vs time and pressure vs time (imperial)
            fig, ax1 = plt.subplots(figsize=(13, 8))
            #plot thrust
            ax1.plot(time, thrust_imperial, marker='o', linestyle='-', color="b", label="Thrust")
            ax1.set_xlabel("Time (sec)")
            ax1.set_ylabel("Thrust (lbf)")
            handles1, labels1 = ax1.get_legend_handles_labels()
            #plot pressure
            ax2 = ax1.twinx() #creates another axis that shares the x-axis
            ax2.plot(time, press_imperial, marker='^', linestyle='-', color="r", label="Pressure")
            ax2.set_ylim(top=max(press_imperial)*1.6) #sets max for the ylim to be a bit higher
            ax2.set_ylabel("Pressure (psig)")
            #show
            all_handles = handles1 + handles2
            all_labels = labels1 + labels2
            plt.legend(all_handles, all_labels)
            plt.savefig(outputFileBase2 + "_thrust-pressure_imperial")
            plt.close()

            #burn rate vs time and burn area vs time (metric)
            fig, ax1 = plt.subplots(figsize=(13, 8))
            #plot burn rate
            ax1.plot(time, ds_dt, marker='o', linestyle='-', color="b", label="Burn rate ds/dt")
            ax1.set_xlabel("Time (sec)")
            ax1.set_ylabel("Burn rate (mm/sec)")
            handles1, labels1 = ax1.get_legend_handles_labels()
            #plot burn area
            ax2 = ax1.twinx() #creates another axis that shares the x-axis
            #A_b = [i * 1000000 for i in calc.get_A_bArr()] #use for conversion to mm^2
            ax2.plot(time, A_b, marker='^', linestyle='-', color="r", label="Burn area A_b")
            #ax2.set_ylim(top=max(A_b)*2)
            #ax2.set_ylim(bottom=0)
            ax2.set_ylabel("Burn area (m^2)")
            handles2, labels2 = ax2.get_legend_handles_labels()
            #show
            all_handles = handles1 + handles2
            all_labels = labels1 + labels2
            plt.legend(all_handles, all_labels)
            plt.savefig(outputFileBase2 + "_burnrate-burnarea_metric")
            plt.close()

            #burn rate vs time and burn area vs time (imperial)
            fig, ax1 = plt.subplots(figsize=(13, 8))
            #plot burn rate
            ax1.plot(time, ds_dt_imperial, marker='o', linestyle='-', color="b", label="Burn rate ds/dt")
            ax1.set_xlabel("Time (sec)")
            ax1.set_ylabel("Burn rate (in/sec)")
            handles1, labels1 = ax1.get_legend_handles_labels()
            #plot burn area
            ax2 = ax1.twinx() #creates another axis that shares the x-axis
            ax2.plot(time, A_b_imperial, marker='^', linestyle='-', color="r", label="Burn area A_b")
            #ax2.set_ylim(top=max(A_b_imperial)*2)
            #ax2.set_ylim(bottom=0)
            ax2.set_ylabel("Burn area (in^2)")
            handles2, labels2 = ax2.get_legend_handles_labels()
            #show
            all_handles = handles1 + handles2
            all_labels = labels1 + labels2
            plt.legend(all_handles, all_labels)
            plt.savefig(outputFileBase2 + "_burnrate-burnarea_imperial")
            plt.close()

            #output to excel sheet
            finalDataFrame = testFires[x][y].get_dat().copy() #start with original data
            #concatenate the rest of the data with the original data
            finalDataFrame = pd.concat(
                [finalDataFrame, pd.DataFrame({"Time (sec)": time}),
                 pd.DataFrame({"Pressure (MPa)": press}),
                 pd.DataFrame({"Thrust (N)": thrust}),
                 pd.DataFrame({"Burn Area A_b (m^2)": A_b}),
                 pd.DataFrame({"Instantaneous Regression ds (m)": ds}),
                 pd.DataFrame({"Cumulative Regression s (m)": s}),
                 pd.DataFrame({"Instantaneous Burn Rate ds/dt (mm/sec)": ds_dt}),
                 pd.DataFrame({"Time (sec)": time}),
                 pd.DataFrame({"Pressure (psi)": press_imperial}),
                 pd.DataFrame({"Thrust (lbf)": thrust_imperial}),
                 pd.DataFrame({"Burn Area A_b (in^2)": A_b_imperial}),
                 pd.DataFrame({"Instantaneous Regression ds (in)": ds_imperial}),
                 pd.DataFrame({"Cumulative Regression s (in)": s_imperial}),
                 pd.DataFrame({"Instantaneous Burn Rate ds/dt (in/sec)": ds_dt_imperial})], axis=1)
            #print(finalDataFrame)
            finalDataFrame.to_excel(excelWriter, sheet_name=str(y))
            y += 1
        excelWriter.close()

        #TODO: CALCULATE BURN RATE!! add this information (avg pressures, avg burnrates, a and n coefficients for both sets of units mm/sec+MPa and in/sec+psi) to a new sheet in the excel workbook, and create and output a figure for the power curve fit for both sets of units


        x += 1


# --------------------- MAIN ---------------------
#debug helper function to print all attributes associated with each TestFire object
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
    
    #results
    outputResults()

main()
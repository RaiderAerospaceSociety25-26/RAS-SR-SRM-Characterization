# RAS-SR-SRM-Characterization
Scripts for characterization for RAS Space Raiders solid rocket motors.

### Reference
Nakka characterization resources:
[Nakka PTBurn](https://www.nakka-rocketry.net/ptburn.html)
[Nakka Burnrate](https://www.nakka-rocketry.net/burnrate.html)

This method uses the method listed at the PTBurn link.

### Configuration File Formatting
Sample entry:
```
!CONFIGSTART
filename test_data.xlsx psig lbf
geometry in [3.139 0.75 1.8] [3.139 0.75 1.8] [3.139 0.75 1.8] [3.139 1 1.8]
throat in 0.546 0.531 0.515
!CONFIGEND
```
Formatting details:
* Line 1: `!CONFIGSTART` is the start of a characterization entry.
* Line 2: `file test_data.xlsx psig lbf` denotes the filename ("test_data.xlsx" here) and the pressure and thrust units associated with this static fire (here psig and lbf). Only `psig` and `kPa` (psi gauge and kilopascals) are accepted entries for pressure, and only `lbf` and `N` (pounds-force and Newtons) are accepted entries for thrust. This file should have worksheets with data from each static fire. The first column of each sheet should be time, the second column should be pressure, and the third column should be thrust. It doesn't matter if the data has a header or not (but if it does, this header must not be more than one row).
* Line 3: `geometry in [3.139 0.75 1.8] [3.139 0.75 1.8] [3.139 0.75 1.8] [3.139 1 1.8]` denotes the geometry of the motor being tested. `in` denotes the units being used in this line (here inches). Only `in` and `mm` (inches and millimeters) are accepted entries. In each set of brackets, the grain length, core diameter, and outer diameter for each grain is entered, starting with the forwardmost grain and ending with the aftmost grain.
* Line 4: `throat in 0.546 0.531 0.515` denotes the throat diameter for each fire with data in the entered Excel workbook. `in` denotes the units being used in this line (here inches). Only `in` and `mm` (inches and millimeters) are accepted entries. These numbers must be entered in the order in which the fires appear as worksheets in the Excel workbook given in Line 2 of the configuration. If there are multiple fires with the same throat diameter, it must be entered multiple times.
* Line 5: `!CONFIGEND` denotes the end of a characterization entry. If another characterization entry is desired within the same configuration file, this series of 5 lines can be repeated after this line.

Ensure there are no unnecessary spaces in the entry (a double-space or a space after a line could mess up the parsing of the config file).

The file should be a regular .txt file and the filename must be denoted in the characterization script (details in comments in the script). The benefit of using this configuration file is that changing the configuration file name in the script is the only change required to the script for any run.
# Scripts Used for BU SM Produciton Checkout
These scripts are used to automate production of the Apollo SM. The complete instructions are [here](https://apollo-lhc.gitlab.io/Assembly/Rev3-assembly/)

This repo was forked from https://github.com/apollo-lhc/Cornell_CM_Production_Scripts/.  The IBERTpy is a set of modified scripts from https://github.com/mvsoliveira/IBERTpy to convert Vivado eyescans from .csv to .pdf and .png formats. 


## Program IPMC
### Overview
The IPMC paramaters are initally set over serial. 

This script is run on adpsun1 at BU.
### Requirements
Make sure to use a virtaul environment if this script is being run as root.
- **Python 3+**
- **pyserial** 

### Instructions
Once the IPMC fw is programmed, run the following to set the parameters:
```
python3 program_ipmc.py
```
Enter the serial number into the prompt.

### Results
Verify the result by connecting to the IPMC directly with screen.


## SM MGT Script
### Overview
Testing the assembled SM involves two uses of IBERTpy. Testing the SM MGTs is done with ```sm_mgt_eyescan.py```, which programs the clocks, loads the loopback firmware, starts the xvcserver, and runs the eyescans provided that the SM is mated to a CM loopback board.

This script is run on minion at BU.
### Requirements
- **Python 3+**
- **fpdf** (the package used to make a pdf file from converting a csv file of a Vivado eyescan. For instruction on how to install it, please follow https://github.com/reingart/pyfpdf) 
- **matplotlib**
- **pandas**
- **fabric** (the package used to execute arbitrary commands over ssh )
- **vivado** (The script sources vivado from /tools/Xilinx/Vivado/2023.2/settings64.sh)
### Instructions
Create a eyescans folder in the home directory.

The hostname comes in the Apollo####-# format. Once the CM loopback board is mated, and the SM connected to the network, test the SM MGTs by running:
```
python3 sm_mgt_eyescan.py -b [hostname] -p [password]
```

If the xvcserver is started, add the ```v``` flag to skip directly to starting the eyescan.

```
python3 sm_mgt_eyescan.py -b [hostname] -p [password] -v
```

Before running the eyescan, the tcl script called by sm_mgt_eyescan will wait so that the BER can be seen dropping below 1E-12. This time can be changed with the ```t``` flag.

### Results
The eyescans automatically be rerun if the eyes are completely closed since Vivado occasionally fails to perform eyescans on perfectly operational links. If all the links are at least partially open, the eyescan csv, and the generated pdf and png, will be saved to the eyescan folder in the home directory.

##  DTH Script
### Overview
Testing the DTH links to the SM is done with ```dth.py```. This launches vivado lab, which programs the DTH FPGA with an IBERT fw and runs a sweep on the link to find the one with the maximum open area. The DTH is then repgrommed with the DTH fw. The clocks on the SM are programmed and routed to the loopback CM so that they can be scoped. 

This script is run on server-room at BU.
### Requirements
- **Python 3+**
- **fpdf** (the package used to make a pdf file from converting a csv file of a Vivado eyescan. For instruction on how to install it, please follow https://github.com/reingart/pyfpdf) 
- **matplotlib**
- **pandas**
- **fabric** (the package used to execute arbitrary commands over ssh )
- **vivado lab** (The script sources vivado lab from /home/tools/Xilinx/Vivado_Lab/2024.1/settings64.sh)
### Instructions
Create a eyescans folder in the home directory.

The hostname comes in the Apollo####-# format. Once the SM is in an ATCA crate with a DTH board, and the SM connected to the network, test the DTH link by running:
```
python3 dth.py -b [hostname] -p [password] -v -d -a 
```

If the SM does not have the production fw loaded, add the ```c``` flag.

### Results
The best eyescan of the sweep is saved in the directory the script was run in.

## C2C-link Eyescans Script
- **Python 2.7** 
- **lnx4189.classe.cornell.edu machine** 
- ssh key-pair to **Apollo## blade**
### Instructions
There are four C2C transceivers with RX-eyescans enable on each rev1 apollo blade. That includes:
```INI
1: C2C1_PHY (RX on Zynq from Virtex)
2: C2C2_PHY (RX on Zynq from Kintex)
3: K_C2C_PHY (RX on Kintex from Zynq)
4: V_C2C_PHY (RX on Virtex from Zynq)
```

*Only K_C2C_PHY is not working (update on 02/01/2022)

Given that we know the Apollo## blade and ttydevice(e.g. ttyUL1)

Run the following command on lnx4189 to just run a single eyescan at a time
```sh
shell $ ./automate_apollo_single_eyescan.sh
```
Or, run the following command on lnx4189 to run eyescans in parallel. 
```sh
shell $ ./automate_apollo_parallel_eyescans.sh
```

Depending on what program is executed, it will ask for Apollo##, ttydevice and your username or foldername on apollo's home directory as well as the C2C link number (1,2,..etc.) for the single-eyescan script. It will `ssh` to a corresponding Zynq and run either **c2c_single_eyescan_script** or **c2c_parallel_eyescans_script** in `username/ApolloTool` folder. Then, it will take a few minutes to run eyescan(s), given the customizable numbers of x-binning, y-binnning, and maximum prescale inside the above automate shell script. The current set of these parameters is {binx=40,biny=40,max_prescale=6}. 

In addition to eyescan outputs to be transfered, both programs also implicitly dump CM##, ID and some commands to check statuses of FPGAs on the CM module to `mcu_tools/data` folder before transfering its `dump*.txt` to lnx4189. However, if the board ID/CM ID is not yet set (i.e ID:00000000), then the program will ask for a user-defined CM# (which is supposed to be the same as the board ID) to `set_id` on the apollo board and ammend the ID info in the `dump*.txt` that is transfered earlier. 

Once, the output files are ready to be transfered. The programs will create a directory `/CM##/weekXX-MM-YYYY/` in `/nfs/cms/hw/apollo/` in order to save `*.png` and `*.log` files from running eyescans with `BUTool.exe` on Apollo##. This step is done implicitly by `check_cm_id_to_mkdir.py` and `set_cm_dir.sh`. (Note that Weekly = Mon-Sun and WeekXX where XX = 1-53)


### Results

* **Eyescan outputs:** Two files(`*.png` + `*.log`) per one eyescan, or three* `*.png` and one `*.log` files from parallel eyescans will be transfered to the weekly-report folder. 
* **Minicom outputs:** One `dump*.txt` file per program execution will be transfered to the weekly-report folder. 

## Autotuning System for Xilinx MGTs

### Overview
Directory containing scripts to tune the emphasis and equalization of
high-speed serial links between two Xilinx FPGA's.

### Requirements
- **Python 3+**
- **Vivado** (the scripts consider that it is possible to start the vivado
  software by calling *vivado* at the terminal. If that is not the case, change
  the \_\_init\_\_ method of XilinxTCL class)
- Boards programmed with the **IBERT bitstream**, configured with the MGT's to
  be tuned at the desired line rate

### Instructions
The autotuning is done in 3 steps: **preparing the boards**, **setting the
*config.ini*** and **running the autotuning script**. In this respository, all
parameters were set for an optical transmission between two KC705 kits, running
at 10 Gbps and using PRBS31.

#### Preparing the boards
The transmitter and receiver boards should be programmed with an IBERT bitstream
generated by Vivado. The line rate, reference clock and enabled MGT's should be
set according to the conditions the system is going to operate.

#### [Optional] Set up the automated autotuning script
Please create and/or adjust the hw_*.tcl in the autotuning/automate folder.

#### Setting the *config.ini*
The *config.ini* file is where the test parameters should be set. They are
loaded by the *run.py* script and specify the MGT's to be tuned, the FPGA's on which the transmitters and receivers are located, the tuning
configurations to be tested, stop conditions for the tuning process, among other
parameters. The file is organized in sections and their variables, as the
following example:

```INI

[Section1]
variable1 = value
variable2 = value

[Section2]
variable3 = value
variable4 = value
variable5 = value

[DEFAULT]
variable1 = value
variable4 = value
variable5 = value

```

The DEFAULT section is a special one, and stablishes the default value for some
of the variables of other sections. If they are not set in their own sections,
the DEFAULT value is used.

#### Setting other files
In the program's current state, autotuning can only run over a set of MGT's that all
share the same transmitter and receiver FPGA locations (e.g. all MGT's with
transmitters on FPGA 1 and all receivers on FPGA 2). Autotuning of MGT's with different
transmitter and receiver FPGA locations must be performed in multiple runs of the autotuning
program for each collection of MGT's that have the same transmitter and receiver FPGA
locations, properly modifying the relevant files after each run.
Before running the files, be sure to set the FPGA on which the transmitters and
receivers of the MGT's are located in CM_VU13P_rcv_setup.tcl and CM_VU13P_trm_setup.tcl.
Both of these files have a line near the top of the code that specifies the FPGA location:
xcvu13p_0 for FPGA 1 and xcvu13p_1 for FPGA 2.

#### Running the autotuning script
The autotuning script is run by the following command:

```sh
$ python3 run.py
```

It loads the parameters in *config.ini*, opening two vivado instances and
connecting one to the transmitter and the other to the receiver FPGA. The
initial setting it then loaded through TCL files, which can set the initial
tuning configuration, PRBS pattern, DFE setting and invert RX/TX differential
pins (if this is required by the PCB design. The script then tests everyone of
the tuning configurations, saves its performance in a CSV file and then presents
the best configuration found.

#### [Optional] Run the automated autotuning script
This script opens Vivado instances and configures the FPGAs with bit files. The 
Vivado instances remain open (no need to start Vivado by yourself). Then the test 
is perormed by using the run.py script:

```sh
$ cd automate
$ ./run_MGT_autotune.sh
```

### Results
The results are presented in a CSV file. The columns present the TX Differential
Swing, TX Pre, TX Post, RX termination voltage and the respective eye scan open
area resultant for that configuration. This parameter measures how open the eye
scan is, and should be maximized to improve the link integrity. An example of a
CSV result file is shown bellow.

```CSV
TXDIFFSWING,TXPRE,TXPOST,RXTERM,Open Area
269 mV (0000),0.00 dB (00000),0.00 dB (00000),900 mV,2664
269 mV (0000),0.00 dB (00000),4.44 dB (10000),900 mV,2268
269 mV (0000),4.44 dB (10000),0.00 dB (00000),900 mV,1692
269 mV (0000),4.44 dB (10000),4.44 dB (10000),900 mV,1332
------------BEST------------
269 mV (0000),0.00 dB (00000),0.00 dB (00000),900 mV,2664

```

#### Running the margin scanning script
The margin scanning script is run by the following command. It uses the same logic as the autotuning script but scans with 1D bathtub plot instead of 2D eyescan.

```sh
$ python3 run1D.py
```
This only scans parameters on the FPGA. To scan parameter on the firefly, one needs to directly change the setting on the firefly via mcu and run the scan for each of the changed setting. Make sure to modify the name of the files saved everytime the firefly setting changes.


To plot. First run the following command to make a table with all the data.
```sh
$ python3 table.py
```
This creates a log that gathers all the settings and links together as well as an array of number of good links in the end.

Copy and paste the last array into the following script and run to create plot.

```sh
$ python3 plotting.py
```

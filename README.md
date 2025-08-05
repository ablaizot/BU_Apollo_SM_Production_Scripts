# Scripts Used for BU SM Produciton Checkout
These scripts are used to automate production of the Apollo SM. The complete instructions are [here](https://apollo-lhc.gitlab.io/Assembly/Rev3-assembly/)

This repo was forked from https://github.com/apollo-lhc/Cornell_CM_Production_Scripts/.  The IBERTpy is a set of modified scripts from https://github.com/mvsoliveira/IBERTpy to convert Vivado eyescans from .csv to .pdf and .png formats. 


## Program IPMC
### Overview
The IPMC paramaters are initally set over serial. 

This script is run on adpsun1 at BU.
### Requirements
Make sure to use a virtual environment if this script is being run as root.
- **Python 3+**
- **pyserial** 

### Instructions
Once the IPMC fw is programmed, run the following to set the parameters:
```
python3 program_ipmc.py
```
Enter the serial number into the prompt.

### Results
Verify IPMC parameters were set correctly by connecting to the IPMC directly with screen.

## BootMedia
### Overview
The sd card and the ssd are loaded with the latest FW and FS.

This script is run on adpsun1 at BU.
### Requirements
### Instructions
Place the latest FS from https://apollo-lhc.gitlab.io/SM_Filesystem/01-location/ in the BootMedia folder.

Plug in the sd card.
```
sudo ./make_sd_zynq.sh /dev/sdX [service module serial number]
```
This will load the FS and FW onto the SD card.

Plug in the ssd.
```
sudo ./make_ssd.sh /dev/sdX
```
This will load the FS onto the sdd.


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
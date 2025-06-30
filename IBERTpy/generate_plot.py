# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 16:40:12 2017

@author: msilvaol
"""

from eyescan_plot import eyescan_plot
from glob import glob
import argparse
import datetime
import os.path
import numpy as np

minlog10ber = -8
overwrite = True

wmy='%W-%m-%Y'
weekly = datetime.datetime.now().strftime(wmy) 
#print(weekly)
dhms='day-%d_time-%H.%M.%S'
timestamp = datetime.datetime.now().strftime(dhms)
#print(timestamp)

parser = argparse.ArgumentParser()
parser.add_argument('CMXX', type=int, help="specified CM##")
parser.add_argument('file_path', type=str, help="file path to the CSV file")

args = parser.parse_args()

out_file = args.file_path.replace('csv','pdf')

yticks = list(np.arange(-127,0,16))+[0]+list(np.arange(127,0,-16))[-1::-1]
xticks = list(np.arange(-0.5,0.625,0.125))

eyescan_plot(args.file_path, out_file, minlog10ber, colorbar=True, xaxis=True, yaxis=True, xticks_f=xticks, yticks_f=yticks, mask_x1x2x3y1y2=(0.25, 0.4, 0.45, 0.25, 0.28))

#!/bin/bash

# NOTE: YOU NORMALLY DO NOT NEED TO RUN THIS SCRIPT.  DO SO ONLY AFTER READING BELOW.

# Use this script to generate a new set of tshark protocols. After running it remove 
# the protocols from the protocols.txt file the script produces by either commenting 
# out (with # character like a bash script) the protocols you aren't interested in 
# or just taking htem out of the list compltetely. Then replace conf/protocols.ini 
# save with your new list. Note you should always exclude the protocols that are 
# commented out in the current protocols.ini. 


tshark -G protocols | awk 'BEGIN { FS = "\t" } ; { print $3 }' | sort > protocols.txt

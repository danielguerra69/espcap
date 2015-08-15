#!/bin/bash

# Use this script to generate a new set of tshark protocols.
# After running, it remove the protocols from protocols.txt
# by either commenting them out (with # character like a bash
# script) that you aren't interested then save the new list as
# file as protocols.list. Note you should always exclude the
# protocols in the current protocols.ini, should check which
# ones those are before running this script. 

tshark -G protocols | awk 'BEGIN { FS = "\t" } ; { print $3 }' | sort > protocols.txt

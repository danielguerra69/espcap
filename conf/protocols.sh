#!/bin/bash

tshark -G protocols | awk 'BEGIN { FS = "\t" } ; { print $3 }' | sort > protocols.txt

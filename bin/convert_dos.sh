#!/bin/bash
PATH=/usr/local/bin:$PATH
finp=$1
fout=$2
epstool --quiet -t6u --dpi 96 $finp $fout


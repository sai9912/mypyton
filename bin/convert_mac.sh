#!/bin/bash
PATH=/usr/local/bin:$PATH
finp=$1
fout=$2
epstool --quiet --add-pict-preview --mac-binary --dpi 72 $finp $fout

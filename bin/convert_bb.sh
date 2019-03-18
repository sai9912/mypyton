#!/bin/bash
PATH=/usr/local/bin:$PATH
finp=$1
fout=$2
#epstool --quiet --copy --bbox $finp $fout
epstool --quiet --copy $finp $fout
#cp $finp $fout

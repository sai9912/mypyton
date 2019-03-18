#!/bin/bash

echo "installing epstool"

if [ ! -f /home/ubuntu/opt/usr/local/bin/epstool ]; then
    echo "esptool not found"
    cd /root/app/src && tar zxvf ./epstool-3.08.tar.gz && cd ./epstool-3.08 && prefix=/home/ubuntu/opt make install
    ln -s /home/ubuntu/opt/usr/local/bin/epstool /usr/bin/epstool
fi

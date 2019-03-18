#!/usr/bin/env bash
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ./id_rsa -p 2222 root@127.0.0.1 "cd /root/app && make test"

#!/usr/bin/env bash
./ssh-retry.sh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ./id_rsa root@127.0.0.1 -p 2222

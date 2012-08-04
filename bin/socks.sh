#!/bin/bash

login=${1:-proxy}
daemon="autossh"
while true
do
pgrep $daemon >/dev/null || $daemon -M 0 -f -N -F /home/dhh/.ssh/config $login
sleep 5
done

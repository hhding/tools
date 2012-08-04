#!/bin/bash

mobileno=$1
passwd=$2

while true
do
    for h in dna-505 dna-419
    do
        sleep 2
        date
        if echo | nc -w2 $h 22 | grep -q mis; then
            echo $h OK
        else
            echo $h NOK
            ./cliofetion -f $mobileno -p $passwd -t $mobileno -d "$h abnormal: check from $HOSTNAME"
            sleep 60
        fi
    done
done | tee /tmp/check.log


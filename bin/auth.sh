#!/bin/bash
#art@copyright-notice.com
#9SlucsOak 

user=$1
pass=$2
method=$3

if test $method = pop
then
  echo user $user
  echo pass $pass
else
  echo HELO localhost
  echo AUTH LOGIN
  echo -n $user | base64
  echo -n $pass | base64
fi

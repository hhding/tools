#!/bin/bash

expect -c '
spawn luit -encoding gbk ssh -1 dhh@newsmth.net

interact {
        timeout 30 { send "\0"}
}'


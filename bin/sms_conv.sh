#!/bin/bash

sed 's/\(..\)\(..\)/\2\1/g' | xxd -r -p | iconv -f utf16; echo

#!/bin/bash

infile=$1
outfile=$2
algorithm=$3
key=$4

openssl enc -d $3 -in $1 -out $2 -k $4 2>/dev/null 
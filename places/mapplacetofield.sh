#!/bin/bash

infile=$1
srcfile=$2

while read line; do
	grep -e "$line" $srcfile | awk -F"|" '{print $1"\t"$2}' | sort | uniq
done < $infile

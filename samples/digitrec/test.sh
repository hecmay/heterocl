#!/bin/bash
for i in $(seq 1 2 200)
do
   echo "Welcome $i times"
   python digitrec_test.py $i
done

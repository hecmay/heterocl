#!/bin/bash
for i in $(seq 200 2 400)
do
   echo "Welcome $i times"
   python digitrec_test.py $i
done

#!/bin/bash
for ((i=0; i<=9; i=i+1))
do 
      unzip 20bn-jester-v1-"0""$i".zip 20bn-jester-v1-"0""$i"
done

for ((i=10; i<=22; i=i+1))
do 
      unzip 20bn-jester-v1-"$i".zip 20bn-jester-v1-"$i"
done

cat 20bn-jester-v1-?? | tar zx
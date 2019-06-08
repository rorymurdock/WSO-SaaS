#!/bin/bash
for i in {1..2000}
do
	if ping cn$i.awmdm.com -c 1 > /dev/null 2>&1
	then
		echo cn$i.awmdm.com
	fi
done

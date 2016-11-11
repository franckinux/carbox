#!/bin/bash

wget -O zones-de-danger-magellan.zip -- http://carte-gps-gratuite.fr/radars/zones-de-danger-magellan.zip
if [ -f md5sum.txt ] ; then
   md5sum --quiet -c md5sum.txt
   if [ $? != 0 ] ; then
      unzip -o zones-de-danger-magellan.zip
      md5sum zones-de-danger-magellan.zip > md5sum.txt
   fi
else
   md5sum zones-de-danger-magellan.zip > md5sum.txt
   unzip -o zones-de-danger-magellan.zip
fi
rm -f zones-de-danger-magellan.zip
rm -rf __MACOSX

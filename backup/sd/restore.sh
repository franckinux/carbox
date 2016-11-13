#!/bin/bash
gzip -dc image.bin.gz | dd of=$1

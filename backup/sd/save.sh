i#!/bin/bash
dd if=$1 bs=1M | gzip > image.bin.gz

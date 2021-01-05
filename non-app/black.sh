#!/bin/bash

for x in $(ls -1 *py); do black $x ; done

#!/bin/bash

if [[ "$(whoami)" == "root" ]] 
then
  pip install -r requirements.txt
else
  echo "run this script as root"
fi

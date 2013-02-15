#!/bin/bash

mkdir -b bitbucket
mkdir -p github

if [[ "$(whoami)" == "root" ]] 
then
  pip install -r requirements.txt
else
  echo "run this script as root"
fi

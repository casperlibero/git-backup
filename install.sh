#!/bin/bash

mkdir -p bitbucket
mkdir -p github

if [[ ! "$(which pip)" ]]
then
  echo "you need install python-pip"
  exit
fi

if [[ "$(whoami)" == "root" ]] 
then
  pip install -r requirements.txt
else
  echo "run this script as root"
  exit
fi

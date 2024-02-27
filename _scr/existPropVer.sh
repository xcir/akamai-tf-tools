#!/bin/bash
rootpath=$(dirname $(cd $(dirname $0); pwd))
find ${rootpath}/props/ctr_* -type f -name *.json|xargs grep propertyVersion

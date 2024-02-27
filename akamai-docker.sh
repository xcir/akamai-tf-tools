#!/bin/bash
if [ -z "$AKHOME" ]; then
  AKHOME="$HOME"
fi
SCRIPT_DIR=$(cd $(dirname $0); pwd)
docker run --rm -it -v $AKHOME/.edgerc:/root/.edgerc -v ./:/workdir/mount akamai/shell
echo 'chown -R props work'
sudo chown -R $(id -u $USER):$(id -g $USER)  $SCRIPT_DIR/props $SCRIPT_DIR/work

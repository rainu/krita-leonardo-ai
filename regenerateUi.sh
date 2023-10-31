#!/bin/sh

SCRIPT_PATH=$(realpath "$0")
SCRIPT_HOME=$(dirname "$SCRIPT_PATH")

for UI_FILE in $(find ./ -name "*.ui"); do
  GEN_FILE=$(echo $UI_FILE | sed 's/.ui/.py/')
  python -m PyQt5.uic.pyuic -x ${UI_FILE} -o ${GEN_FILE}
done
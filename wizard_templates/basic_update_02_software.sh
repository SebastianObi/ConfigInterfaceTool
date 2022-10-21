#!/bin/bash


source vendor/colors.sh


if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}Error:${NC} You need to run this script as root (UID=0)"
  exit 1
fi


if [ -p /dev/stdin ]; then
  echo -e "${RED}Error:${NC} This script can't be piped!"
  exit 1
fi


LOG_FILE="/tmp/wizard.log"
echo "" > "${LOG_FILE}"


echo -ne "Updating Reticulum..."
if ! pip3 install rns --upgrade >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Updating NomadNet..."
if ! pip3 install nomadnet --upgrade >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Updating RNode Software..."
if ! pip3 install rnodeconf --upgrade >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -e "Finished!"


exit 0
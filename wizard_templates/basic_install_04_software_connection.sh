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


echo -ne "Installing Advanced network functions..."
if ! apt -y -q install dnsmasq iptables bridge-utils >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Installing WiFi access point..."
if ! apt -y -q install hostapd dnsmasq iptables bridge-utils >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Installing SSH Server..."
if ! apt -y -q install ssh >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


#echo -ne "Installing VNC Server..."
#if ! apt -y -q install realvnc-vnc-server realvnc-vnc-viewer >> "${LOG_FILE}" 2>&1; then
#  echo -e " ${RED}failed!${NC}"
#  exit 1
#fi
#echo -e " ${GREEN}OK!${NC}"


echo -e "Finished!"


exit 0
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


echo -ne "Updating packet repository..."
if ! apt -y -q update >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Updating system..."
if ! ( DEBIAN_FRONTEND=noninteractive apt -y -q -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade && DEBIAN_FRONTEND=noninteractive apt -y -q -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" full-upgrade ) >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Cleanup system..."
if ! ( apt -y -q clean && apt -y -q autoclean && apt -y -q autoremove ) >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -e "Finished!"


exit 0
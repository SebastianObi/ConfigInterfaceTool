#!/bin/bash


##############################################################################################################
# Configuration


DOWNLOAD_URL_SERVER="https://raw.githubusercontent.com/SebastianObi/ConfigInterfaceTool/main/releases/"
DOWNLOAD_URL_FILE_RELEASE="release_full.tar.gz"
DOWNLOAD_URL_FILE_DEV="dev_full.tar.gz"
DOWNLOAD_URL="${DOWNLOAD_URL_SERVER}${DOWNLOAD_URL_FILE_RELEASE}"
DOWNLOAD_PATH="/root/ConfigInterfaceTool"
DOWNLOAD_CMD="./install.sh"
DOWNLOAD_CMD_ARGS="-s -u"


##############################################################################################################
# Colors


RED='\033[0;31m'
LIGHT_RED='\033[1;31m'
GREEN='\033[0;32m'
LIGHT_GREEN='\033[1;32m'
YELLOW='\033[0;33m'
LIGHT_YELLOW='\033[1;33m'
BLUE='\033[0;34m'
LIGHT_BLUE='\033[1;34m'
PURPLE='\033[0;35m'
LIGHT_PURPLE='\033[1;35m'
WHITE='\033[0;37m'
BG_BLACK='\033[40m'
RESET='\033[0m'
NC='\033[0m'


##############################################################################################################
# Texts


OK="${GREEN}${BG_BLACK} ok.${RESET}"
FAIL="${RED}${BG_BLACK} failed!${RESET}"
NOK="${YELLOW}${BG_BLACK} nok.${RESET}"


##############################################################################################################
# Setup/Start


while getopts ":rd" opt; do
  case "${opt}" in
    r) DOWNLOAD_URL="${DOWNLOAD_URL_SERVER}${DOWNLOAD_URL_FILE_RELEASE}";;
    d) DOWNLOAD_URL="${DOWNLOAD_URL_SERVER}${DOWNLOAD_URL_FILE_DEV}";;
  esac
done


echo -ne "Checking root..."
if [[ $EUID -ne 0 ]]; then
  echo -e "${FAIL}"
  echo -e "You need to run this script as root (UID=0)."
  echo -e "To change the user to root enter the command: sudo su"
  exit 1
fi
echo -e "${OK}"


echo -ne "Checking script execution..."
if [ -p /dev/stdin ]; then
  echo -e "${FAIL}"
  echo -e "This script can't be piped!"
  exit 1
fi
echo -e "${OK}"


if [ -n "${DOWNLOAD_PATH}" ]; then
  echo -ne "Creating folder '${DOWNLOAD_PATH}'..."
  if ! mkdir -p $DOWNLOAD_PATH 2>&1; then
    echo -e "${NOK}"
    exit 1
  fi
  echo -e "${OK}"

  echo -ne "Entering folder '${DOWNLOAD_PATH}'..."
  if ! cd $DOWNLOAD_PATH 2>&1; then
    echo -e "${NOK}"
    exit 1
  fi
  echo -e "${OK}"
fi


echo -ne "Downloading..."
if [ -n "${DOWNLOAD_URL}" ]; then
  if wget --no-check-certificate -q -O - "${DOWNLOAD_URL}" | tar -xz 2>&1; then
    echo -e "${OK}"
    echo -ne "Checking installer..."
    if [ -e "${DOWNLOAD_CMD}" ]; then
      echo -e "${OK}"
      echo -ne "Changing installer permissions/right..."
      if chmod +x "${DOWNLOAD_CMD}" 2>&1; then
        echo -e "${OK}"
        echo -e "Starting installer..."
        $DOWNLOAD_CMD $DOWNLOAD_CMD_ARGS
        exit 0
      else
        echo -e "${NOK}"
        exit 1
      fi
    else
      echo -e "${NOK}"
      exit 1
    fi
  else
    echo -e "${NOK}"
    exit 1
  fi
else
  echo -e "${NOK}"
  exit 1
fi

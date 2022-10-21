#!/bin/bash


##############################################################################################################
# Configuration


#set -o errexit # Exit on error
#set -o errtrace # Exit on error inside functions
#set -o xtrace # Turn on traces, disabled by default

APP_NAME="ConfigInterfaceTool"
APP_FILE="configinterfacetool"
APP_DESCRIPTION="Easy, minimalistic and simple interface for device/application administration and configuration."
APP_VERSION="0.0.1"
APP_COPYRIGHT="(c) 2022 Sebastian Obele  /  obele.eu"

DOWNLOAD_URL_SERVER="https://raw.githubusercontent.com/SebastianObi/ConfigInterfaceTool/main/releases/"
DOWNLOAD_URL_FILE_RELEASE="release_update.tar.gz"
DOWNLOAD_URL_FILE_DEV="dev_update.tar.gz"
DOWNLOAD_URL=""
DOWNLOAD_CMD=""
DOWNLOAD_CMD_ARGS=""


##############################################################################################################
# Setup/Start


_run() {
_header
_start_prompt
_root_check
_pipe_check
_linux_check
_download_prompt
_download_check
_file_delete
_file_copy
_file_permission_owner
_file_permission_rights
_footer
_reboot_prompt
}


_run_unattended() {
_header
#_start_prompt
_start_unattended_prompt
_root_check
_pipe_check
_linux_check
#_download_prompt
_download_check
_file_delete
_file_copy
_file_permission_owner
_file_permission_rights
_footer
_reboot_prompt
}


##############################################################################################################
# Variables


LOG_FILE="/tmp/${0##*/}-$(date +%Y%m%d-%H%M%S).log"
DEPS_SYSTEM=()
DEPS_PYTHON=()
PATH_CURRENT=$(dirname $(realpath $0))
PERMISSION_OWNER=("$PATH_CURRENT/*")
PERMISSION_RIGHTS=("$PATH_CURRENT/bin/main*.py" "$PATH_CURRENT/*.sh" "$PATH_CURRENT/service_templates/*.sh" "$PATH_CURRENT/software_templates/*.sh" "$PATH_CURRENT/wizard_templates/*.sh")
FILE_DELETE=("/var/www/${APP_FILE}/*")
FILE_COPY_SOURCE=("$PATH_CURRENT/www/.")
FILE_COPY_DEST=("/var/www/${APP_FILE}/")


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
# Functions


_help() {
  local help
  read -r -d '' help << EOM
Usage: $0 [-hvud]

  -h         Displays this help

  -r         Download release version
  -d         Download development version

  -u         Unattended installation
  -v         Outputs release info and exits
EOM
  echo "$help"
  exit 1
}


_version() {
  echo -e "${APP_NAME} v${APP_VERSION} - ${APP_DESCRIPTION}"
  exit 1
}


_divider() {
  echo -e "..............................................................................."
}


_header() {
  _divider
  echo -e "        Name: ${APP_NAME}"
  echo -e "              ${APP_DESCRIPTION}"
  echo -e "Program File: ${0##*/}"
  echo -e "    Log File: ${LOG_FILE}"
  echo -e "     Version: ${APP_VERSION}"
  echo -e "   Copyright: ${APP_COPYRIGHT}"
  _divider
}


_footer() {
  _divider
  echo -e "Finished!"
  echo -e "You have successfully updated ${APP_NAME}."
  _divider
}


_panic() {
  echo -e ""
  echo -e "Aborted!"
  echo -e "For more information check the logs in ${LOG_FILE}"
  echo -e ""
  echo -e "You can try to run the script again, this maybe solve the error."
  exit 1
}


_start_prompt() {
  echo -e ""
  echo -e "This script updates ${APP_NAME}."
  echo -e "The Quick Updater will guide you through a few easy steps."
  while true; do
    read -p "Do you want to proceed? [y/n]" YN
    case $YN in 
      [Yy]*)
        echo -e ""
        echo -e "Ok, proceeding..."
        break;;
      [Nn]*)
        echo -e ""
        echo -e "No, exiting now."
        exit 1;;
      *)
        echo -e ""
        echo -e "Please answer yes or no.";;
    esac
  done
}


_start_unattended_prompt() {
  echo -e ""
  echo -e "This script updates ${APP_NAME}."
  echo -e ""
  echo -e "Unattended mode without any user interaction! Using recommended default settings!"
}


_root_check() {
  echo -ne "Checking root..."
  if [[ $EUID -ne 0 ]]; then
    echo -e "${FAIL}"
    echo -e "You need to run this script as root (UID=0)"
    echo -e "To change the user to root enter the command: sudo su"
    exit 1
  fi
  echo -e "${OK}"
}


_pipe_check() {
  echo -ne "Checking script execution..."
  if [ -p /dev/stdin ]; then
    echo -e "${FAIL}"
    echo -e "This script can't be piped!"
    exit 1
  fi
  echo -e "${OK}"
}


_linux_check() {
  echo -ne "Checking Linux..."
  if type lsb_release >/dev/null 2>&1; then # linuxbase.org
    OS=$(lsb_release -si)
    RELEASE=$(lsb_release -sr)
    CODENAME=$(lsb_release -sc)
    DESC=$(lsb_release -sd)
    MODEL=""
    if [ -f /proc/device-tree/model ]; then
      MODEL=$(tr -d '\0' < /proc/device-tree/model)
    fi
  elif [ -f /etc/os-release ]; then # freedesktop.org
    . /etc/os-release
    OS=$ID
    RELEASE=$VERSION_ID
    CODENAME=$VERSION_CODENAME
    DESC=$PRETTY_NAME
    MODEL=""
    if [ -f /proc/device-tree/model ]; then
      MODEL=$(tr -d '\0' < /proc/device-tree/model)
    fi
  else
    echo -e "${FAIL}"
    echo -e "Unsupported Linux distribution"
     exit 1
  fi
  echo -e "${OK}"
}


_download_prompt() {
  LOOP=1
  while [ $LOOP -eq 1 ]; do
    echo -e ""
    echo -e "Which version do you want to use?"
    options=("Release (Recommended for production use)" "Development")
    select opt in "${options[@]}"; do
      case $opt in
      "Release"*)
        echo -e ""
        echo -e "Ok, downloading the latest release version."
        DOWNLOAD_URL="${DOWNLOAD_URL_SERVER}${DOWNLOAD_URL_FILE_RELEASE}"
        _download
        LOOP=0
        break;;
      "Development"*)
        echo -e ""
        echo -e "Ok, downloading the latest development version."
        DOWNLOAD_URL="${DOWNLOAD_URL_SERVER}${DOWNLOAD_URL_FILE_DEV}"
        _download
        LOOP=0
        break;;
      *)
        echo -e ""
        echo -e "Invalid choice!";;
      esac
    done
  done
}


_download_check() {
  echo -ne "Checking Download URL..."
  if [ -n "${DOWNLOAD_URL}" ]; then
    echo -e "${OK}"
    _download
  else
    echo -e "${NOK}"
    _panic
  fi
}


_download() {
  echo -ne "Downloading..."
  if [ -n "${DOWNLOAD_URL}" ]; then
    if wget --no-check-certificate -q -O - "${DOWNLOAD_URL}" | tar -xz >> "${LOG_FILE}" 2>&1; then
      echo -e "${OK}"
    else
      echo -e "${NOK}"
      _panic
    fi
  else
    echo -e "${NOK}"
    _panic
  fi
}


_file_delete() {
  echo -ne "Deleting files..."
  for i in ${!FILE_DELETE[@]}; do
    if ! rm -R -f "${FILE_DELETE[$i]}" >> "${LOG_FILE}" 2>&1; then
      echo -e "${NOK}"
      _panic
    fi
  done
  echo -e "${OK}"
}


_file_copy() {
  echo -ne "Copying files..."
  for i in ${!FILE_COPY_SOURCE[@]}; do
    if [ -d "${FILE_COPY_DEST[$i]}" ]; then
      if ! cp -a "${FILE_COPY_SOURCE[$i]}" "${FILE_COPY_DEST[$i]}" >> "${LOG_FILE}" 2>&1; then
        echo -e "${NOK}"
        _panic
      fi
    fi
  done
  echo -e "${OK}"
}


_file_permission_owner() {
  echo -ne "Changing file permissions/owner to '$(whoami)'..."
  for file in ${PERMISSION_OWNER[@]}; do
    if [ -e "${file}" ]; then
      if ! chown -cR "$(whoami)" "${file}" >> "${LOG_FILE}" 2>&1; then
        echo -e "${NOK}"
        _panic
      fi
    fi
  done
  echo -e "${OK}"
}


_file_permission_rights() {
  echo -ne "Changing file permissions/right..."
  for file in ${PERMISSION_RIGHTS[@]}; do
    if [ -e "${file}" ]; then
      if ! chmod +x "${file}" >> "${LOG_FILE}" 2>&1; then
        echo -e "${NOK}"
        _panic
      fi
    fi
  done
  echo -e "${OK}"
}


_reboot_prompt() {
  echo -e ""
  echo -e "To activate the changes, the system must be rebooted."
  while true; do
    read -p "Do you want to reboot now? [y/n]" YN
    case $YN in 
      [Yy]*)
        echo -e ""
        echo -e "Ok, rebooting..."
        _reboot
        break;;
      [Nn]*)
        echo -e ""
        echo -e "No, exiting now."
        exit 1;;
      *)
        echo -e ""
        echo -e "Please answer yes or no.";;
    esac
  done
}


_reboot() {
  shutdown -r now
}


##############################################################################################################
# Setup/Start


UNATTENDED=false


while getopts ":hvurd" opt; do
  case "${opt}" in
    v) _version;;
    u) UNATTENDED=true;;
    r) DOWNLOAD_URL="${DOWNLOAD_URL_SERVER}${DOWNLOAD_URL_FILE_RELEASE}";;
    d) DOWNLOAD_URL="${DOWNLOAD_URL_SERVER}${DOWNLOAD_URL_FILE_DEV}";;
    h) _help;;
    *) _help;;
  esac
done


if [ "$UNATTENDED" = true ]; then
  _run_unattended
else
  _run
fi
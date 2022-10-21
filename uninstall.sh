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


##############################################################################################################
# Setup/Start


_run() {
_header
_start_prompt
_root_check
_pipe_check
_linux_check
_service_addon_uninstall
_service_uninstall
_webproxy_uninstall
_deps_python_uninstall
_deps_system_uninstall
_deps_system_clean
_footer
_footer_next_steps
}


_run_unattended() {
_header
#_start_prompt
_start_unattended_prompt
_root_check
_pipe_check
_linux_check
_service_addon_uninstall
_service_uninstall
_webproxy_uninstall
_deps_python_uninstall
_deps_system_uninstall
_deps_system_clean
_footer
_footer_next_steps
}


##############################################################################################################
# Variables


LOG_FILE="/tmp/${0##*/}-$(date +%Y%m%d-%H%M%S).log"
DEPS_SYSTEM=("python3-pip" "nginx")
DEPS_PYTHON=("psutil" "gunicorn" "flask" "flask_httpauth" "aiohttp" "aiohttp_basicauth")
PATH_CURRENT=$(dirname $(realpath $0))


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
Usage: $0 [-hvu]

  -h         Displays this help
  -v         Outputs release info and exits
  -u         Unattended uninstallation
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
  echo -e "You have successfully uninstalled ${APP_NAME}."
  _divider
}


_footer_next_steps() {
  echo -e ""
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
  echo -e "This script uninstalls ${APP_NAME}, all files/folders and all dependencies."
  echo -e "The Quick Uninstaller will guide you through a few easy steps."
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
  echo -e "This script uninstalls ${APP_NAME}, all files/folders and all dependencies."
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
    MODEL=$(tr -d '\0' < /proc/device-tree/model)
  elif [ -f /etc/os-release ]; then # freedesktop.org
    . /etc/os-release
    OS=$ID
    RELEASE=$VERSION_ID
    CODENAME=$VERSION_CODENAME
    DESC=$PRETTY_NAME
    MODEL=$(tr -d '\0' < /proc/device-tree/model)
  else
    echo -e "${FAIL}"
    echo -e "Unsupported Linux distribution"
    exit 1
  fi
  echo -e "${OK}"
}


_return_check() {
  if [ "$1" -ne 0 ]; then
    echo -e "${FAIL}"
    _panic
  fi
}


_deps_system_clean() {
  echo -ne "Cleaning dependencies system..."
  if grep -q "debian" /etc/os-release; then
    if ! apt clean && apt autoclean && apt autoremove >> "${LOG_FILE}" 2>&1; then
      echo -e "${FAIL}"
      _panic
    fi
  else
    echo -e "${FAIL}"
    echo -e "Cannot detect your distribution package manager."
    _panic
  fi
  echo -e "${OK}"
}


_deps_system_uninstall() {
  echo -ne "Checking and uninstalling dependencies system..."
  for dep in ${DEPS_SYSTEM[@]}; do
    if command -v "${dep}" >> "${LOG_FILE}" 2>&1; then
      if grep -q "debian" /etc/os-release; then
        apt remove -y "${dep}" >> "${LOG_FILE}" 2>&1
      elif grep -q "fedora" /etc/os-release || grep -q "centos" /etc/os-release; then
        dnf remove -y "${dep}" >> "${LOG_FILE}" 2>&1
      else
        echo -e "${FAIL}"
        echo -e "Cannot detect your distribution package manager."
        _panic
      fi
      _return_check $?
    fi
  done
  echo -e "${OK}"
}


_deps_python_uninstall() {
  echo -ne "Checking and uninstalling dependencies python..."
  for dep in ${DEPS_PYTHON[@]}; do
    pip3 uninstall -y "${dep}" >> "${LOG_FILE}" 2>&1
    _return_check $?
  done
  echo -e "${OK}"
}


_webproxy_uninstall() {
  echo -ne "Uninstalling Webproxy..."

  if rm -f "/etc/ssl/private/${APP_FILE}.key" >> "${LOG_FILE}" 2>&1; then
    echo -ne ""
  else
    echo -e "${NOK}"
    _panic
  fi

  if rm -f "/etc/ssl/certs/${APP_FILE}.crt" >> "${LOG_FILE}" 2>&1; then
    echo -ne ""
  else
    echo -e "${NOK}"
    _panic
  fi

  if rm -f "/etc/nginx/${APP_FILE}.pem" >> "${LOG_FILE}" 2>&1; then
    echo -ne ""
  else
    echo -e "${NOK}"
    _panic
  fi

  if rm -f "/etc/nginx/sites-enabled/${APP_FILE}.conf" >> "${LOG_FILE}" 2>&1; then
    echo -ne ""
  else
    echo -e "${NOK}"
    _panic
  fi

  if rm -f "/etc/nginx/sites-available/${APP_FILE}.conf" >> "${LOG_FILE}" 2>&1; then
    echo -ne ""
  else
    echo -e "${NOK}"
    _panic
  fi

  if rm -R -f "/var/www/${APP_FILE}/*" >> "${LOG_FILE}" 2>&1; then
    echo -ne ""
  else
    echo -e "${NOK}"
    _panic
  fi

  echo -e "${OK}"
}


_service_uninstall() {
  echo -ne "Unistalling service..."
  systemctl stop $APP_FILE >> "${LOG_FILE}" 2>&1

  if rm -f "/etc/systemd/system/${APP_FILE}.service" >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi

  echo -ne "Reloading service..."
  if systemctl daemon-reload >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


_service_addon_uninstall() {
  echo -ne "Unistalling addon service..."
  systemctl stop $APP_FILE-addon >> "${LOG_FILE}" 2>&1

  if rm -f "/etc/systemd/system/${APP_FILE}-addon.service" >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi

  echo -ne "Reloading addon service..."
  if systemctl daemon-reload >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


##############################################################################################################
# Setup/Start


UNATTENDED=false


while getopts ":hvu" opt; do
  case "${opt}" in
    v) _version;;
    u) UNATTENDED=true;;
    h) _help;;
    *) _help;;
  esac
done


if [ "$UNATTENDED" = true ]; then
  _run_unattended
else
  _run
fi

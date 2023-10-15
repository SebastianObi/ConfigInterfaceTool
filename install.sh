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
DOWNLOAD_URL_FILE_RELEASE="release_full.tar.gz"
DOWNLOAD_URL_FILE_DEV="dev_full.tar.gz"
DOWNLOAD_URL=""
DOWNLOAD_CMD="install.sh"
DOWNLOAD_CMD_ARGS="-s"
DOWNLOAD_CMD_ARGS_USER=""

DEFAULT_SSL="/C=DE/ST=NRW/L=Duesseldorf/O=IT/CN=configinterfacetool.local"
DEFAULT_USER="admin"
DEFAULT_PASSWORD="password"


##############################################################################################################
# Setup/Start


_run() {
_header
_start_prompt
_root_check
_pipe_check
_linux_check
_download_prompt
_file_delete
_file_copy
_file_permission_owner
_file_permission_rights
_addon_prompt
_deps_system_update
_deps_system_check
_python_check
_deps_python_check
_deps_file_check
_config_prompt
_webserver_prompt
_webproxy_prompt
_password_prompt
_user_prompt
_service_prompt
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
#_download_prompt
_download_check
_file_delete
_file_copy
_file_permission_owner
_file_permission_rights
#_addon_prompt
_deps_system_update
_deps_system_check
_python_check
_deps_python_check
_deps_file_check
#_config_prompt
_config_install
#_webserver_prompt
_webserver_gunicorn
#_webproxy_prompt
_webproxy_nginx_install
_webproxy_nginx_config_ssl
#_webproxy_nginx_config_dh
_webproxy_nginx_config
_webserver_config
#_password_prompt
_password_default
#_user_prompt
#_service_prompt
_service_install
_service_addon_install
_service_start
_service_addon_start
_footer
_footer_next_steps
}


##############################################################################################################
# Variables

PATH_CURRENT=$(dirname $(realpath $0))
LOG_FILE="/tmp/${0##*/}-$(date +%Y%m%d-%H%M%S).log"
DEPS_SYSTEM=("python3-pip")
DEPS_PYTHON=("psutil")
DEPS_FILE=("$PATH_CURRENT/bin/main.py")
PERMISSION_OWNER=("$PATH_CURRENT/*")
PERMISSION_RIGHTS=("$PATH_CURRENT/bin/main*.py" "$PATH_CURRENT/*.sh" "$PATH_CURRENT/service_templates/*.sh" "$PATH_CURRENT/software_templates/*.sh" "$PATH_CURRENT/wizard_templates/*.sh")
FILE_DELETE=()
FILE_COPY_SOURCE=()
FILE_COPY_DEST=()

ADDON=0
ADDON_WEBPROXY=0
ADDON_START=0


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

  -s         Download nothing/skip
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
  echo -e "You have successfully installed ${APP_NAME}."
  _divider
}


_footer_next_steps() {
  _divider
  
  if [ $ADDON_START -eq 1 ]; then
    echo -e "To proceed with further installation and configuration, please open a web browser with the following address (depending on your network ip address):"
  else
    echo -e "To proceed with further installation and configuration, please start the program first."
    echo -e "Then open a web browser with the following address (depending on your network ip address):"
  fi

  if [ $ADDON_WEBPROXY -eq 1 ]; then
    IP_PROTO="https://"
    IP_PORT=""
  else
    IP_PROTO="http://"
    IP_PORT=":8080"
  fi

  IPLIST=$(ip -4 -o addr show scope global | awk '{gsub(/\/.*/,"",$4); print $4}')
  for s in $IPLIST; do
    echo -e "${IP_PROTO}${s}${IP_PORT}"
  done

  echo -e ""
  echo -e "Use the following login data:"
  echo -e "Username: ${DEFAULT_USER}"
  echo -e "Password: ${DEFAULT_PASSWORD}"

  echo -e ""
  echo -e "If a certificate warning is displayed, it can be ignored and confirmed. This is because the certificate was self-signed."

  echo -e ""
  echo -e "If the connection does not work then clear the browser cache and reopen the browser."

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
  echo -e "This script installs and creates the basic configuration for ${APP_NAME}."
  echo -e "The Quick Installer will guide you through a few easy steps."
  echo -e ""
  echo -e "The software is installed in the following folder: ${PATH_CURRENT}"
  echo -e "It is recommended to create a new custom folder manually. "
  echo -e ""
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
  echo -e "This script installs and creates the basic configuration for ${APP_NAME}."
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
  if [ "$DOWNLOAD_SKIP" = true ]; then
    return
  fi

 if [ -n "${DOWNLOAD_URL}" ]; then
    _download
    return
  fi

  echo -e ""
  echo -e "This installer can download the latest version from the internet and install it."
  while true; do
    read -p "Do you want to start download? [y/n]" YN
    case $YN in 
      [Yy]*)
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
        break;;
      [Nn]*)
        echo -e ""
        echo -e "No, using existing version."
        break;;
      *)
        echo -e ""
        echo -e "Please answer yes or no.";;
    esac
  done
}


_download_check() {
  if [ "$DOWNLOAD_SKIP" = true ]; then
    return
  fi

  echo -ne "Checking Download URL..."
  if [ -n "${DOWNLOAD_URL}" ]; then
    echo -e "${OK}"
    _download
  else
    echo -e "${NOK}"
  fi
}


_download() {
  echo -ne "Downloading..."
  if [ -n "${DOWNLOAD_URL}" ]; then
    if wget --no-check-certificate -q -O - "${DOWNLOAD_URL}" | tar -xz >> "${LOG_FILE}" 2>&1; then
      echo -e "${OK}"
      file="${PATH_CURRENT}/${DOWNLOAD_CMD}"
      echo -ne "Checking installer..."
      if [ -n "${DOWNLOAD_CMD}" ] && [ -e "${file}" ]; then
        echo -e "${OK}"
        echo -ne "Changing installer permissions/right..."
        if chmod +x "${file}" >> "${LOG_FILE}" 2>&1; then
          echo -e "${OK}"
          echo -e "Starting installer..."
          $file $DOWNLOAD_CMD_ARGS $DOWNLOAD_CMD_ARGS_USER
          exit 0
        else
          echo -e "${NOK}"
          _panic
        fi
      else
        echo -e "${NOK}"
        _panic
      fi
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


_return_check() {
  if [ "$1" -ne 0 ]; then
    echo -e "${FAIL}"
    _panic
  fi
}


_deps_system_update() {
  echo -ne "Updating sources..."
  if grep -q "debian" /etc/os-release; then
    if ! apt -y -q update >> "${LOG_FILE}" 2>&1; then
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


_deps_system_check() {
  echo -ne "Checking and installing dependencies system..."
  for dep in ${DEPS_SYSTEM[@]}; do
    if ! command -v "${dep}" >> "${LOG_FILE}" 2>&1; then
      _deps_system_install "${dep}"
      _return_check $?
    fi
  done
  echo -e "${OK}"
}


_deps_system_install() {
  if grep -q "debian" /etc/os-release; then
    apt -y -q install "$1" >> "${LOG_FILE}" 2>&1
  elif grep -q "fedora" /etc/os-release || grep -q "centos" /etc/os-release; then
    dnf -y -q install "$1" >> "${LOG_FILE}" 2>&1
  else
    echo -e "${FAIL}"
    echo -e "Cannot detect your distribution package manager."
    _panic
  fi
}


_deps_python_check() {
  echo -ne "Checking and installing dependencies python..."
  for dep in ${DEPS_PYTHON[@]}; do
    pip3 install "${dep}" >> "${LOG_FILE}" 2>&1
    _return_check $?
  done
  echo -e "${OK}"
}


_deps_file_check() {
  echo -ne "Checking files..."
  for dep in ${DEPS_FILE[@]}; do
    if [ ! -e "${dep}" ]; then
      echo "File '${dep}' missing." >> "${LOG_FILE}"
      echo -e "${FAIL}"
      echo -e "Needed files missing."
      _panic
    fi
  done
  echo -e "${OK}"
}


_python_check() {
  echo -ne "Checking python..."
  if pip3 --version >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    echo -e "Please install pip3 first"
    _panic
  fi
}


_addon_prompt() {
  LOOP=1
  options=("Terminal (Web-Terminal)" "Skip")
  while [ $LOOP -eq 1 ] && [ "${#options[@]}" -ne "1" ]; do
    echo -e ""
    echo -e "Select addons which should be used:"
    select opt in "${options[@]}"; do
      case $opt in
      "Terminal"*)
        unset -v 'options[0]'
        ADDON=1
        echo -e ""
        echo -e "Adding Terminal (Web-Terminal)...${OK}"
        break;;
      "Skip"*)
        LOOP=0
        echo -e ""
        break;;
      *)
        echo -e ""
        echo -e "Invalid choice!";;
      esac
    done
  done
}


_config_prompt() {
  if [ ! -f "$PATH_CURRENT/config.cfg" ] || [ ! -f "$PATH_CURRENT/config_auth.cfg" ]; then
    _config_install
  else
    while true; do
      echo -e ""
      echo -e "There is already an existing configuration."
      read -p "Do you want to overwrite this configuration? [y/n]" YN
      case $YN in 
        [Yy]*)
          echo -e ""
          _config_install
          break;;
        [Nn]*)
          echo -e ""
          break;;
        *)
          echo -e ""
          echo -e "Please answer yes or no.";;
      esac
    done
  fi
}


_config_install() {
  echo -ne "Installing config..."
  if python3 bin/main.py --defaultconfig >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


_webserver_prompt() {
  LOOP=1
  while [ $LOOP -eq 1 ]; do
    echo -e ""
    echo -e "Select a webserver to be used:"
    options=("Gunicorn (Recommended)" "Flask" "aiohttp")
    select opt in "${options[@]}"; do
      case $opt in
      "Gunicorn"*)
        echo -e ""
        _webserver_gunicorn
        LOOP=0
        break;;
      "Flask"*)
        echo -e ""
        _webserver_flask
        LOOP=0
        break;;
      "aiohttp"*)
        echo -e ""
        _webserver_aiohttp
        LOOP=0
        break;;
      *)
        echo -e ""
        echo -e "Invalid choice!";;
      esac
    done
  done
}


_webserver_config() {
  ADDON_WEBPROXY=1
  echo -ne "Configuring webserver for use with webproxy..."
  sed -i '/^\[/h;G;/connection_webserver_aiohttp/s/\(host = \).*/\1127.0.0.1/m;P;d' config.cfg
  sed -i '/^\[/h;G;/connection_webserver_aiohttp/s/\(port = \).*/\18080/m;P;d' config.cfg
  sed -i '/^\[/h;G;/connection_webserver_flask/s/\(host = \).*/\1127.0.0.1/m;P;d' config.cfg
  sed -i '/^\[/h;G;/connection_webserver_flask/s/\(port = \).*/\18080/m;P;d' config.cfg
  sed -i '/^\[/h;G;/connection_webserver_gunicorn/s/\(host = \).*/\1127.0.0.1/m;P;d' config.cfg
  sed -i '/^\[/h;G;/connection_webserver_gunicorn/s/\(port = \).*/\18080/m;P;d' config.cfg
  echo -e "${OK}"
}


_webserver_gunicorn() {
  echo -ne "Installing Gunicorn..."
  if pip3 install gunicorn flask flask_httpauth >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
  
  echo -ne "Configuring Gunicorn..."
  sed -i '/^\[/h;G;/connection_webserver_aiohttp/s/\(enabled = \).*/\1False/m;P;d' config.cfg
  sed -i '/^\[/h;G;/connection_webserver_flask/s/\(enabled = \).*/\1False/m;P;d' config.cfg
  sed -i '/^\[/h;G;/connection_webserver_gunicorn/s/\(enabled = \).*/\1True/m;P;d' config.cfg
  echo -e "${OK}"
  
  if [ $ADDON -eq 1 ]; then
    echo -ne "Installing Addons..."
    if pip3 install flask_socketio >> "${LOG_FILE}" 2>&1; then
      echo -e "${OK}"
    else
      echo -e "${NOK}"
      _panic
    fi
  fi
}


_webserver_flask() {
  echo -ne "Installing Flask..."
  if pip3 install flask flask_httpauth >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi

  echo -ne "Configuring Flask..."
  sed -i '/^\[/h;G;/connection_webserver_aiohttp/s/\(enabled = \).*/\1False/m;P;d' config.cfg >> "${LOG_FILE}"
  sed -i '/^\[/h;G;/connection_webserver_flask/s/\(enabled = \).*/\1True/m;P;d' config.cfg >> "${LOG_FILE}"
  sed -i '/^\[/h;G;/connection_webserver_gunicorn/s/\(enabled = \).*/\1False/m;P;d' config.cfg >> "${LOG_FILE}"
  echo -e "${OK}"

  if [ $ADDON -eq 1 ]; then
    echo -ne "Installing Addons..."
    if pip3 install flask_socketio >> "${LOG_FILE}" 2>&1; then
      echo -e "${OK}"
    else
      echo -e "${NOK}"
      _panic
    fi
  fi
}


_webserver_aiohttp() {
  echo -ne "Installing aiohttp..."
  if pip3 install aiohttp aiohttp_basicauth >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi

  echo -ne "Configuring aiohttp..."
  sed -i '/^\[/h;G;/connection_webserver_aiohttp/s/\(enabled = \).*/\1False/m;P;d' config.cfg >> "${LOG_FILE}"
  sed -i '/^\[/h;G;/connection_webserver_flask/s/\(enabled = \).*/\1False/m;P;d' config.cfg >> "${LOG_FILE}"
  sed -i '/^\[/h;G;/connection_webserver_gunicorn/s/\(enabled = \).*/\1True/m;P;d' config.cfg >> "${LOG_FILE}"
  echo -e "${OK}"
}


_webproxy_prompt() {
  LOOP=1
  while [ $LOOP -eq 1 ]; do
    echo -e ""
    echo -e "Select a webproxy to be used:"
    options=("Nginx (Recommended for production use)" "None")
    select opt in "${options[@]}"; do
      case $opt in
      "Nginx"*)
        echo -e ""
        _webproxy_nginx_prompt
        LOOP=0
        break;;
      "None"*)
        echo -e ""
        LOOP=0
        break;;
      *)
      echo -e ""
      echo -e "Invalid choice!";;
      esac
    done
  done
}


_webproxy_nginx_prompt() {
  echo -ne "Checking Nginx..."
  if ! command -v "nginx" >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
    _webproxy_nginx_install
    _webproxy_nginx_config_ssl_prompt
    _webproxy_nginx_config_dh_prompt
    _webproxy_nginx_config
    _webserver_config
  else
    echo -e "${OK}"
    echo -e ""
    echo -e "Nginx is already installed."
    echo -e "This wizard will create a new web page with HTTP & HTTPS."
    echo -e "You will need to check the configuration later to make sure there are no conflicts with the existing configuration."
    read -p "Do you want to proceed? [y/n]" YN
    while true; do
      case $YN in 
        [Yy]*)
          echo -e ""
          _webproxy_nginx_config_ssl_prompt
          _webproxy_nginx_config_dh_prompt
          _webproxy_nginx_config
          _webserver_config
          break;;
        [Nn]*)
          echo -e ""
          echo -e "Continue without configuring the webproxy."
          echo -e "This is not recommended for a productive environment!"
          echo -e "You have to do the configuration manually later!"
          break;;
        *)
          echo -e ""
          echo -e "Please answer yes or no.";;
      esac
    done
  fi
}


_webproxy_nginx_install() {
  if ! command -v "nginx" >> "${LOG_FILE}" 2>&1; then
    echo -ne "Installing Nginx..."
    _deps_system_install "nginx"
    _return_check $?
  fi
}


_webproxy_nginx_config_ssl_prompt() {
  echo -e "Configuring Nginx..."

  if [ ! -f "/etc/ssl/private/${APP_FILE}.key" ] && [ ! -f "/etc/ssl/certs/${APP_FILE}.crt" ]; then
    echo -e "Configuring SSL..."
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout "/etc/ssl/private/${APP_FILE}.key" -out "/etc/ssl/certs/${APP_FILE}.crt"
    echo -e "${OK}"
  else
    while true; do
      echo -e ""
      echo -e "There is already an existing SSL certificate."
      read -p "Do you want to generate a new one? [y/n]" YN
      case $YN in 
        [Yy]*)
          echo -e ""
          echo -e "Configuring SSL..."
          openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout "/etc/ssl/private/${APP_FILE}.key" -out "/etc/ssl/certs/${APP_FILE}.crt"
          echo -e "${OK}"
          break;;
        [Nn]*)
          echo -e ""
          break;;
        *)
          echo -e ""
          echo -e "Please answer yes or no.";;
      esac
    done
  fi
}


_webproxy_nginx_config_ssl() {
  echo -e "Configuring Nginx..."
  echo -e "Configuring SSL..."
  openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout "/etc/ssl/private/${APP_FILE}.key" -out "/etc/ssl/certs/${APP_FILE}.crt"  -subj "${DEFAULT_SSL}"
  echo -e "${OK}"
}


_webproxy_nginx_config_dh_prompt() {
  echo -e "Configuring Nginx..."

  if [ ! -f "/etc/nginx/${APP_FILE}.pem" ]; then
    while true; do
      echo -e ""
      echo -e "Do you want to create a Diffie–Hellman Key for a higher level of security?"
      read -p "This is going to take a long time. (~20 minutes) [y/n]" YN
      case $YN in 
        [Yy]*)
          echo -e ""
          echo -e "Configuring Diffie–Hellman Key..."
          openssl dhparam -out "/etc/nginx/${APP_FILE}.pem" 4096
          echo -e "${OK}"
          break;;
        [Nn]*)
          echo -e ""
          break;;
        *)
          echo -e ""
          echo -e "Please answer yes or no.";;
      esac
    done
  else
    while true; do
      echo -e ""
      echo -e "There is already an existing Diffie–Hellman Key."
      echo -e "Do you want to generate a new one?"
      read -p "This is going to take a long time. (~20 minutes) [y/n]" YN
      case $YN in 
        [Yy]*)
          echo -e ""
          echo -e "Configuring Diffie–Hellman Key..."
          openssl dhparam -out "/etc/nginx/${APP_FILE}.pem" 4096
          echo -e "${OK}"
          break;;
        [Nn]*)
          echo -e ""
          break;;
        *)
          echo -e ""
          echo -e "Please answer yes or no.";;
      esac
    done
  fi
}


_webproxy_nginx_config_dh() {
  echo -e "Configuring Nginx..."
  echo -ne "Configuring Diffie–Hellman Key..."
  openssl dhparam -out "/etc/nginx/${APP_FILE}.pem" 4096
  echo -e "${OK}"
}


_webproxy_nginx_config() {
  echo -e "Configuring Nginx..."
  echo -ne "Creating web site config..."

  if [ $ADDON -eq 1 ]; then
    COMMENT_ADDON=""
  else
    COMMENT_ADDON="#"
  fi

  if [ -f "/etc/nginx/${APP_FILE}.pem" ]; then
    COMMENT_DHPARAM=""
  else
    COMMENT_DHPARAM="#"
  fi

  FILE_DEFAULT="/etc/nginx/sites-enabled/default"
  FILE_AVAILABLE="/etc/nginx/sites-available/${APP_FILE}.conf"
  FILE_ENABLED="/etc/nginx/sites-enabled/${APP_FILE}.conf"

cat <<EOF > ${FILE_AVAILABLE}
server {
  listen 80;
  server_name _;
  return 301 https://$host$request_uri;
}

server {
  listen 443 ssl;
  listen [::]:443 ssl;
  ssl_certificate /etc/ssl/certs/${APP_FILE}.crt;
  ssl_certificate_key /etc/ssl/private/${APP_FILE}.key;
  ${COMMENT_DHPARAM}ssl_dhparam /etc/nginx/${APP_FILE}.pem;
  server_name _;

  auth_basic "${APP_NAME}";
  auth_basic_user_file /var/www/${APP_FILE}.htpasswd;

  location ~ ^/index?.*[^.css|.html|.js]$ {
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header HOST \$http_host;
    proxy_set_header X-Forwarded-Host \$http_host;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_pass http://127.0.0.1:8080;
    proxy_redirect off;
  }

  ${COMMENT_ADDON}location /socket.io {
  ${COMMENT_ADDON}  proxy_set_header X-Real-IP \$remote_addr;
  ${COMMENT_ADDON}  proxy_set_header HOST \$http_host;
  ${COMMENT_ADDON}  proxy_set_header X-Forwarded-Host \$http_host;
  ${COMMENT_ADDON}  proxy_set_header X-Forwarded-Proto \$scheme;
  ${COMMENT_ADDON}  proxy_pass http://127.0.0.1:8181;
  ${COMMENT_ADDON}  proxy_redirect off;
  ${COMMENT_ADDON}}

  location / {
    root /var/www/${APP_FILE};
  }
}

EOF

  if [ -f "$FILE_AVAILABLE" ]; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi


  echo -ne "Enabling web site config..."
  if ln -sf "$FILE_AVAILABLE" -T "$FILE_ENABLED" >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi


  if [ -f "$FILE_DEFAULT" ]; then
    echo -ne "Disabling default web site config..."
    if rm -f "$FILE_DEFAULT" >> "${LOG_FILE}" 2>&1; then
      echo -e "${OK}"
    else
      echo -e "${NOK}"
      _panic
    fi
  fi


  echo -ne "Copying web site files..."
  if ! [ -d "/var/www/${APP_FILE}" ]; then
    if mkdir "/var/www/${APP_FILE}" >> "${LOG_FILE}" 2>&1; then
      echo -ne ""
    else
      echo -e "${NOK}"
      _panic
    fi
  else
    if rm -R -f "/var/www/${APP_FILE}/*" >> "${LOG_FILE}" 2>&1; then
      echo -ne ""
    else
      echo -e "${NOK}"
      _panic
    fi
  fi

  if cp -a "${PATH_CURRENT}/www/." "/var/www/${APP_FILE}/" >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi

  echo -ne "Changing file ownership..."
  if chown -cR www-data "/var/www/${APP_FILE}" >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi

  echo -ne "Restarting Nginx..."
  if systemctl restart nginx >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


_password_prompt() {
  while true; do
    echo -e ""
    echo -e "Define the default admin password."
    echo -e "New Password:"
    read -sp "" VAR1
    echo -e "Retype new password:"
    read -sp "" VAR2
    if [ "$VAR1" = "$VAR2" ]; then
      echo -e ""
      echo -ne "Updating password..."
      if python3 bin/main.py --user "admin" --password "${VAR1}" >> "${LOG_FILE}" 2>&1; then
        DEFAULT_PASSWORD="${VAR1}"
        echo -e "${OK}"
        break
      else
        echo -e "${NOK}"
        _panic
      fi
    else
      echo -e ""
      echo -e "Sorry, passwords do not match."
    fi
  done
}


_password_default() {
  echo -ne "Updating password..."
  if python3 bin/main.py --user "${DEFAULT_USER}" --password "${DEFAULT_PASSWORD}" >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


_user_prompt() {
  while true; do
    echo -e ""
    read -p "Do you want to add users? [y/n]" YN
    case $YN in 
      [Yy]*)
        read -p "Username:" USER
        echo -e "Password:"
        read -sp "" VAR1
        echo -e "Retype password:"
        read -sp "" VAR2
        if [ "$VAR1" = "$VAR2" ]; then
          echo -e ""
          echo -ne "Adding user..."
          if python3 bin/main.py --user "${USER}" --password "${VAR1}" >> "${LOG_FILE}" 2>&1; then
            echo -e "${OK}"
          else
            echo -e "${NOK}"
          fi
        else
          echo -e ""
          echo "Password ${FAIL} (Both passwords do not match.)"
          echo "Please try again."
        fi
        ;;
      [Nn]*)
        echo -e ""
        echo -e "No, skip user setup."
        break;;
      *)
        echo -e ""
        echo -e "Please answer yes or no.";;
    esac
  done
}


_service_install() {
  echo -ne "Installing service..."
  systemctl stop $APP_FILE >> "${LOG_FILE}" 2>&1
  FILE="/etc/systemd/system/${APP_FILE}.service"

cat <<EOF > ${FILE}
[Unit]
Description=${APP_NAME} Daemon
After=multi-user.target
[Service]
# ExecStartPre=/bin/sleep 10
Type=simple
Restart=always
RestartSec=3
User=root
ExecStart=${PATH_CURRENT}/bin/main.py --service
[Install]
WantedBy=multi-user.target
EOF

  if [ -f "$FILE" ]; then
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

  echo -ne "Enabling service..."
  if systemctl enable $APP_FILE >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


_service_addon_install() {
  if [ $ADDON -ne 1 ]; then
    return
  fi

  echo -ne "Installing addon service..."
  systemctl stop $APP_FILE-addon >> "${LOG_FILE}" 2>&1
  FILE="/etc/systemd/system/${APP_FILE}-addon.service"

cat <<EOF > ${FILE}
[Unit]
Description=${APP_NAME} Daemon
After=multi-user.target
[Service]
# ExecStartPre=/bin/sleep 10
Type=simple
Restart=always
RestartSec=3
User=root
ExecStart=${PATH_CURRENT}/bin/main_terminal.py --service
[Install]
WantedBy=multi-user.target
EOF

  if [ -f "$FILE" ]; then
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

  echo -ne "Enabling addon service..."
  if systemctl enable $APP_FILE-addon >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


_service_uninstall() {
  systemctl stop $APP_FILE >> "${LOG_FILE}" 2>&1
  systemctl disable $APP_FILE >> "${LOG_FILE}" 2>&1
  rm "/etc/systemd/system/${APP_FILE}.service" >> "${LOG_FILE}" 2>&1
  systemctl daemon-reload >> "${LOG_FILE}" 2>&1
}


_service_addon_uninstall() {
  systemctl stop $APP_FILE-addon >> "${LOG_FILE}" 2>&1
  systemctl disable $APP_FILE-addon >> "${LOG_FILE}" 2>&1
  rm "/etc/systemd/system/${APP_FILE}-addon.service" >> "${LOG_FILE}" 2>&1
  systemctl daemon-reload >> "${LOG_FILE}" 2>&1
}


_service_prompt() {
  while true; do
    echo -e ""
    echo -e "Do you want to install ${APP_NAME} as a system service?"
    read -p "This will start the program automatically at system startup. [y/n]" YN
    case $YN in 
      [Yy]*)
        echo -e ""
        _service_install
        _service_addon_install
        _service_start_prompt
        break;;
      [Nn]*)
        echo -e ""
        _service_uninstall
        _service_addon_uninstall
        break;;
      *)
        echo -e ""
        echo -e "Please answer yes or no.";;
    esac
  done
}


_service_start_prompt() {
  while true; do
    echo -e ""
    read -p "Do you want to start ${APP_NAME} now? [y/n]" YN
    case $YN in 
      [Yy]*)
        echo -e ""
        _service_start
        _service_addon_start
        break;;
      [Nn]*)
        echo -e ""
        break;;
      *)
        echo -e ""
        echo -e "Please answer yes or no.";;
    esac
  done
}


_service_start() {
  ADDON_START=1
  echo -ne "Starting service..."
  if systemctl start $APP_FILE >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


_service_addon_start() {
  if [ $ADDON -ne 1 ]; then
    return
  fi

  echo -ne "Starting addon service..."
  if systemctl start $APP_FILE-addon >> "${LOG_FILE}" 2>&1; then
    echo -e "${OK}"
  else
    echo -e "${NOK}"
    _panic
  fi
}


##############################################################################################################
# Setup/Start


UNATTENDED=false
DOWNLOAD_SKIP=false


while getopts ":hsvurd" opt; do
  case "${opt}" in
    v) _version;;
    s) DOWNLOAD_SKIP=true;;
    u)
       UNATTENDED=true
       DOWNLOAD_CMD_ARGS_USER=" -u";;
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

#!/bin/bash


source vendor/colors.sh


APP_FILE="configinterfacetool"

DOWNLOAD_URL_SERVER="https://raw.githubusercontent.com/SebastianObi/ConfigInterfaceTool/main/releases/"
DOWNLOAD_URL_FILE_RELEASE="release_update.tar.gz"
DOWNLOAD_URL_FILE_DEV="dev_update.tar.gz"
DOWNLOAD_URL=""
PATH_CURRENT=$(dirname $(realpath $0))
PATH_CURRENT=${PATH_CURRENT%/*}
PERMISSION_OWNER=("$PATH_CURRENT/*")
PERMISSION_RIGHTS=("$PATH_CURRENT/bin/main*.py" "$PATH_CURRENT/*.sh" "$PATH_CURRENT/service_templates/*.sh" "$PATH_CURRENT/software_templates/*.sh" "$PATH_CURRENT/wizard_templates/*.sh")
FILE_DELETE=("/var/www/${APP_FILE}/*")
FILE_COPY_SOURCE=("$PATH_CURRENT/www/.")
FILE_COPY_DEST=("/var/www/${APP_FILE}/")



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
      LOOP=0
      break;;
    "Development"*)
      echo -e ""
      echo -e "Ok, downloading the latest development version."
      DOWNLOAD_URL="${DOWNLOAD_URL_SERVER}${DOWNLOAD_URL_FILE_DEV}"
      LOOP=0
      break;;
    *)
      echo -e ""
      echo -e "Invalid choice!";;
    esac
  done
done


echo -ne "Changing path..."
if ! cd $PATH_CURRENT 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Downloading..."
if [ -n "${DOWNLOAD_URL}" ]; then
  if wget --no-check-certificate -q -O - "${DOWNLOAD_URL}" | tar -xz >> "${LOG_FILE}" 2>&1; then
    echo -e " ${GREEN}OK!${NC}"
  else
      echo -e " ${RED}failed!${NC}"
      exit 1
  fi
else
   echo -e " ${RED}failed!${NC}"
   exit 1
fi


echo -ne "Deleting files..."
for i in ${!FILE_DELETE[@]}; do
  if ! rm -R -f "${FILE_DELETE[$i]}" >> "${LOG_FILE}" 2>&1; then
    echo -e " ${RED}failed!${NC}"
    exit 1
  fi
done
echo -e "${OK}"


echo -ne "Copying files..."
for i in ${!FILE_COPY_SOURCE[@]}; do
  if [ -d "${FILE_COPY_DEST[$i]}" ]; then
    if ! cp -a "${FILE_COPY_SOURCE[$i]}" "${FILE_COPY_DEST[$i]}" >> "${LOG_FILE}" 2>&1; then
      echo -e " ${RED}failed!${NC}"
      exit 1
    fi
  fi
done
echo -e "${OK}"


echo -ne "Changing file permissions/owner to '$(whoami)'..."
for file in ${PERMISSION_OWNER[@]}; do
  if [ -e "${file}" ]; then
    if ! chown -cR "$(whoami)" "${file}" >> "${LOG_FILE}" 2>&1; then
      echo -e " ${RED}failed!${NC}"
      exit 1
    fi
  fi
done
echo -e " ${GREEN}OK!${NC}"


echo -ne "Changing file permissions/right..."
for file in ${PERMISSION_RIGHTS[@]}; do
  if [ -e "${file}" ]; then
    if ! chmod +x "${file}" >> "${LOG_FILE}" 2>&1; then
      echo -e " ${RED}failed!${NC}"
      exit 1
    fi
  fi
done
echo -e " ${GREEN}OK!${NC}"


echo -e ""
echo -e "To activate the changes, the system must be rebooted."


echo -e "Finished!"


exit 0
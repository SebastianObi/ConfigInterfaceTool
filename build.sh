#!/bin/bash


_build_full() {
  echo -e "Part full..."
  tar --exclude="${EXCLUDE_EXAMPLES}" --exclude='./.git' --exclude='./backup/*auto_backup*' --exclude='./backup/*user_backup*' --exclude='./cache/*' --exclude='./docs' --exclude='./releases' --exclude='./test' --exclude='./tmp/*' --exclude='./config.cfg' --exclude='./config_auth.cfg' --exclude='./README.md' -czf ${FILE}_full.tar.gz .
}


_build_update() {
  echo -e "Part update..."
  tar --exclude="${EXCLUDE_EXAMPLES}" --exclude='./.git' --exclude='./backup/*' --exclude='./cache/*' --exclude='./config_files/*' --exclude='./config_templates/*' --exclude='./docs' --exclude='./releases' --exclude='./service_files/*' --exclude='./service_templates/*' --exclude='./software_files/*' --exclude='./software_templates/*' --exclude='./test' --exclude='./tmp/*' --exclude='./wizard_files/*' --exclude='./wizard_templates/*' --exclude='./www/downloads' --exclude='./config.cfg' --exclude='./config_auth.cfg' --exclude='./README.md' -czf ${FILE}_update.tar.gz .
}


_build_config() {
  echo -e "Part config..."
  tar --exclude="${EXCLUDE_EXAMPLES}" -czf ${FILE}_config.tar.gz ./backup/factory_backup.cfg ./backup/factory_backup.cfg.tar ./config_files/* ./config_templates/* ./service_files/* ./service_templates/* ./software_files/* ./software_templates/* ./wizard_files/* ./wizard_templates/*
}


if [[ $EUID -ne 0 ]]; then
  echo -e "Error: You need to run this script as root (UID=0)"
  exit 1
fi


if [ -p /dev/stdin ]; then
  echo -e "Error: This script can't be piped!"
  exit 1
fi


if ! mkdir -p releases; then
  echo "Error creating 'releases' dir, exiting now."
  exit 1
fi


while true; do
  echo -e ""
  read -p "Do you want to include examples? [y/n]" YN
  case $YN in 
    [Yy]*)
      echo -e "Ok"
      EXCLUDE_EXAMPLES=""
      break;;
    [Nn]*)
      echo -e "No"
      EXCLUDE_EXAMPLES="example_*"
      break;;
    *)
      echo -e ""
      echo -e "Please answer yes or no.";;
  esac
done


echo -e ""
echo -e "What do you want to build?:"
options=("all" "development" "release")
select opt in "${options[@]}"; do
  case $opt in
  "all"*)
    echo -e ""
    echo -e "Building release..."
    FILE="releases/release"
    _build_full
    _build_update
    _build_config
    echo -e ""
    echo -e "Building development..."
    FILE="releases/dev"
    _build_full
    _build_update
    _build_config
    break;;
  "development"*)
    echo -e ""
    echo -e "Building development..."
     FILE="releases/dev"
    _build_full
    _build_update
    _build_config
    break;;
  "release"*)
    echo -e ""
    echo -e "Building release..."
    FILE="releases/release"
    _build_full
    _build_update
    _build_config
    break;;
  *)
    echo -e ""
    echo -e "Invalid choice!"
    exit 1;;
  esac
done


echo -e ""
echo -e "Copying files..."
cp -a "install.sh" "releases/install.sh"
cp -a "install_online.sh" "releases/install_online.sh"
cp -a "update.sh" "releases/update.sh"
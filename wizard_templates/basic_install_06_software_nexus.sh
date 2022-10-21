#!/bin/bash


source vendor/colors.sh


################################################################################################
# Check script execution.
################################################################################################


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


################################################################################################
# Check linux version.
################################################################################################


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
  echo -e " ${RED}failed!${NC}"
  echo -e "Unsupported Linux distribution"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


################################################################################################
# Check existing installation.
################################################################################################


if [ -d "/root/nexus" ]; then
  while true; do
    echo -e ""
    echo -e "There is already an existing installation on your system."
    read -p "Do you want to replace it? [y/n]" YN
    case $YN in 
      [Yy]*)
        echo -ne "Ok, removing old installation..."
        if ! rm -R -f "/root/nexus" >> "${LOG_FILE}" 2>&1; then
            echo -e " ${RED}failed!${NC}"
            exit 1
        fi
        echo -e " ${GREEN}OK!${NC}"
        break;;
      [Nn]*)
        echo -e "No, exiting now."
        exit 1
        break;;
      *)
        echo -e ""
        echo -e "Please answer yes or no.";;
    esac
  done
fi


################################################################################################
# Full system update,some helper packages, clean up and sudo.
################################################################################################


# Not needed for use with ConfigInterface.

#echo -ne "Updating packet repository..."
#if ! apt -y -q update >> "${LOG_FILE}" 2>&1; then
#  echo -e " ${RED}failed!${NC}"
#  exit 1
#fi
#echo -e " ${GREEN}OK!${NC}"


#echo -ne "Updating system..."
#if ! ( apt -y -q -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade && apt -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" full-upgrade ) >> "${LOG_FILE}" 2>&1; then
#  echo -e " ${RED}failed!${NC}"
#  exit 1
#fi
#echo -e " ${GREEN}OK!${NC}"


#echo -ne "Cleanup system..."
#if ! ( apt -y -q clean && apt -y -q autoclean && apt -y -q autoremove ) >> "${LOG_FILE}" 2>&1; then
#  echo -e " ${RED}failed!${NC}"
#  exit 1
#fi
#echo -e " ${GREEN}OK!${NC}"


#echo -ne "Installing tools..."
#if !apt -y -q install mc screen >> "${LOG_FILE}" 2>&1; then
#  echo -e " ${RED}failed!${NC}"
#  exit 1
#fi
#echo -e " ${GREEN}OK!${NC}"


#echo -ne "Changing user permissions..."
#if !usermod -aG sudo pi >> "${LOG_FILE}" 2>&1; then
#  echo -e " ${RED}failed!${NC}"
#  exit 1
#fi
#echo -e " ${GREEN}OK!${NC}"


################################################################################################
# Assign alsa names to USB Ports.
################################################################################################


echo -ne "Configuring audio interface..."

# RPi 2 Model B v1.1 [Radiobox2]
if [[ $MODEL == *"Pi 2"* ]]; then
cat <<EOF > "/etc/udev/rules.d/85-my-usb-audio.rules"
SUBSYSTEM!="sound", GOTO="my_usb_audio_end"
ACTION!="add", GOTO="my_usb_audio_end"
DEVPATH=="/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2:1.0/sound/card?", ATTR{id}="Alpha"
DEVPATH=="/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.3/1-1.3:1.0/sound/card?", ATTR{id}="Bravoe"
DEVPATH=="/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4/1-1.4:1.0/sound/card?", ATTR{id}="Charlie"
DEVPATH=="/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.5/1-1.5:1.0/sound/card?", ATTR{id}="Delta"
LABEL="my_usb_audio_end"
EOF
fi

# RPi 1 Model B+ v1.2 [Radiobox2]
if [[ $MODEL == *"Pi 1"* ]]; then
cat <<EOF > "/etc/udev/rules.d/85-my-usb-audio.rules"
SUBSYSTEM!="sound", GOTO="my_usb_audio_end"
ACTION!="add", GOTO="my_usb_audio_end"
DEVPATH=="/devices/platform/soc/20980000.usb/usb1/1-1/1-1.2/1-1.2:1.0/sound/card?", ATTR{id}="Alpha"
DEVPATH=="/devices/platform/soc/20980000.usb/usb1/1-1/1-1.3/1-1.3:1.0/sound/card?", ATTR{id}="Bravo"
DEVPATH=="/devices/platform/soc/20980000.usb/usb1/1-1/1-1.4/1-1.4:1.0/sound/card?", ATTR{id}="Charlie"
DEVPATH=="/devices/platform/soc/20980000.usb/usb1/1-1/1-1.5/1-1.5:1.0/sound/card?", ATTR{id}="Delta"
LABEL="my_usb_audio_end"
EOF
fi

# OrangePI4 LTS [Orange]
if [[ $MODEL == *"OrangePI4"* ]]; then
cat <<EOF > "/etc/udev/rules.d/85-my-usb-audio.rules"
SUBSYSTEM!="sound", GOTO="my_usb_audio_end"
ACTION!="add", GOTO="my_usb_audio_end"
DEVPATH=="/devices/platform/usb@fe900000/fe900000.usb/xhci-hcd.1.auto/usb1/1-1/1-1:1.0/sound/card?", ATTR{id}="Alpha"
DEVPATH=="/devices/platform/fe3e0000.usb/usb4/4-1/4-1:1.0/sound/card?", ATTR{id}="Bravo"
DEVPATH=="/devices/platform/fe3a0000.usb/usb8/8-1/8-1:1.0/sound/card?", ATTR{id}="Charlie"
LABEL="my_usb_audio_end"
EOF
fi

# RPi 4 Model B 8GB [Radiobox]
if [[ $MODEL == *"Pi 4"* ]]; then
cat <<EOF > "/etc/udev/rules.d/85-my-usb-audio.rules"
SUBSYSTEM!="sound", GOTO="my_usb_audio_end"
ACTION!="add", GOTO="my_usb_audio_end"
DEVPATH=="/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.3/1-1.3:1.0/sound/card?", ATTR{id}="Alpha"
DEVPATH=="/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.4/1-1.4:1.0/sound/card?", ATTR{id}="Bravo"
DEVPATH=="/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.1/1-1.1:1.0/sound/card?", ATTR{id}="Charlie"
DEVPATH=="/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.2/1-1.2:1.0/sound/card?", ATTR{id}="Delta"
LABEL="my_usb_audio_end"
EOF
fi

echo -e " ${GREEN}OK!${NC}"


################################################################################################
# Install docker.
################################################################################################


echo -ne "Installing docker..."
if ! curl -fsSL https://get.docker.com | sh >> "${LOG_FILE}" 2>&1; then
  if ! curl -fsSL https://get.docker.com | sh >> "${LOG_FILE}" 2>&1; then
    echo -e " ${RED}failed!${NC}"
    exit 1
  fi
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Checking docker..."
if ! docker ps >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Checking docker compose..."
if ! docker compose >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


################################################################################################
# Install Nexus Container.
################################################################################################


echo -ne "Entering folder '/root/'..."
if ! cd /root/ >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


if ! command -v git >> "${LOG_FILE}" 2>&1; then
  echo -ne "Installing git..."
  if ! apt -y -q install git >> "${LOG_FILE}" 2>&1; then
    echo -e " ${RED}failed!${NC}"
    exit 1
  fi
  echo -e " ${GREEN}OK!${NC}"
fi


echo -ne "Configuring git..."
if ! git config --global pull.rebase false >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


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
      echo -ne "Downloading..."
      if ! git clone https://github.com/HarlekinSimplex/nexus.git >> "${LOG_FILE}" 2>&1; then
        echo -e " ${RED}failed!${NC}"
        exit 1
      fi
      echo -e " ${GREEN}OK!${NC}"
      LOOP=0
      break;;
    "Development"*)
      echo -e ""
      echo -e "Ok, downloading the latest development version."
      echo -ne "Downloading..."
      if ! git clone -b development https://github.com/HarlekinSimplex/nexus.git >> "${LOG_FILE}" 2>&1; then
        echo -e " ${RED}failed!${NC}"
        exit 1
      fi
      echo -e " ${GREEN}OK!${NC}"
      LOOP=0
      break;;
    *)
      echo -e ""
      echo -e "Invalid choice!";;
    esac
  done
done


################################################################################################
# Configure and test Nexus Container.
################################################################################################


echo -ne "Entering folder 'nexus'..."
if ! cd nexus >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Creating environment variables..."
if ! bash create_env.sh >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Preparing for first start (test) (This may take a while)..."
if ! docker compose up -d >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


echo -ne "Waiting for first start (test) (This may take a while)..."
docker compose logs > "${LOG_FILE}"
while [ "$( docker inspect -f '{{.State.Status}}' nexus-server )" != "running" ]; do
  docker compose logs > "${LOG_FILE}"
  echo -ne "."
  sleep 2
done
echo -e " ${GREEN}OK!${NC}"


echo -ne "Shutdown (test)..."
if ! docker compose down >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


# Only needed for use with ConfigInterface.
# Delete configuration which will be replaced later by the ConfigInterface.

echo -ne "Deleting default configuration..."
if ! rm -f "/root/nexus/.env" "/root/nexus/nexus_root/.nexus/config" "/root/nexus/nexus_root/.nomadnetwork/config" "/root/nexus/nexus_root/.nomadnetwork/storage/pages/index.mu" "/root/nexus/nexus_root/.reticulum/config" >> "${LOG_FILE}" 2>&1; then
  echo -e " ${RED}failed!${NC}"
  exit 1
fi
echo -e " ${GREEN}OK!${NC}"


################################################################################################
# Finished/End.
################################################################################################


echo -e "Finished!"


exit 0
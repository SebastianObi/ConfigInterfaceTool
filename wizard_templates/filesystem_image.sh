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


echo -e "Please connect the destination device you wish to use."
read -p "Hit enter when it is connected."


DEVICE_PATH=()
DEVICE_NAME=()
while read s; do
  DEVICE_PATH+=("$s")
done < <(fdisk -l -o Device | grep '^/dev/sd[a-z][0-9]')
while read s; do
  DEVICE_NAME+=("$s")
done < <(fdisk -l -o Device,Size,Type | grep '^/dev/sd[a-z][0-9]')


if [ ${#DEVICE_PATH[@]} -eq 0 ]; then
  echo -e "Could not find any devices, exiting now."
  exit 1
fi


echo -e "What is your destination device?"
select PORT in "${DEVICE_NAME[@]}"; do
  REPLY=$REPLY-1
  if [[ ${DEVICE_NAME[$REPLY]} ]]; then
    echo -e "Ok, using device: ${DEVICE_NAME[$REPLY]}"
    echo -e ""
    read -p "Do you want to proceed? [y/n]" YN
    case $YN in 
      [Yy])
        echo -e "Ok, proceeding..."

        if mountpoint -q /mnt/clone/; then
          if ! umount /mnt/clone/; then
            echo -e "Error, exiting now."
            exit 1
          fi
        fi

        if ! mkdir -p /mnt/clone; then
          echo -e "Error, exiting now."
          exit 1
        fi

        if ! mount ${DEVICE_PATH[$REPLY]} /mnt/clone/; then
          echo -e "Error, exiting now."
          exit 1
        fi

        FILE="$(hostname)-$(date +%Y%m%d-%H%M%S).img"

        echo -e "Creating image file '${FILE}'..."
        if ! dd if=/dev/mmcblk0 of=/mnt/clone/${FILE} bs=1M status=progress; then
          umount /mnt/clone/
          echo -e "Error, exiting now."
          exit 1
        fi

        echo -e "Shrinking image file '${FILE}'..."
        if ! vendor/pishrink.sh -z /mnt/clone/${FILE}; then
          umount /mnt/clone/
          echo -e "Error, exiting now."
          exit 1
        fi

        if ! umount /mnt/clone/; then
          echo -e "Error, exiting now."
          exit 1
        fi

        echo -e "Finished!"
        exit 0
        ;;

      [Nn])
        echo -e "No, exiting now."
        exit 1
        ;;

      *)
        echo -e "Please answer yes or no."
        ;;
    esac
  else
    echo -e "Could not find specified device, exiting now."
    exit 1
  fi
done


echo -e "Finished!"


exit 0
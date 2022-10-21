#!/bin/bash

source vendor/colors.sh


convert_bytes_to_human () {
  echo $1 | awk '{xin=$1;if(xin==0){print "0 B";}else{x=(xin<0?-xin:xin);s=(xin<0?-1:1);split("B KiB MiB GiB TiB PiB",type);for(i=5;y < 1;i--){y=x/(2^(10*i));}print y*s " " type[i+2];};}'
}


if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}Error:${NC} You need to run this script as root (UID=0)"
  exit 1
fi


if [ -p /dev/stdin ]; then
  echo -e "${RED}Error:${NC} This script can't be piped!"
  exit 1
fi


echo -e "Please connect the destination device (sd-card, usb-stick) you wish to use."
read -p "Hit enter when it is connected."


DEVICE_PATH=()
DEVICE_DISK=()
DEVICE_NAME=()
DEVICE_SIZE=()
while IFS= read -r -d $'\0' device; do
  DEVICE_PATH+=($device)
  device=${device/\/dev\//}
  DEVICE_DISK+=($device)
  DEVICE_NAME+=("`cat "/sys/class/block/$device/device/model"`")
  size=$((`cat "/sys/class/block/$device/size"` * 512))
  DEVICE_SIZE+=("$(convert_bytes_to_human "${size}")")
done < <(find "/dev/" -regex '/dev/sd[a-z]\|/dev/vd[a-z]\|/dev/hd[a-z]' -print0 | sort -z)

unset DEVICES
for i in `seq 0 $((${#DEVICE_DISK[@]}-1))`; do
    DEVICES+=("${DEVICE_DISK[$i]} ${DEVICE_NAME[$i]} ${DEVICE_SIZE[$i]}")
done


if [ ${#DEVICES[@]} -eq 0 ]; then
  echo -e "Could not find any devices, exiting now."
  exit 1
fi


echo -e "What is your destination device?"
select PORT in "${DEVICES[@]}"; do
  REPLY=$REPLY-1
  if [[ ${DEVICES[$REPLY]} ]]; then
    echo -e "Ok, using device: ${DEVICES[$REPLY]}"
    echo -e ""
    echo -e "WARNING: All data on the destination device will be deleted!"
    echo -e ""
    read -p "Do you want to proceed? [y/n]" YN
    case $YN in 
      [Yy])
        echo -e "Ok, proceeding..."
        vendor/rpi-clone.sh ${DEVICE_DISK[$REPLY]} -f -U
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
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


USERS=()
USERLIST=$(python3 ../bin/main.py --userget)
for s in $USERLIST; do
  USERS+=("$s")
done


if [ ${#USERS[@]} -eq 0 ]; then
  echo -e "Could not find any user, exiting now."
  exit 1
fi


while true; do
  if [ ${#USERS[@]} -eq 1 ]; then
    REPLY=0
    echo -e ""
    echo -e "Define the password for user '${USERS[$REPLY]}':"
    read -sp "" VAR
    echo -e ""
    echo -ne "Updating password..."
    if python3 ../bin/main.py --user "${USERS[$REPLY]}" --password "${VAR}" >> /dev/null 2>&1; then
      echo -e " ${GREEN}OK!${NC}"
      break
    else
      echo -e " ${RED}failed!${NC}"
      break
    fi
  else
    echo -e "Which user would you like to edit?"
    select USER in "${USERS[@]}"; do
      REPLY=$REPLY-1
      if [[ ${USERS[$REPLY]} ]]; then
        echo -e ""
        echo -e "Define the password for user '${USERS[$REPLY]}':"
        read -sp "" VAR
        echo -e ""
        echo -ne "Updating password..."
        if python3 ../bin/main.py --user "${USERS[$REPLY]}" --password "${VAR}" >> /dev/null 2>&1; then
          echo -e " ${GREEN}OK!${NC}"
          break
        else
          echo -e " ${RED}failed!${NC}"
          break
        fi
      fi
    done
  fi

  if [ ${#USERS[@]} -eq 1 ]; then
    break
  fi

  echo -e ""
  read -p "Do you want to edit another user? [y/n]" YN
    case $YN in 
      [Yy]*)
        ;;
      [Nn]*)
        break;;
      *)
        echo -e ""
        echo -e "Please answer yes or no.";;
    esac
done


echo -e "Finished!"


exit 0
#!/bin/bash


source vendor/colors.sh


echo -e "Hello!"
echo -e ""
read -p "Hit enter to start."


echo -e ""
read -p "Do you want to proceed? [y/n]" YN
case $YN in 
  [Yy])
    echo -e "Ok, proceeding..."
    ;;
  [Nn])
    echo -e "No, exiting now."
    exit 1
    ;;
  *)
    echo -e "Please answer yes or no."
    ;;
esac


echo -e ""
read -p "Do you want to proceed? (y/n)" YN
case $YN in 
  [Yy])
    echo -e "Ok, proceeding..."
    ;;
  [Nn])
    echo -e "No, exiting now."
    exit 1
    ;;
  *)
    echo -e "Please answer yes or no."
    ;;
esac


echo -e ""
read -p "Do you want to proceed? [yes/no]" YN
case $YN in 
  yes)
    echo -e "Ok, proceeding..."
    ;;
  no)
    echo -e "No, exiting now."
    exit 1
    ;;
  *)
    echo -e "Please answer yes or no."
    ;;
esac


echo -e ""
read -p "Do you want to proceed? (yes/no)" YN
case $YN in 
  yes)
    echo -e "Ok, proceeding..."
    ;;
  no)
    echo -e "No, exiting now."
    exit 1
    ;;
  *)
    echo -e "Please answer yes or no."
    ;;
esac


echo -e ""
read -p "Do you want to proceed? [y/n/c]" YN
case $YN in 
  [Yy])
    echo -e "Ok, proceeding..."
    ;;
  [Nn])
    echo -e "No, exiting now."
    exit 1
    ;;
  [Cc])
    echo -e "Cancel, exiting now."
    exit 1
    ;;
  *)
    echo -e "Please answer yes or no."
    ;;
esac


echo -e ""
read -p "Do you want to proceed? (y/n/c)" YN
case $YN in 
  [Yy])
    echo -e "Ok, proceeding..."
    ;;
  [Nn])
    echo -e "No, exiting now."
    exit 1
    ;;
  [Cc])
    echo -e "Cancel, exiting now."
    exit 1
    ;;
  *)
    echo -e "Please answer yes or no."
    ;;
esac


echo -e ""
echo -e "What option do you want to choose?"
echo -e "1. Option 1"
echo -e "2. Option 2"
echo -e "3. Option 3"
read OPTION
case $OPTION in
  [1])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [2])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [3])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  *)
    echo -e "Error: That option does not exist, exiting now."
    exit 1
    ;;
esac


echo -e ""
echo -e "What option do you want to choose?"
echo -e "[1] Option 1"
echo -e "[2] Option 2"
echo -e "[3] Option 3"
read OPTION
case $OPTION in
  [1])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [2])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [3])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  *)
    echo -e "Error: That option does not exist, exiting now."
    exit 1
    ;;
esac


echo -e ""
echo -e "What option do you want to choose?"
unset OPTIONS
OPTIONS+=("Option 1")
OPTIONS+=("Option 2")
OPTIONS+=("Option 3")
select OPTION in "${OPTIONS[@]}"; do
  case ${OPTION} in
    $OPTIONS)
      echo -e "Ok, selected: ${OPTION}"
      break
      ;;
    *)
      echo -e "Error: That option does not exist, exiting now."
      exit 1
      ;;
  esac
done


echo -e ""
echo -e "What option do you want to choose? [1/2/3/4/5]"
read OPTION
case $OPTION in
  [1])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [2])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [3])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [4])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [5])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  *)
    echo -e "Error: That option does not exist, exiting now."
    exit 1
    ;;
esac


echo -e ""
echo -e "What option do you want to choose? (1/2/3/4/5)"
read OPTION
case $OPTION in
  [1])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [2])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [3])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [4])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  [5])
    echo -e "Ok, selected: ${OPTION}"
    ;;
  *)
    echo -e "Error: That option does not exist, exiting now."
    exit 1
    ;;
esac


echo -e ""
read -p "Enter username/text:" TEXT;
echo -e "Ok, username/text: ${TEXT}"


echo -e ""
read -s -p "Enter password:" TEXT;
echo -e "Ok, password: ${TEXT}"


echo -e ""
echo -e "Finished!"


exit 0
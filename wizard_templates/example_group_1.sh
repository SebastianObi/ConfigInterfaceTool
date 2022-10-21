#!/bin/bash


source vendor/colors.sh


echo -e "Hello!"
echo -e ""
echo -e "This is Group #1"
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
echo -e "Finished!"


exit 0
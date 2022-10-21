#!/bin/bash


source vendor/colors.sh


echo -e "Hello!"
echo -e ""
read -p "Hit enter to start."


echo -ne "Checking test 1..."
echo -e " ${GREEN}OK!${NC}"


echo -ne "Checking test 2..."
sleep 5s
echo -e " ${GREEN}OK!${NC}"


echo -ne "Checking test 3..."
sleep 5s
echo -e " ${YELLOW}nok.${NC}"


echo -ne "Checking test 4..."
sleep 5s
echo -e "${RED}failed!${NC}"


echo -e ""
echo -e "Finished!"


exit 0
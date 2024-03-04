#!/bin/bash

UDEVS_DEST_DIR=/etc/udev/rules.d
RULE_NAME=70-streamdeck.rules

sudo rm -f $UDEVS_DEST_DIR/$RULE_NAME

#Do heredoc style so that paths are correct always
cat << EOF > $UDEVS_DEST_DIR/$RULE_NAME
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0060", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0063", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006c", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006d", TAG+="uaccess"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
sudo /etc/init.d/udev restart

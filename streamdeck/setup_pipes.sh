#!/bin/bash

UUID=$(id -u $USER)
PIPEPATH="/var/run/user/$UUID/streampipe"
SCRIPTPATH="/home/$USER/.local/bin"

mkfifo $PIPEPATH

echo '#!/bin/bash' > $SCRIPTPATH/streampipe.sh
echo "while true; do eval \"$(cat $PIPEPATH)\"; done" >> $SCRIPTPATH/streampipe.sh

sudo chmod guo+x $SCRIPTPATH/streampipe.sh

crontab -l > tempcron
echo "@reboot $SCRIPTPATH/streampipe.sh" >> tempcron
crontab tempcron
rm tempcron

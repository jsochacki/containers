#!/bin/bash

#Not safe
#homedir=$(eval echo ~$USER)
#Prevents errors due to sudo run setting USER as root
TMPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd
homedir=$(pwd)
cd $TMPDIR

mkfifo $TMPDIR/streampipe

echo "#!/bin/bash" > streampipe.sh
echo "while true: do eval \"$(cat $TMPDIR/streampipe)\"; done" >> streampipe.sh

sudo chmod guo+x streampipe.sh

crontab -l > tempcron
echo "@reboot $TMPDIR/streampipe.sh" >> tempcron
crontab tempcron
rm tempcron

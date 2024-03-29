#! /bin/bash -e

: '
###################################################################################################################################################
#                                            Script To Hard Restart Components       
###################################################################################################################################################'

read -p "Are you sure? " -n 1 -r
    echo # (Optiononal) new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi
echo Stopping all opsview components...
/opt/opsview/watchdog/bin/opsview-monit stop all
while : ; do
/opt/opsview/watchdog/bin/opsview-monit summary -B | egrep -q 'Running|Initializing' && sleep 10 || break
done;
echo Stopping opsview-agent and opsview-watchdog...
systemctl stop opsview-agent opsview-watchdog
echo Cleaning .pid and .lock files...
find /opt/opsview \( -name *.pid -o -name *.lock \) -delete | sleep 2s
echo Killing opsview user processes...
pkill -u opsview | sleep 2s
echo Checking if there are any remaining processes running under the opsview user
ps -fu opsview | sleep 2s
echo Starting opsview-agent and opsview-watchdog...
systemctl start opsview-agent opsview-watchdog && systemctl status opsview-agent opsview-watchdog | grep -i active
echo Starting opsview components...
/opt/opsview/watchdog/bin/opsview-monit start all
while : ; do
/opt/opsview/watchdog/bin/opsview-monit summary -B | egrep -i 'Not Monitored|Initializing' && sleep 10 || break
done;
if /opt/opsview/watchdog/bin/opsview-monit summary -B | grep -i Running
then
echo All Components Running!
exit 0
fi

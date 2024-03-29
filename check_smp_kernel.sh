#!/bin/sh 
######################
## CHECK SMP KERNEL ##
######################
MODULE=xt_RTPENGINE
SIG_A= 127.0.0.1
SIG_B= 10.140.3.136
NULL= ''
######################
if 
lsmod | grep -qw "$MODULE" && ssh -q $SIG_B << EOF 
lsmod | grep -qw "$MODULE"
EOF
then
echo "CRITICAL - SMP Kernel Loaded On Both SIGs!"
exit 2

elif
lsmod | grep -qw "$MODULE" || ssh -q $SIG_B << EOF 
lsmod | grep -qw "$MODULE" 
EOF
then
echo "OK - SMP Kernel is loaded!"
exit 0

elif
lsmod | grep -qw "$MODULE" ; echo $? -eq 1 > /dev/null & ssh -q $SIG_B << EOF 
lsmod | grep -qw "$MODULE" ; echo $? -eq 1 > /dev/null 
EOF
then
echo "WARNING - SMP Kernel Unloaded on Both SIGs!"
exit 1
fi

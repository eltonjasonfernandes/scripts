#!/bin/sh
######################
## CHECK SMP KERNEL ##
######################

MODULE="xt_RTPENGINE"
SIG_A="127.0.0.1"
SIG_B="10.140.3.136"

######################
check_module() {
    HOST=$1

    if [ "$HOST" = "127.0.0.1" ]; then
        lsmod | grep -qw "$MODULE"
        return $?
    else
        ssh -o ConnectTimeout=5 -q "$HOST" "lsmod | grep -qw $MODULE"
        return $?
    fi
}

######################
check_module "$SIG_A"
A_STATUS=$?

check_module "$SIG_B"
B_STATUS=$?

######################
if [ $A_STATUS -eq 0 ] && [ $B_STATUS -eq 0 ]; then
    echo "CRITICAL - SMP Kernel Loaded On Both SIGs!"
    exit 2

elif [ $A_STATUS -eq 0 ] || [ $B_STATUS -eq 0 ]; then
    echo "OK - SMP Kernel is loaded on at least one SIG!"
    exit 0

elif [ $A_STATUS -ne 0 ] && [ $B_STATUS -ne 0 ]; then
    echo "WARNING - SMP Kernel Unloaded on Both SIGs!"
    exit 1

else
    echo "UNKNOWN - Unable to determine state"
    exit 3
fi


#!/bin/bash

STUDENT_ID='12345678'
PASSWORD='123456'
NETWORK_LINE='CUC-BRAS'
LOG_FILE='/var/log/portal-login/portal-login.log'
INTERNET_PROBE_URL='baidu.com'
LAN_PROBE_URL='10.3.8.211'
AUTH_IN_URL="http://10.3.8.216/login"
AUTH_IN_OUTPUT='/var/log/portal-login/auth_in_output.html'
AUTH_OUT_URL="http://10.3.8.211"
AUTH_OUT_OUTPUT='/var/log/portal-login/auth_out_output.html'
AUTH_100M_URL="http://10.3.8.217/login"
AUTH_100M_OUTPUT='/var/log/portal-login/auth_100m_output.html'

printLog(){
    echo "$(date +"%Y%m%d%H%M%S"): $1"
    echo "$(date +"%Y%m%d%H%M%S"): $1" >> $LOG_FILE
}

ping_domain(){
    ping -q -w 1 -c 1 $1 > /dev/null && return 0 || return 1
}

print_ipv4(){
    ip addr show wlan0 | awk '$1 == "inet" && $6 == "global" { gsub(/\/.*$/, "", $2); print $2; exit }' | grep '10.*.*.*'
}

auth_in(){
    printLog "Getting LAN access."
    curl -s -d "user=$STUDENT_ID&pass=$PASSWORD" "$AUTH_IN_URL" -o "$AUTH_IN_OUTPUT" 2>&1
}

auth_out(){
    printLog "Getting Internet access."
    curl -s -d "DDDDD=$STUDENT_ID&upass=$PASSWORD&R1=0" "$AUTH_OUT_URL" -o "$AUTH_OUT_OUTPUT" 2>&1
}

auth_100M(){
    printLog "Getting 100M access."
    curl -s -d "user=$STUDENT_ID&pass=$PASSWORD&line=$NETWORK_LINE" "$AUTH_100M_URL" -o "$AUTH_100M_OUTPUT" 2>&1
}

printLog "Getting IP."
ip_lan_v4=$(print_ipv4)
if [ -z $ip_lan_v4 ]; then
    printLog "Not in LAN: $ip_lan_v4."
else
    printLog "Login to BUPT-Portal."
    if ping_domain "$INTERNET_PROBE_URL"; then
        printLog "Already have Internet access."
    else
        if ping_domain "$LAN_PROBE_URL"; then
            printLog "Already have LAN access."
        else
            auth_in
        fi
        auth_out
    fi
    auth_100M
    printLog "Login finished."
fi

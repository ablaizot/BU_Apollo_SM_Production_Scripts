#!/usr/bin/env bash

stty -F /dev/ttyACM1 115200 raw -echo   #CONFIGURE SERIAL PORT
exec 3</dev/ttyACM1                     #REDIRECT SERIAL OUTPUT TO FD 3
  cat <&3 > /tmp/ttyDump.dat &          #REDIRECT SERIAL OUTPUT TO FILE
  PID=$!                                #SAVE PID TO KILL CAT
    echo "eepromrd" > /dev/ttyACM1           #SEND COMMAND STRING TO SERIAL PORT
    sleep 0.2s                          #WAIT FOR RESPONSE
  kill $PID                             #KILL CAT PROCESS
  wait $PID 2>/dev/null                 #SUPRESS "Terminated" output

exec 3<&-                               #FREE FD 3
cat /tmp/ttyDump.dat                    #DUMP CAPTURED DATA

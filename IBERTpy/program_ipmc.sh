stty -F /dev/ttyUSB0 115200 raw -echo   #CONFIGURE SERIAL PORT
exec 3</dev/ttyUSB0                     #REDIRECT SERIAL OUTPUT TO FD 3
  cat <&3 > /tmp/ttyDump.dat &          #REDIRECT SERIAL OUTPUT TO FILE
  PID=$!                                #SAVE PID TO KILL CAT
    echo "R" > /dev/ttyUSB0             #SEND COMMAND STRING TO SERIAL PORT
    sleep 0.2s                          #WAIT FOR RESPONSE
  kill $PID                             #KILL CAT PROCESS
  wait $PID 2>/dev/null                 #SUPRESS "Terminated" output

exec 3<&-                               #FREE FD 3
cat /tmp/ttyDump.dat                    #DUMP CAPTURED DATA

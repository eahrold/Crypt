#!/bin/bash
#
# Automatically starts Crypt on unencrypted disks during login.
#


readonly BINARY="/usr/local/crypt/Crypt.app/Contents/MacOS/Crypt"
readonly DISKUTIL="/usr/sbin/diskutil"


log() {
  echo "${@}" >&2
  logger -t request_encryption "${@}"
}



check_encryption_state() {
  ${DISKUTIL} cs list | grep -q -e 'Conversion\ Status.*Pending'
  if [[ ${?} -eq 0 ]]; then
    log "Disk encryption pending, skipping."
    exit 0
  fi

  ${DISKUTIL} cs list | grep -q -e 'Conversion\ Status.*Complete'
  if [[ ${?} -eq 0 ]]; then
    log "Disk encryption complete, skipping."
    exit 0
  fi

  ${DISKUTIL} cs list | grep -q -e 'Conversion\ Status.*Converting'
  if [[ ${?} -eq 0 ]]; then
    log "Disk encrypting or decrypting, skipping."
    exit 0
  fi
}


# Replace YOUR_LOCAL_ADMIN_ACCOUNT here if you want to allow such accounts to bypass this check.
main() {
  check_encryption_state

  if [[ $1 == "root" || $1 == "YOUR_LOCAL_ADMIN_ACCOUNT" ]]; then
    log "Exiting Crypt hook for $1 logging in."
    exit 0
  fi

  # Uncomment the following three lines for use with iHook
  #echo "%WINDOWLEVEL NORMAL"
  #echo "%BEGINPOLE"
  #echo "%RESIGNKEY"

  if [ -f ${BINARY} ]; then
    cd /tmp
    ${BINARY}
    BINARY_EXIT=${?}
    log "Crypt exited with ${BINARY_EXIT}"
  else
    log "Crypt doesn't exist! Please contact helpdesk!"
    echo "Crypt doesn't exist! Please visit helpdesk!"
    sleep 10
    exit 1
  fi

  #if [[ ${BINARY_EXIT} == 0 ]]; then
  #  echo "Crypt needs to reboot to begin encryption." >&2
  #  echo "Rebooting..." >&2

#    for i in 0 20 40 60 80 100; do
#      echo "%${i}"
#      sleep 1
#    done

#    /sbin/shutdown -r now
#  fi

  # Here, we've either already bailed out, or failed, soooo...
  echo "Crypt couldn't encrypt your disk."
  echo "Please contact helpdesk immediately!"
  sleep 1000
}


main "${@}"
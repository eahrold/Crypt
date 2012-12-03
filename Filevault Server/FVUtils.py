#-*- coding: utf-8 -*-
#
#  FVUtils.py
#  Filevault Server
#
#  Created by Graham Gilbert on 03/12/2012.
#  Copyright (c) 2012 Graham Gilbert. All rights reserved.
#

#import os
#import sys
import re
import subprocess

def GetMacSerial():
    """Returns the serial number for the Mac
        """
    the_command = "ioreg -c \"IOPlatformExpertDevice\" | awk -F '\"' '/IOPlatformSerialNumber/ {print $4}'"
    serial = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
    serial = re.sub(r'\s', '', serial)
    return serial

def GetRootDisk():
    """Returns the device name of the root disk.
        
        Returns:
        str, like "/dev/disk...."
        Raises:
        Error: When the root disk could not be found.
        """
    try:
        the_command = '/sbin/mount'
        stdout = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
    except:
        NSLog("Crap, something went wrong")
    
    for line in stdout.splitlines():
        try:
            device, _, mount_point, _ = line.split(' ', 3)
            if mount_point == '/' and re.search(r'^[/a-z0-9]+$', device, re.I):
                return device
        except ValueError:
            pass
#-*- coding: utf-8 -*-
#
#  FVUtils.py
#  Filevault Server
#
#  Created by Graham Gilbert on 03/12/2012.
#
# Copyright 2012 Graham Gilbert.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import subprocess
from Foundation import CFPreferencesCopyAppValue, NSDate

# our preferences "bundle_id"
BUNDLE_ID = 'FVServer'

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

##This was lifted verbatim from the Munki project - hope Greg doesn't mind!

def set_pref(pref_name, pref_value):
    """Sets a preference, writing it to
        /Library/Preferences/ManagedInstalls.plist.
        This should normally be used only for 'bookkeeping' values;
        values that control the behavior of munki may be overridden
        elsewhere (by MCX, for example)"""
    try:
        CFPreferencesSetValue(
                              pref_name, pref_value, BUNDLE_ID,
                              kCFPreferencesAnyUser, kCFPreferencesCurrentHost)
        CFPreferencesAppSynchronize(BUNDLE_ID)
    except Exception:
        pass

def pref(pref_name):
    """Return a preference. Since this uses CFPreferencesCopyAppValue,
    Preferences can be defined several places. Precedence is:
        - MCX
        - /var/root/Library/Preferences/ManagedInstalls.plist
        - /Library/Preferences/ManagedInstalls.plist
        - default_prefs defined here.
    """
    default_prefs = {
        'ServerURL': 'http://fvserver',
    }
    pref_value = CFPreferencesCopyAppValue(pref_name, BUNDLE_ID)
    if pref_value == None:
        pref_value = default_prefs.get(pref_name)
        # we're using a default value. We'll write it out to
        # /Library/Preferences/<BUNDLE_ID>.plist for admin
        # discoverability
        set_pref(pref_name, pref_value)
    if isinstance(pref_value, NSDate):
        # convert NSDate/CFDates to strings
        pref_value = str(pref_value)
    return pref_value
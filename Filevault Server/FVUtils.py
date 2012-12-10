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
import os
import plistlib
import subprocess
from Foundation import *
import urllib2

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
        NSLog(u"Crap, something went wrong")
    
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
        'ServerURL': 'http://crypt',
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

def encryptDrive(password,username):
    #time to turn on filevault
    # we need to see if fdesetup is available, might as well use the built in methods in 10.8
    if os.path.exists('/usr/bin/fdesetup'):
        ##build plist
        the_settings = {}
        the_error = ""
        fv_status = ""
        the_settings['Username'] = username
        the_settings['Password'] = password
        input_plist = plistlib.writePlistToString(the_settings)
        try:
            p = subprocess.Popen(['/usr/bin/fdesetup','enable','-outputplist', '-inputplist'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_data = p.communicate(input=input_plist)[0]
            NSLog(u"%s" % stdout_data)
            fv_status = plistlib.readPlistFromString(stdout_data)
            return fv_status['RecoveryKey'], the_error
        except:
            return fv_status, "Couldn't enable FileVault"
            
    else:
        try:
            the_command = "/usr/local/bin/csfde "+FVUtils.GetRootDisk()+" "+username+" "+password
            proc = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
            fv_status = plistlib.readPlistFromString(proc)
            return fv_status['recovery_password']
        except:
            return fv_status, "Couldn't enable FilveVault"

def internet_on():
    try:
        response=urllib2.urlopen(pref('ServerURL'),timeout=1)
        NSLog(u"Server is accessible")
        return True
    except urllib2.URLError as err: pass
    NSLog(u"Server is not accessible")
    return False
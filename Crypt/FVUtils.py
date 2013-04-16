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
import FoundationPlist
from Foundation import *
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.parsers import expat
import urllib
import FVAlerts

# our preferences "bundle_id"
BUNDLE_ID = 'FVServer'

# paths to common executables
fdesetupExec='/usr/bin/fdesetup'
diskutilExec = '/usr/sbin/diskutil'
csfdeExec = '/usr/local/bin/csfde'

def GetMacSerial():
    """Returns the serial number for the Mac
        """
    the_command = "ioreg -c \"IOPlatformExpertDevice\" | awk -F '\"' '/IOPlatformSerialNumber/ {print $4}'"
    serial = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
    serial = re.sub(r'\s', '', serial)
    return serial


def GetMacName():
    theprocess = "scutil --get ComputerName"
    thename = subprocess.Popen(theprocess,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
    thename = thename.strip()
    return thename



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
        'CryptDir': '/usr/local/crypt',
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
    the_error = ""
    fv_status = ""
    if os.path.exists(fdesetupExec):
        ##build plist
        the_settings = {}
        the_settings['Username'] = username
        the_settings['Password'] = password
        input_plist = plistlib.writePlistToString(the_settings)
        try:
            p = subprocess.Popen([fdesetupExec,'enable','-outputplist', '-inputplist'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_data = p.communicate(input=input_plist)[0]
            NSLog(u"%s" % stdout_data)
            fv_status = plistlib.readPlistFromString(stdout_data)
            return fv_status['RecoveryKey'], the_error
        except:
            return fv_status, "Couldn't enable FileVault on 10.8"

    if not os.path.exists(fdesetupExec):
        try:
            the_command = "/sbin/mount"
            stdout = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
            for line in stdout.splitlines():
                try:
                    device, _, mount_point, _ = line.split(' ', 3)
                    if mount_point == '/' and re.search(r'^[/a-z0-9]+$', device, re.I):
                        the_disk = device
                        break
                except:
                    NSLog(u"couldn't get boot disk")
            #the_disk = FVUtils.GetRootDisk()
            NSLog(u"%s" % the_disk)
            stdout_data = subprocess.Popen([csfdeExec,the_disk,username,password], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
            fv_status = plistlib.readPlistFromString(stdout_data)
            NSLog(u"%s" % fv_status['recovery_password'])
            return fv_status['recovery_password'], the_error
        except:
            return fv_status, "Couldn't enable FilveVault on 10.7"

def driveIsEncrypted(self):
    NSLog(u"Checking on FileVault Status")
    if os.path.exists(fdesetupExec):
        try:
            fv_status = subprocess.Popen([fdesetupExec,'status'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
            if re.match(r'FileVault is On.|Encryption in progress:*',fv_status):
                FVAlerts.quit_if_encrypted(self)
                return True
            elif re.match(r'Decryption in progress:|FileVault is Off, but needs to be restarted to finish.',fv_status):
                FVAlerts.quit_if_decrypting(self)
                return True
            else:
                NSLog(u"FileVault Not Enabled, launching Crypt")
                return False
        except expat.ExpatError as e:
            return False

    elif os.path.exists(diskutilExec):
        try:
            lv_family = plistlib.readPlistFromString(subprocess.Popen([diskutilExec,'cs','info','-plist','/'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]).get('MemberOfCoreStorageLogicalVolumeFamily')
           
            the_command=diskutilExec+" cs list "+lv_family
            stdout = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
            for line in stdout.splitlines():
                try:
                    FVproperty, FVstatus= line.split(':', 2)
                    if re.search(r'Conversion Status', FVproperty):
                        lvf_status = FVstatus
                    elif re.search(r'Conversion Direction', FVproperty):
                        lvf_direction = FVstatus
                    elif re.search(r'Fully Secure', FVproperty):
                        lvf_secure = FVstatus
                except:
                    NSLog(u"something went wrong!")

   
            if re.search(r'Yes',lvf_secure):
                FVAlerts.quit_if_encrypted(self)
                return True
            elif re.search(r'No',lvf_secure):
                if re.search(r'Converting',lvf_status):
                    NSLog(u"Drive is Currenlty in the process of Converting....")

                    if re.search(r'forward',lvf_direction):
                        FVAlerts.quit_if_encrypted(self)
                        return True
                        
                    elif re.search(r'backward',lvf_direction):
                        FVAlerts.quit_if_decrypting(self)
                        return True
                else:
                    NSLog(u"FileVault Not Enabled, launching Crypt")
                    return False                    
        except expat.ExpatError as e:
            print False



def internet_on():
    try:
        response=urlopen(pref('ServerURL'),timeout=1)
        NSLog(u"Server is accessible")
        return True
    except URLError as err: pass
    NSLog(u"Server is not accessible")
    return False

def root_user():
    if os.geteuid() == 0:
        return True
    else:
        NSLog(u"Crypt Needs to run as root, relaunching...")
        launch_file="/usr/local/crypt/watch/launch"
        open(launch_file, 'w').close()
        os.remove(launch_file)
        return False

def escrowKey(key, username, runtype):
    ##submit this to the server fv_status['recovery_password']
    theurl = pref('ServerURL')+"/checkin/"
    serial = GetMacSerial()
    macname = GetMacName()
    mydata=[('serial',serial),('recovery_password',key),('username',username),('macname',macname)]
    mydata=urllib.urlencode(mydata)
    req = Request(theurl, mydata)
    try:
        response = urlopen(req)
    except URLError, e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
            has_error = True
        #NSApp.terminate_(self)
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request'
            print 'Error code: ', e.code
            has_error = True
            #NSApp.terminate_(self)
            if has_error:
                plistData = {}
                plistData['recovery_key']=key
                plistData['username']=username
                
                FoundationPlist.writePlist(plistData, '/usr/local/crypt/recovery_key.plist')
                os.chmod('/usr/local/crypt/recovery_key.plist',0700)
                if runtype=="initial":
                    os.system('reboot now')
    else:
        ##need some code to read in the json response from the server, and if the deta matches, display success message, or failiure message, then reboot. If not, we need to cache it on disk somewhere - maybe pull it out with facter?
        #time to turn on filevault
        #NSLog(u"%s" % fvprefs['ServerURL'])
        ##escrow successful, if the file exists, remove it
        thePlist = '/usr/local/crypt/recovery_key.plist'

        if os.path.exists(thePlist):
            os.remove(thePlist)
        if runtype=="initial":
            os.system('reboot now')
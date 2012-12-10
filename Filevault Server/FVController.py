#-*- coding: utf-8 -*-
#
#  FVController.py
#  Filevault Server
#
#  Created by Graham Gilbert on 03/12/2012.
#
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

import objc
import FoundationPlist
import os
from Foundation import *
import subprocess
import sys
import re
import FVUtils
import urllib
import plistlib
import re
from urllib2 import Request, urlopen, URLError, HTTPError


class FVController(NSObject):
    userName = objc.IBOutlet()
    password = objc.IBOutlet()
    encryptButton = objc.IBOutlet()
    errorField = objc.IBOutlet()
    window = objc.IBOutlet()
    
    def encryptDrive(self,password,username):
        #time to turn on filevault
        # we need to see if fdesetup is available, might as well use the built in methods in 10.8
        the_command = "/usr/local/bin/csfde "+FVUtils.GetRootDisk()+" "+username+" "+password
        proc = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
        fv_status = plistlib.readPlistFromString(proc)
        return fv_status['recovery_password']
    
    def startRun(self):
        if self.window:
            self.window.setCanBecomeVisibleWithoutLogin_(True)
            self.window.setLevel_(NSScreenSaverWindowLevel - 1)
            self.window.center()
    
    @objc.IBAction
    def encrypt_(self,sender):
        fvprefspath = "/Library/Preferences/FVServer.plist"
        the_command = "ioreg -c \"IOPlatformExpertDevice\" | awk -F '\"' '/IOPlatformSerialNumber/ {print $4}'"
        serial = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
        serial = re.sub(r'\s', '', serial)
        serverURL = FVUtils.pref("ServerURL")
        NSLog(u"%s" % serverURL)
        if serverURL == "":
            self.errorField.setStringValue_("ServerURL isn't configured")
            self.userName.setEnabled_(False)
            self.password.setEnabled_(False)
            self.encryptButton.setEnabled_(False)
        username_value = self.userName.stringValue()
        password_value = self.password.stringValue()
        self.userName.setEnabled_(False)
        self.password.setEnabled_(False)
        self.encryptButton.setEnabled_(False)
    
        if username_value == "" or password_value == "":
            self.errorField.setStringValue_("You need to enter your username and password")
            self.userName.setEnabled_(True)
            self.password.setEnabled_(True)
            self.encryptButton.setEnabled_(True)

        if username_value != "" and password_value !="":
            self.userName.setEnabled_(False)
            self.password.setEnabled_(False)
            self.encryptButton.setEnabled_(False)
            
            #NSLog(u"csfde results: %s" % fv_status)
            recovery_key = encryptDrive(password_value, username_value)
            if fv_status['error'] == False:
                ##submit this to the server fv_status['recovery_password']
                theurl = serverURL+"/checkin/"
                mydata=[('serial',serial),('recovery_password',recovery_key)]
                mydata=urllib.urlencode(mydata)
                req = Request(theurl, mydata)
                try:
                    response = urlopen(req)
                except URLError, e:
                    if hasattr(e, 'reason'):
                        print 'We failed to reach a server.'
                        print 'Reason: ', e.reason
                        NSApp.terminate_(self)
                    elif hasattr(e, 'code'):
                        print 'The server couldn\'t fulfill the request'
                        print 'Error code: ', e.code
                        NSApp.terminate_(self)
    
                else:
                    ##need some code to read in the json response from the server, and if the deta matches, display success message, or failiure message, then reboot. If not, we need to cache it on disk somewhere - maybe pull it out with facter?
                    #time to turn on filevault
                    #NSLog(u"%s" % fvprefs['ServerURL'])
                    the_command = "/sbin/reboot"
                    reboot = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
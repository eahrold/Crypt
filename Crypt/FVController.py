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
from AppKit import *
from Cocoa import *
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
        
        def enable_inputs(self):
            self.userName.setEnabled_(True)
            self.password.setEnabled_(True)
            self.encryptButton.setEnabled_(True)
    
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
            recovery_key, encrypt_error = FVUtils.encryptDrive(password_value, username_value)
            if encrypt_error:
                NSLog(u"%s" % encrypt_error)
                ##write the key to a plist
                ##load a launch daemon - touch a file maybe?
                ##submit the key
                alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                                                                                                                          NSLocalizedString(u"Something went wrong", None),
                                                                                                                          NSLocalizedString(u"Aww, drat", None),
                                                                                                                          objc.nil,
                                                                                                                          objc.nil,
                                                                                                                          NSLocalizedString(u"There was a problem with enabling encryption on your Mac. Please take sure your are using your short username and that your password is correct. Please contact IT Support if you need help.", None))
                alert.beginSheetModalForWindow_modalDelegate_didEndSelector_contextInfo_(
                                                                                             self.window, self, enable_inputs(self), objc.nil)
            if recovery_key:
                FVUtils.escrowKey(recovery_key, username_value, 'initial')
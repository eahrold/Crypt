#-*- coding: utf-8 -*-
#
#  FVController.py
#  Filevault Server
#
#  Created by Graham Gilbert on 03/12/2012.
#  Copyright (c) 2012 Graham Gilbert. All rights reserved.
#

import objc
import FoundationPlist
import os
from Foundation import *
import subprocess
import sys
import re
import FVUtils
import urllbib
from urllib2 import Request, urlopen, URLError, HTTPError


class FVController(NSObject):
    #if filevaultenabled:
    #    sys.exit("\nFileVault is already enabled\n")
    #get the server url from the plist - if its not present, disable everything in the ui and display an error
    userName = objc.IBOutlet()
    password = objc.IBOutlet()
    encryptButton = objc.IBOutlet()
    errorField = objc.IBOutlet()

    @objc.IBAction
    def encrypt_(self,sender):
        fvprefspath = "/Library/Preferences/FVServer.plist"
        
        if not os.path.exists(fvprefspath):
            self.errorField.setStringValue_("Preferences Missing")
            self.userName.setEnabled_(False)
            self.password.setEnabled_(False)
            self.encryptButton.setEnabled_(False)
        fvprefs = FoundationPlist.readPlist(fvprefspath)
        if fvprefs['ServerURL'] == "":
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
            #time to turn on filevault
            the_command = "/usr/local/bin/csfde "+FVUtils.GetRootDisk()+" "+username_value+" "+password_value
            fv_status = subprocess.Popen(the_command,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
            if fv_status['error'] == False:
                ##submit this to the server fv_status['recovery_password']
                theurl = fvprefs['ServerURL']
                mydata=[('serial',serial),('recovery_password',fv_status['recovery_password'])]
                mydata=urllib.urlencode(mydata)
                req = Request(theurl, mydata)
                try:
                    response = urlopen(req)
                except URLError, e:
                    if hasattr(e, 'reason'):
                        print 'We failed to reach a server.'
                        print 'Reason: ', e.reason
                        sys.exit(e.reason)
                    elif hasattr(e, 'code'):
                        print 'The server couldn\'t fulfill the request'
                        print 'Error code: ', e.code
                        sys.exit(e.code)
						##need some code to read in the json response from the server, and if the deta matches, display success message, or failiure message, then reboot

                                
        NSLog(u"username: %s" % username_value)
        NSLog(u"Password: %s" % password_value)
        NSLog(u"Root Disk: %s" % FVUtils.GetRootDisk())
        NSLog(u"FV Prefs: %s" % fvprefs)
        NSLog(u"FV Status: %s" % fv_status)
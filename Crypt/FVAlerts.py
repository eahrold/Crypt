#-*- coding: utf-8 -*-
#
#  FVAlerts.py
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


from AppKit import *
from Foundation import *

def quit_if_encrypted(self):
    NSLog(u"Drive is Already Encrypted, quitting.")
    alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                                                                                                              NSLocalizedString(u"Your Drive is Already Encrypted", None),
                                                                                                              NSLocalizedString(u"OK", True),
                                                                                                              objc.nil,
                                                                                                              objc.nil,
                                                                                                              NSLocalizedString(u"You already have FileVault enabled on this drive, if you have the Recovery Key saved, you may email it to IT support and they can store it for you.", None))
    alert.runModal()
    NSApp.terminate_(self)

def quit_if_decrypting(self):
    NSLog(u"Drive is Currently Decrypting, try again once complete.  Quitting.")
    alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                                                                                                              NSLocalizedString(u"Your Drive is Currently Decrypting", None),
                                                                                                              NSLocalizedString(u"OK", True),
                                                                                                              objc.nil,
                                                                                                              objc.nil,
                                                                                                              NSLocalizedString(u"Please try again once the decryption process has completed and your computer has restarted.", None))
    alert.runModal()
    NSApp.terminate_(self)

def crypt_error(self,encrypt_error):
    NSLog(u"%s" % encrypt_error)
    alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                                                                                                              NSLocalizedString(u"Something went wrong", None),
                                                                                                              NSLocalizedString(u"Aww, drat", None),
                                                                                                              objc.nil,
                                                                                                              objc.nil,
                                                                                                              NSLocalizedString(u"There was a problem with enabling encryption on your Mac. Please take sure your are using your short username and that your password is correct. Please contact IT Support if you need help.", None))
    alert.beginSheetModalForWindow_modalDelegate_didEndSelector_contextInfo_(self.window, self, enable_inputs(self), objc.nil)


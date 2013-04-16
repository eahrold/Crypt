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



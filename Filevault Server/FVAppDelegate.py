#-*- coding: utf-8 -*-
#
#  Filevault_ServerAppDelegate.py
#  Filevault Server
#
#  Created by Graham Gilbert on 04/11/2012.
#  Copyright Graham Gilbert 2012. All rights reserved.
#

from Foundation import *
from AppKit import *

class FVAppDelegate(NSObject):
    def applicationWillFinishLaunching_(self, sender):
        # don't show menu bar
        NSMenu.setMenuBarVisible_(NO)
                
        def applicationDidFinishLaunching_(self, sender):
            NSLog(u"FV Server finished launching.")

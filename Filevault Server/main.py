#-*- coding: utf-8 -*-
#
#  main.py
#  Filevault Server
#
#  Created by Graham Gilbert on 04/11/2012.
#  Copyright Graham Gilbert 2012. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import FVAppDelegate
import FVController

# pass control to AppKit
AppHelper.runEventLoop()

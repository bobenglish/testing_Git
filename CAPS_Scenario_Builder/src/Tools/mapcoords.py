## -*- coding:utf-8 -*-
#--------------------------------------------------------------------- 
#
#Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#---------------------------------------------------------------------- 
# Copyright (C) 2007  Ecotrust
# Copyright (C) 2007  Aaron Racicot
# Copyright (C) 2011  Robert English: Daystar Computing (http://edaystar.com)
#---------------------------------------------------------------------
# 
# licensed under the terms of GNU GPLv3
# 
# This file is part of CAPS.

#CAPS is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#CAPS is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with CAPS.  If not, see <http://www.gnu.org/licenses/>..
# 
#---------------------------------------------------------------------
# General system includes
import sys, string
# PyQt4 includes for python bindings to QT
from PyQt4 import QtCore
from PyQt4 import QtGui
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *
  
# Coordinates display in statusbar
class MapCoords(object):
    def __init__(self, parent):
        self.parent = parent
    
        # This captures the mouse move for coordinate display
        QtCore.QObject.connect(parent.canvas, QtCore.SIGNAL("xyCoordinates(const QgsPoint &)"),
                        self.updateCoordsDisplay)
        self.latlon = QtGui.QLabel("0.0 , 0.0")
        self.latlon.setFixedWidth(200)
        self.latlon.setAlignment(QtCore.Qt.AlignHCenter)
        self.parent.statusBar.addPermanentWidget(self.latlon)

    # Signal handler for updating coord display
    def updateCoordsDisplay(self, p):
        # debugging
        #if str(p.x()) == "-1.#IND":
            #self.latlon.setText("0.0 , 0.0")   
        #else:
        
        capture_string = QtCore.QString("%.3f" % float(p.x()) + " , " +
                                 "%.3f" % float(p.y()))
        self.latlon.setText(capture_string)

  

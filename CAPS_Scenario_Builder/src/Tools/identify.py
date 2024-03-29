# -*- coding:utf-8 -*-
#---------------------------------------------------------------------
#
# Conservation Assessment and Prioritization System (CAPS) - An Open Source  
# GIS tool to create scenarios for environmental modeling.
#
#--------------------------------------------------------------------- 
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

# PyQt4 includes for python bindings to QT
from PyQt4 import QtCore, QtGui 
# QGIS bindings for mapping functions
from qgis.core import *
from qgis.gui import *
# CAPS application imports
import shared

class Identify(QgsMapTool):
    ''' Provide a tool to get information about vector features and raster values '''
    def __init__(self, parent):
        QgsMapTool.__init__(self, parent.canvas)
    
        # Make handle to mainwindow and call all variables needed for methods from mainwindow.
        # This allows variables to be updated when the active layer changes so that 
        # re-instantiating the class every time a layer changes is not necessary.
        self.mainwindow = parent
        self.display = None
        
#######################################################################
    ''' Overridden QgsMapTool Events '''
#######################################################################

    def canvasPressEvent(self, event):
        ''' Get point and transform to map coordinates '''
        point = event.pos()
        self.transform = self.mainwindow.canvas.getCoordinateTransform()
        # returns a QgsPoint object in map coordinates
        qgsPoint = self.transform.toMapCoordinates(point.x(), point.y())
        if self.mainwindow.activeVLayer:
            self.vectorIdentifyTool(point, qgsPoint)
        elif self.mainwindow.activeRLayer:
            self.rasterIdentifyTool(qgsPoint)
        
    def canvasReleaseEvent(self, event):
        pass
     
######################################################################
    ''' Core Methods '''
######################################################################
 
    def rasterIdentifyTool(self, qgsPoint):
        ''' Get text for the clicked point and raster value at that point '''
        # debugging
        print "identify.rasterIdentifyTool()"
        
        text = "The clicked x,y point is (" + str(qgsPoint.x()) + ", " + str(qgsPoint.y()) + ")\n"
        # this QgsVectorLayer method returns a tuple consisting of the bool result (success = True) 
        # and a dictionary with the key being the band names of the raster and the values
        # being the values at the clicked point.
        result, identifyDict = self.mainwindow.activeRLayer.identify(qgsPoint)
        for (k,v) in identifyDict.iteritems():
            text += str(k) + " value: " + str(v) + "\n"
        if not result: # if the identify method fails
            print "Identify raster layer failed"
        
        # now display the text to the user
        title = "Identify Raster"
        self.displayInformation(title, text)        
             
    def vectorIdentifyTool(self, point, qgsPoint):
        ''' Get text for the coordinates and attributes of vector features '''
        # debugging
        print "identify.vectorIdentifyTool()"
        
        provider = self.mainwindow.provider
        # fields() returns a dictionary with the field key and the name of the field
        fieldNamesDict = provider.fields()
        allAttrs = provider.attributeIndexes()
        selectRect = shared.makeSelectRect(self.mainwindow.geom, point, self.transform)
        provider.select(allAttrs, selectRect, True, False)
        feat = QgsFeature()
        while provider.nextFeature(feat):
            # fetch the feature geometry, which is the feature's spatial coordinates
            fgeom = feat.geometry()
            # This records the feature's ID and its spatial coordinates
            text = "Feature ID %d: %s\n" % (feat.id()+1, fgeom.exportToWkt()) 
            #A QgsAttribute map is a Python dictionary (key = field id : value = 
            # the field's value as a QtCore.QVariant()object 
            attrs = feat.attributeMap() 
            # This takes the field key (starting with 0 for the first field) uses it
            # to return the field name from the fieldNamesDictionary.  The loop then
            # records the field name and field value for the selected feature
            # note: t
            for (key, attr) in attrs.iteritems():
                text += "%s: %s\n" % (fieldNamesDict.get(key).name(), attr.toString())
                
            # display the text to the user
            title = "Vector Feature Information"
            self.displayInformation(title, text)
                            
    def displayInformation(self, title, text):
        ''' Display the information about the vector or raster '''
        # debugging
        print "identify.displayInformation()"
        
        title = QtCore.QString(title)
        text = QtCore.QString(text)
        # See mainwindow.openRasterCategoryTable() for a description of the following code: 
        if not self.display:       
            self.display = QtGui.QDockWidget(title, self.mainwindow)
            self.display.setFloating(True)
            self.display.setMinimumSize(QtCore.QSize(450, 300))
            self.textBrowser = QtGui.QTextBrowser()
            self.textBrowser.setWordWrapMode(QtGui.QTextOption.NoWrap)
            self.textBrowser.setText(text)
            self.textBrowser.setFontPointSize(9.0)
            self.display.setWidget(self.textBrowser)
            self.display.show()
        else:
            self.textBrowser.setText(text)
            self.display.setVisible(True)

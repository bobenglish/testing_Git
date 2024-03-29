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
from dlgaddattributes import DlgAddAttributes
import shared


class AddLinesPolygons(QgsMapTool):
    ''' Provide a tool to add new lines or polygons, and their attributes, to an editing shapefile '''
    def __init__(self, parent):
        QgsMapTool.__init__(self, parent.canvas)
        
        # debigging
        print "Class AddLinesPolygons()"
        
        ''' This class is initiated whenever the add line or add polygon action is
            selected.  The add line and add polygon actions are set to unselected
            whenever the active layer is changed, so the instance variables below
            always get updated whenever the active layer changes.
        '''
        
        self.mainwindow = parent
        self.canvas = parent.canvas
        self.down = False
        self.started = False
        self.rubberBand = None
            
#######################################################################
    ''' Overridden QgsMapTool Events '''
#######################################################################
   
    def canvasPressEvent(self, event):
        ''' Record the mouse down event '''
        # set the active vector layer
        self.activeVLayer = self.mainwindow.activeVLayer
        if self.activeVLayer == None:
            return
        
        # set the current geometry and some variables for the QgsRubberBand
        if self.mainwindow.geom:
            if self.mainwindow.geom == 1: # line
                self.geom = False
            else: self.geom = True # polygon
        
        # check if the editing layer is selected but only on the first click
        if self.started == False:
            currentLayerName = self.mainwindow.legend.currentItem().canvasLayer.layer().name()
            if shared.checkSelectedLayer(self.mainwindow, self.mainwindow.scenarioType, 
                                                               currentLayerName) == "Cancel":    
                return # return without starting to draw
        self.down = True # starts the drawing process

    def canvasReleaseEvent(self, event):
        if self.down == True:
            if (self.started == False) and (event.button()== QtCore.Qt.RightButton):
                # We have a right button but have not started a poly... just return
                return
            # mouse is down, before release initialize rubber band
            if self.started==False:
                # Initialize Rubber Band
                self.rubberBand = QgsRubberBand(self.canvas, self.geom)
                self.rubberBand.setWidth(.6)
                self.rubberBand.show()
                self.numberOfPoints = 0

            # getCoordinateTransform returns a QgsMapToPixel object
            # which transforms between device coordinates and map coordinates 
            transform = self.canvas.getCoordinateTransform()
            # toMapCoordinates is a QgsMapToPixel method that 
            # takes a QPoint (from device) as a parameter and returns a 
            # QgsPoint object transformed to map coordinates
            qgsPoint = transform.toMapCoordinates(event.pos().x(),
                                            event.pos().y())
            self.rubberBand.addPoint(qgsPoint)
            self.started=True
            self.numberOfPoints = self.numberOfPoints + 1
            if self.geom:
                if (event.button() == QtCore.Qt.RightButton) and (self.numberOfPoints > 2):
                    #self.down=False
                    #self.started=False
                    self.getNewAttributes()
            else: 
                if (event.button() == QtCore.Qt.RightButton) and (self.numberOfPoints > 1):
                    #self.down=False
                    #self.started=False
                    self.getNewAttributes()
               
    def canvasMoveEvent(self,event):
        if self.started == True:    
            transform = self.canvas.getCoordinateTransform()
            qgsPoint = transform.toMapCoordinates(event.pos().x(), event.pos().y())
            self.rubberBand.movePoint(qgsPoint)

#######################################################################
    ''' Core Methods '''
#######################################################################
 
    def getNewAttributes(self):
        ''' Dialog to get attribute information for the current scenario edit type '''
        # debugging
        print "Class AddLinesPolygons() getNewAttributes()"
        
        self.dlg = DlgAddAttributes(self.mainwindow)

        if self.dlg.exec_(): # The user has clicked "OK"
            # validation
            attributes = self.dlg.getNewAttributes()
            self.addLinePolygon(attributes) 
        else: # User has clicked "Cancel"
            
            # debugging
            print "Canceled"
            # just set the point to nothing
            self.qgsPoint = None
            self.rubberBand.reset(self.geom)
            return  
       
    def addLinePolygon(self, attributes):
        ''' Add the new line or polygon and display '''
        # debugging
        print "AddLinesPolygons.addLinePolygon() starting"
        # Set the data provider
        self.provider = self.mainwindow.provider
        # make a list of the original points in the active layer
        self.originalFeats = shared.listOriginalFeatures(self.provider)
        # need to update the mainwindow instance variable for call to Tools.shared.deleteEdits
        self.mainwindow.originalFeats = self.originalFeats
        
        feat = QgsFeature()
        vlayerName = self.mainwindow.activeVLayer.name()
        # add the line or polygon geometry to the feature
        feat.setGeometry(self.rubberBand.asGeometry())
        feat.setAttributeMap(attributes)
        # this actually writes the added point to disk!
        # the space between parentheses, brackets and the parameter are needed!
        try:
            self.provider.addFeatures( [ feat ] )
        except (IOError, OSError), e:
            error = unicode(e)
            print error                    
            QtGui.QMessageBox.warning(self, "Failed to add feature(s)", "Please check if "
                                 + vlayerName + " is open in another program and then try again.")
   
        
        # reset the editing layer id numbers
        shared.resetIdNumbers(self.provider, self.mainwindow.geom)
        
        # update the attribute table if open
        if self.mainwindow.attrTable and self.mainwindow.attrTable.isVisible():
            self.mainwindow.openVectorAttributeTable()
        
        # reset the QgsRubberBand so color of feature returns to default
        self.resetDraw()

        #set the edit flag to unsaved
        self.mainwindow.editDirty = self.activeVLayer.name()
        # enable the save edits button
        self.mainwindow.mpActionSaveEdits.setDisabled(False)
        
        # debugging
        print "the edit flag was set to " + self.activeVLayer.name() + " by addLinePolygon()."
        print "the number of features added is " + str(shared.numberFeaturesAdded
                                                       (self.activeVLayer, self.originalFeats))
        
        # update layer extents
        shared.updateExtents(self.mainwindow, self.mainwindow.provider, self.mainwindow.activeVLayer, 
                                                                    self.mainwindow.canvas)
 
    def resetDraw(self):
        ''' Resets drawing if user cancels "Add Attributes" dialog '''
        # debugging 
        print "AddLinesPolygons.resetDraw"
        
        self.down = False
        self.started = False
        self.rubberBand.reset(self.geom)


#**************************************************************
    ''' Testing '''
#**************************************************************

    def printFeatures(self):       
        "startingPrintFeatures"
        #self.provider.reloadData()
        feat = QgsFeature()
        allAttrs = self.provider.attributeIndexes()
        self.provider.select(allAttrs)
        # the nextFeature() method operates on a select initialized provider
        while self.provider.nextFeature(feat):
            # fetch the feature geometry, which is the feature's spatial coordinates
            fgeom = feat.geometry()
            # This prints the feature's ID and its spatial coordinates
            print "Feature ID %d: %s\n" % (feat.id(), fgeom.exportToWkt()) 
            print type(feat.id())
            # a QgsAttributeMap is a pointer to a series of QtCore.QVariant objects
            attrs = feat.attributeMap() 
             
            # the map first prints the Qgs feature ID and 
            # then it prints the field key (starting with 0 for the first field) and the field's value.
            # note: the QgsAttribute map is a Python dictionary (key = field id : field value)
            for (key, attr) in attrs.iteritems():
                print "%d: %s" % (key, attr.toString())       
      
#BBD's Krita Script Starter Feb 2018

import sys, os, datetime, pathlib
from PyQt5.QtWidgets import *
from krita import *
from PyQt5.QtCore import QStandardPaths, QSettings
import PyQt5.uic as uic

EXTENSION_ID = 'pykrita_unity_animation_exporter'
MENU_ENTRY = 'Unity Animation Exporter'
UI_FILE = "unity_animation_exporter_ui.ui"

##########
#
# Gets and Loads the UI file
#
##########

def load_ui(ui_file):
	abs_path = os.path.dirname(os.path.realpath(__file__))
	ui_file = os.path.join(abs_path, UI_FILE)
	return uic.loadUi(ui_file)

class Unity_animation_exporter(Extension):

	LogString = ""
	XMLString = ""
	NeedToExit = False

	#########
	#
	# Adds a Time Stamp to stringToAdd
	# and Adds Created String to Log String
	#
	#########
	def AddToLog(self, stringToAdd):
		timeStamp = "[%s]: " % (datetime.datetime.now().strftime("%H:%M:%S"))
		string = timeStamp + stringToAdd + "\n"
		self.LogString += string
		self.ui.browser_LogWindow.setPlainText(self.LogString)
		
	##########
	#
	# Sets the filepath variable
	# based on UI setting
	#
	##########

	def SetFilePath(self):
		self.filepath = self.ui.lineEdit_FilePath.text()
		if self.filepath[len(self.filepath) - 1] != "/" or self.filepath[len(self.filepath - 1)] != "\\":
			self.filepath += "/"

		self.AddToLog("Filepath is: " + self.filepath)

	##########
	#
	# Sets File Extensions Based on
	# UI settings
	#
	##########

	def SetExtensions(self):
		self.fileExtension = self.ui.lineEdit_ExportExtension.text()
		if self.fileExtension[0] != ".":
			self.fileExtension = "." + self.ui.lineEdit_ExportExtension.text()
		self.AddToLog("Export Image Extension is: " + self.fileExtension)

		self.xmlExtension = self.ui.lineEdit_XMLExtension.text()
		if self.xmlExtension[0] != ".":
			self.xmlExtension = "." + self.ui.lineEdit_XMLExtension.text()
		self.AddToLog("XML Extension is: " + self.xmlExtension)

		self.logExtension = self.ui.lineEdit_LogExtension.text()
		if self.logExtension[0] != ".":
			self.logExtension = "." + self.ui.lineEdit_LogExtension.text()
		self.AddToLog("Log Extension is: " + self.logExtension)
		
	##########
	#
	# Sets the File Prefix for Files Exported
	#
	##########
	def SetPrefix(self):
		self.FilePrefix = self.ui.lineEdit_FilePrefix.text()
		self.AddToLog("File Prefix is: " + self.FilePrefix)

	#########
	#
	# Adds Layer Information to XML String
	#
	#########
	def AddToXML(self, layerName, FrameNumber, layerFilePath):

		self.XMLString += "\t\t\t<Frame>\n\t\t\t\t<Name>" + str(layerName) + "</Name>"
		self.XMLString += "\n\t\t\t\t<Filename>" + str(layerName + self.fileExtension) + "</Filename>"
		self.XMLString += "\n\t\t\t\t<FrameNumber>" + str(FrameNumber) + "</FrameNumber>"
		self.XMLString += "\n\t\t\t\t<Path>" + str(layerFilePath) + "</Path>"
		self.XMLString += "\t\t\t</Frame>\n"

	##########
	#
	# Creates Log File Name and Saves
	# The Log File Based On Save Settings
	#
	##########
	def SaveLogFile(self):

		savePath = ""
		logFile = None
		savePath = (self.filepath + "log_%s" + self.logExtension) % (datetime.datetime.now().strftime("%m%d%Y_%H%M%S"))
		logFile= open(savePath, "w+")
		logFile.write(self.LogString)
		logFile.close()

	#########
	#
	# Closes XML String and Saves String
	# to XML File
	#
	#########
	def SaveXMLFile(self):

		xmlFilePath = ""
		xmlFile = None

		self.XMLString += "\t\t</FrameCollection>\n\t</" + self.FilePrefix + ">\n</UnityAnimation>"
		xmlFilePath = self.filepath
		xmlFile = open((xmlFilePath + "xml_%s" + self.xmlExtension) % (datetime.datetime.now().strftime("%m%d%Y_%H%M%S")), "w+")
		xmlFile.write(self.XMLString)
		xmlFile.close()
		
	##########
	#
	# Removes All Top Layers of the Document.
	#
	##########
	def RemoveTopLayers(self):
		children = self.document.topLevelNodes()
		for layer in children:
			if layer.type() != "grouplayer":
				layer.remove()
				self.AddToLog("Removed Top Layer...")
				
				
	##########
	#
	# Exports All of the Animation Frames
	#
	##########
	def ExportFrames(self):
		children = self.document.topLevelNodes()
		i = 1
		FileSuffix = ""
		for layer in children:
			if i < 10:
				FileSuffix = "_Frame0" + str(i)
			else:
				FileSuffix = "_Frame" + str(i)
			layer.setOpacity(255)
			layer.save(self.filepath + self.FilePrefix + FileSuffix + self.fileExtension, layer.bounds().width(), layer.bounds().height())
			self.AddToLog("Saved Frame " + str(i))
			self.AddToXML(self.FilePrefix + FileSuffix, i, self.filepath + self.FilePrefix + FileSuffix + self.fileExtension)
			i += 1
			
	##########
	#
	# Check to Make Sure There Is An Active Document
	#
	##########
	def CheckDocument(self):
		self.document = Krita.instance().activeDocument()
		if self.document is None:
			self.AddToLog("There is No Active Document! Backing Out!")
			self.NeedToExit = True
			return
		self.AddToLog("Found Active Document...")
			
			
	##########
	#
	# Clone Document, Save it and Set it as Active Document
	#
	##########
	def CloneDocument(self):
		ClonedDocument = self.document.clone()
		self.document = ClonedDocument
		Krita.instance().setActiveDocument(self.document)
		
	##########
	#
	# Starts the Export Process. Core of the Extension.
	#
	##########
	def StartExport(self):	
		
		self.AddToLog("Unity Animation Exporter Log [%s]\n" % (datetime.datetime.now().strftime("%m/%d/%Y")))
		self.AddToLog("Checking Active Document...")
		self.CheckDocument()
		if self.NeedToExit == True:
			return
		self.AddToLog("Cloning Document...")
		self.CloneDocument()
		self.AddToLog("Document Cloned...")		
		self.AddToLog("Setting Data...")
		self.SetPrefix()
		self.SetExtensions()
		self.SetFilePath()
		self.XMLString = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
		self.XMLString += "<UnityAnimation>\n\t<" + self.FilePrefix + ">\n\t\t<FrameCollection>\n"
		self.AddToLog("XML Started...")
		self.AddToLog("Data Set...")
		self.AddToLog("Removing Top Layers...")
		self.RemoveTopLayers()
		self.AddToLog("Top Layers Removed...")
		self.AddToLog("Exporting Frames...")
		self.ExportFrames()
		self.AddToLog("Frames Exported...")
		self.AddToLog("Saving XML...")
		self.SaveXMLFile()
		self.AddToLog("Finished Saving XML...")
		self.AddToLog("Saving Log File...")
		self.SaveLogFile()		

	def __init__(self, parent):
		#Always initialise the superclass, This is necessary to create the underlying C++ object 
		super().__init__(parent)

	def setup(self):
		self.script_abs_path =  os.path.dirname(os.path.realpath(__file__))
		self.ui_file = os.path.join(self.script_abs_path,  UI_FILE)
		self.ui = load_ui(self.ui_file)

		self.ui.button_Cancel.clicked.connect(self.cancel)
		self.ui.button_StartExport.clicked.connect(self.StartExport)
		
	def createActions(self, window):
		action = window.createAction(EXTENSION_ID, MENU_ENTRY, "tools/exporters")
		# parameter 1 =  the name that Krita uses to identify the action
		# parameter 2 = the text to be added to the menu entry for this script
		# parameter 3 = location of menu entry
		action.triggered.connect(self.action_triggered)        
		
	def action_triggered(self):
		self.ui.show()
		self.ui.activateWindow()

	def cancel(self):
		self.ui.close()

# And add the extension to Krita's list of extensions:
app=Krita.instance()
extension=Unity_animation_exporter(parent=app) #instantiate your class
app.addExtension(extension)

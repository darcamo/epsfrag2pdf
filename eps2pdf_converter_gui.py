#!/usr/bin/env python
# -*- coding: utf-8 -*-

from eps2pdf_converter import psfrag_replace
import sys
from PyQt4 import QtCore, QtGui
# from eps2pdf_converter import psfrag_replace


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(350, 250)
        self.setWindowTitle('eps2PDF Converter')

        # Show the status bar
        self.statusBar()

        # xxxxx Menubar and toolbar xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # # Common action
        # exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        # exit.setShortcut('Ctrl+Q')
        # exit.setStatusTip('Exit application')
        # self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        # # Menubar
        # menubar = self.menuBar()
        # file = menubar.addMenu('&File')
        # file.addAction(exit)

        # # Toolbar
        # toolbar = self.addToolBar('Exit')
        # toolbar.addAction(exit)
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # xxxxx Central Area xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # Layout
        centralWindow = QtGui.QWidget()
        self.centralVbox = QtGui.QVBoxLayout()
        centralWindow.setLayout(self.centralVbox)

        # File Input
        self.set_input_file_part()

        # Psfrag Replacements
        self.set_psfragreplacements_part()

        # Ok/Quit buttons part
        self.set_convert_quit_buttons()

        # Set the central widget
        self.setCentralWidget(centralWindow)
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    def set_input_file_part(self):
        """
        Set-up the filename label, line edit and file chooser button
        """
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Input File'))

        self.fileNameText = QtGui.QLineEdit()
        hbox.addWidget(self.fileNameText)
        self.connect(self.fileNameText, QtCore.SIGNAL('editingFinished()'), self.comboBoxChanged)

        fileButton = QtGui.QPushButton('Browse')
        hbox.addWidget(fileButton)

        self.fileChooserDialog = QtGui.QFileDialog(self)
        self.connect(fileButton, QtCore.SIGNAL('clicked()'), self.show_dialog)

        self.centralVbox.addLayout(hbox)

    def set_psfragreplacements_part(self):
        # Text area with the psfrag replacements (from the user or from the file)
        self.inputPsfragReplacements = QtGui.QPlainTextEdit()
        # Variable to store the psfrag replacements from the user when
        # self.inputPsfragReplacements is changed to the content of the
        # file. This way we can restore it later
        self.oldPsfragReplacementText = ""
        # self.connect(self.inputPsfragReplacements,
        # QtCore.SIGNAL('textChanged()'), self.updatePsfragStatus)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Psfrag Replacements:'))
        self.comboBox = QtGui.QComboBox()
        self.comboBox.addItem("User Input")
        self.comboBox.addItem("File Input")
        hbox.addWidget(self.comboBox)
        self.updatePsfragReplacementsFromUser()
        self.connect(self.comboBox, QtCore.SIGNAL('currentIndexChanged(int)'), self.comboBoxChanged)

        self.centralVbox.addLayout(hbox)
        self.centralVbox.addWidget(self.inputPsfragReplacements)

    def comboBoxChanged(self):
        currentIndex = self.comboBox.currentIndex()
        if(currentIndex == 0):
            self.updatePsfragReplacementsFromUser()

        if(currentIndex == 1):
            self.updatePsfragReplacementsFromFile()

    def updatePsfragReplacementsFromUser(self):
        """
        When the combobox changes to the User Input this function changes
        the text area with the psfrag replacements accordingly also
        restoring any previously text input by the user.
        """
        self.statusBar().showMessage("Using psfrag replacements from user input", 3000)
        self.inputPsfragReplacements.setPlainText(self.oldPsfragReplacementText)
        self.inputPsfragReplacements.setEnabled(True)

    def updatePsfragReplacementsFromFile(self):
        """
        When the combobox changes to the File Input this function changes
        the text area with the psfrag replacements accordingly.
        """
        self.inputPsfragReplacements.setEnabled(False)
        self.oldPsfragReplacementText = self.inputPsfragReplacements.toPlainText()
        (figDir, figShortName, figExtension) = self.getCanonizeFigName()
        # Name of the file with psfrag replacements (if it exists)
        psfragFile = QtCore.QFile(figDir.absolutePath() + "/" + figShortName + ".psfrags")

        # This will have the psfrag replacements text at the end of the
        # function
        psfragText = ""
        if(psfragFile.exists()):
            psfragFile.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
            psfragText = psfragFile.readAll()
            psfragFile.close()
            self.statusBar().showMessage("Using psfrag replacements from file %s.psfrags" % psfragFile, 3000)
        else:
            self.statusBar().showMessage("File %s.psfrags does not exist" % figName, 3000)

        # TODO: Change QtCore.QString(psfragText) to something that can
        # handle accentuated characters
        self.inputPsfragReplacements.setPlainText(QtCore.QString.fromUtf8(psfragText))

        # figName = self.fileNameText.text()
        # psfragText = ""
        # if(os.path.isfile("%s.psfrags" % figName)):
        #     fID = open("%s.psfrags" % figName)
        #     psfragText = QtCore.QString(fID.read())
        #     fID.close()
        #     self.statusBar().showMessage("Using psfrag replacements from file %s.psfrags" % figName,3000)
        # else:
        #     self.statusBar().showMessage("File %s.psfrags does not exist" % figName,3000)
        # self.inputPsfragReplacements.setPlainText(psfragText)

    def show_dialog(self):
        text = QtGui.QFileDialog.getOpenFileName(
            self,
            filter="Eps files (*.eps);;All Files (*)")
        # If the user cancel the dialog text will be None and we don't
        # change whatever is in fileNameText
        if text:
            self.fileNameText.setText(text)

    def set_convert_quit_buttons(self):
        hbox = QtGui.QHBoxLayout()
        okButton = QtGui.QPushButton("&Convert")
        quitButton = QtGui.QPushButton("&Quit")
        hbox.addWidget(okButton)
        hbox.addWidget(quitButton)
        self.centralVbox.addLayout(hbox)

        # Connect the clicked signals
        self.connect(quitButton, QtCore.SIGNAL('clicked()'), QtCore.SLOT("close()"))
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self.convert)

    # def updatePsfragStatus(self):
    #     psfragText = self.inputPsfragReplacements.toPlainText()
    #     if psfragText.simplified().isEmpty():
    #         self.statusBar().showMessage("No psfrag replacements",3000)

    def getCanonizeFigName(self):
        """
        Separate the path from the file name and also separates the file
        name from the file extension.
        """
        figFullName = self.fileNameText.text()
        fi = QtCore.QFileInfo(figFullName)
        figName = fi.fileName()
        figDir = fi.absoluteDir()
        figShortName = fi.baseName()
        figExtension = fi.completeSuffix()

        # (figDir, figName) = os.path.split(str(figFullName))
        # (figShortName,figExtension) = os.path.splitext(figName)
        return (figDir, figShortName, figExtension)

    def convert(self):
        figFullName = self.fileNameText.text()
        (figDir, figShortName, figExtension) = self.getCanonizeFigName()
        # QDir.setCurrent (QString path)
        # We use the strip function to remove white spaces
        psfrag = self.inputPsfragReplacements.toPlainText()
        if psfrag.simplified().isEmpty():
            self.statusBar().showMessage("Warning: Psfrag Replacements Empty", 3000)
        figNameNoExt = figDir.absolutePath() + "/" + figShortName
        exit_code = psfrag_replace(str(figNameNoExt), str(psfrag.toUtf8()))
        if(exit_code != 0):
            self.statusBar().showMessage("Conversion problems", 3000)
        else:
            self.statusBar().showMessage("Conversion Finished", 3000)

    #
    #
    #
    #
    # def closeEvent(self, event):
    #     reply = QtGui.QMessageBox.question(self, 'Message',
    #         "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    #     if reply == QtGui.QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

# eps2pdf_converter ends here

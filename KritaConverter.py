import os
import glob
import configparser
import tkinter, tkinter.constants, tkinter.filedialog


class MassImageConverterApp(tkinter.Tk):

    def __init__(self, parent):

        #store reference to config file
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        

        tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.InitializeApp()


    def InitializeApp(self):
        self.grid()
        KritaConverterWindow(self).grid(column = 0, row = 0, sticky = tkinter.constants.NSEW)

        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)


    def GetFromConfigFile(self, section: str, entry: str):
        return self.config.get(section, entry)

    #HELPER FUNCTION FOR UPDATING CONFIG FILE
    def UpdateConfigFile(self, section: str, entry: str, data: str):
        self.config.set(section, entry, data)
        with open("config.ini", "w") as configFile:
            self.config.write(configFile)



class KritaConverterWindow(tkinter.Frame):

#CONSTRUCTOR
    def __init__(self, parent):

        #self.controller = controller
        self.parent = parent

        self.fileTypes = options = {}
        options["PNG"] = [".png"]
        options["JPG"] = [".jpg"]
        options["TIFF"] = [".tiff", ".tif"]

        #set a default
        self.currentFileType_ConvertFrom = self.parent.GetFromConfigFile("UserInfo", "lastfiletoconvertfrom")#"TIFF"
        self.currentFileType_ConvertTo = self.parent.GetFromConfigFile("UserInfo", "lastfiletoconvertto") #"PNG"


        self.targetDir = self.parent.GetFromConfigFile("UserInfo", "lastopendir")
        self.saveDir = self.parent.GetFromConfigFile("UserInfo", "targetsavedir")

        self.filesToConvert = self.GetFilesFromFolder(self.currentFileType_ConvertFrom, self.targetDir)

        #parent.title = "Mass Tiff Converter"

        #FILE OPTIONS
        self.file_opt = options = {} #options dictionary for files
        options["defaultextension"] = ".txt"
        options["filetypes"] = [("all files", ".*"), ("text files", ".txt")]
        options["initialdir"] = "C:\\"
        options["initialfile"] = "myfile.txt"
        options["parent"] = parent
        options["title"] = "This is a title for Files."

        #DIRECTORY OPTIONS
        self.dir_opt = options = {} #options dictionary for directories/files
        options["initialdir"] = self.targetDir
        options["mustexist"] = False
        options["parent"] = parent
        options["title"] = "Open Folder To Mass Convert Images"

        #BUTTON OPTIONS
        self.button_opt = options = {}
        options["fill"] = tkinter.constants.BOTH
        options["padx"] = 5
        options["pady"] = 5


        #initialize the TKinter frame we'll be drawing to
        tkinter.Frame.__init__(self, parent)

    #OPEN FOLDER
        tkinter.Button(self,
                       text="Open Folder",
                       command=self.AskOpenDirectory).pack(**self.button_opt)


    #HORIZONTAL GROUPING BAR
        #make a horizontal bar to contain the buttons for setting conversion settings
        conversionSettings_HorBar = tkinter.Frame(self)
        conversionSettings_HorBar.pack()


    #SET FILE TYPE WE WANT CONVERTED FROM
        curFileTypeToConvStrVal = tkinter.StringVar(value = self.currentFileType_ConvertFrom)

        tkinter.OptionMenu(conversionSettings_HorBar,
                           curFileTypeToConvStrVal,
                           *list(self.fileTypes.keys()),
                           command = self.UpdateTargetFileType_ConvertFrom).pack(side = tkinter.LEFT)

        self.currentFileType_ConvertFrom = curFileTypeToConvStrVal.get()


    #LABEL TO MAKE CONVERSION LOGIC CLEAR (hopefully)
        tkinter.Label(conversionSettings_HorBar, text = "->").pack(side = tkinter.LEFT)


    #SET FILE TYPE WE WANT TO CONVERT TO
        curFileTypeConvTarget = tkinter.StringVar(value = self.currentFileType_ConvertTo)

        tkinter.OptionMenu(conversionSettings_HorBar,
                           curFileTypeConvTarget,
                           *list(self.fileTypes.keys()),
                           command = self.UpdateTargetFileType_ConverTo).pack(side = tkinter.LEFT)

        self.currentFileType_ConvertTo = curFileTypeConvTarget.get()


    #RELOAD BUTTON
        tkinter.Button(self,
                       text = "Reload Files",
                       command = self.UpdateListbox).pack()



    #DISPLAY ALL FILES THAT WILL BE ALTERED
        self.listBox_TargetFiles = tkinter.Listbox(self)
        self.listBox_TargetFiles.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH, expand = True)
        #self.listBox_TargetFiles.grid(column = 0, row = 0, weight = 1)

        #populate the list box in case we had any info we wanted to throw in there
        self.PopulateListBox_TargetFiles(self.filesToConvert)



#POPULATE LIST BOX WITH FILES WE WITH TO CONVERT
    def PopulateListBox_TargetFiles(self, fileNames: str):
        #clear list box
        self.listBox_TargetFiles.delete(0, tkinter.END)

        for fN in fileNames:
            self.listBox_TargetFiles.insert(tkinter.END, fN)


    def GetFilesFromFolder(self, fileType: str, folderPath: str):

        #for each supplied file extension, construct a string of the path to the target directory, the wildcard, and the file extension
            #ie, folderPath/*.fileExten
        filePaths = ["%s/*%s"%(folderPath, p) for p in self.fileTypes[fileType]]

        foundFiles = []
        for fPath in filePaths:
            foundFiles.extend(glob.glob(fPath))

        return foundFiles

#HELPER FUNCTION TO AUTOMATE UPDATING LIST BOX WITH NEW FILES
    def UpdateListbox(self):
        #update the list of all files we think we can convert
        self.UpdateTargetFileType_ConvertFrom(self.currentFileType_ConvertFrom)

        print(self.filesToConvert)

        #self.PopulateListBox_TargetFiles(self.GetFilesFromFolder(self.currentFileType_ConvertFrom,
        #                                                         self.targetDir))


    def UpdateTargetFileType_ConvertFrom(self, fType):
        self.currentFileType_ConvertFrom = fType
        self.filesToConvert = self.GetFilesFromFolder(fType, self.targetDir)

        self.PopulateListBox_TargetFiles(self.filesToConvert)

        #update config file so we remember our setting next time we open the program
        self.parent.UpdateConfigFile("UserInfo", "lastfiletoconvertfrom", self.currentFileType_ConvertFrom)

        #self.UpdateListbox()

    def UpdateTargetFileType_ConverTo(self, fType):
        self.currentFileType_ConvertTo = fType

        #update config file so we remember our setting next time we open the program
        self.parent.UpdateConfigFile("UserInfo", "lastfiletoconvertto", self.currentFileType_ConvertTo)

    # def UpdateListbox(self, fType = None):
    #     if fType is None:
    #         fType = self.currentFileType_ConvertFrom

    #     self.PopulateListBox_TargetFiles(self.GetFilesFromFolder(fType,
    #                                                              self.targetDir))

#BINDING FUNCTIONS FOR UI ELEMENTS
    def AskOpenFile(self):
        fileName = tkinter.filedialog.askopenfile(mode="r", **self.file_opt)

        if fileName:
            print(fileName)

        return fileName


    def AskOpenDirectory(self):
        dirName = tkinter.filedialog.askdirectory(**self.dir_opt)

        if dirName:
            self.targetDir = dirName
            #fing out how to get parent's config variable
            self.parent.UpdateConfigFile("UserInfo", "lastopendir", dirName)
            #self.parent.config.set("UserInfo", "lastopendir", "jkl;;;lkj")
            #config.
            print(dirName)

            #print(self.parent.config.sections())

        return dirName



if __name__ == "__main__":
    # ROOT = tkinter.Tk()
    # KritaConverterWindow(ROOT).grid(sticky = tkinter.NSEW)
    # ROOT.mainloop()


    app = MassImageConverterApp(None)
    app.title("Mass Image Converter")
    app.mainloop()

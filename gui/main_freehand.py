#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object labeles for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014

#
#-------------------------------------------------------------------------------
from __future__ import division
from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random
import numpy as np
import cv2

# image sizes for the examples
SIZE = 256, 256

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # Colors
        self.palette = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green']
        self.used_colors = []
        self.unused_colors = self.palette

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''


        # Image
        self.cvimg = None
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to label
        self.labelIdList = []
        self.labelId = None
        self.labelList = []
        self.hl = None
        self.vl = None

        # Label Dictionary
        self.labels = {}

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1, sticky = W+E)
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = 0, column = 5, sticky = W+E)

        # main panel for labeling
        #self.mainPanel = Canvas(self.frame, cursor='tcross')
        #self.mainPanel.grid(row = 1, column = 0, rowspan = 5, columnspan = 4)


        #self.frame.grid(row=0,column=0)
        self.mainPanel=Canvas(self.frame,bg='#FFFFFF',width=300,height=300,scrollregion=(0,0,500,500))
        self.mainPanel.grid(row = 1, column = 0, rowspan = 5, columnspan = 4)
        
        hbar=Scrollbar(self.frame,orient=HORIZONTAL)
        hbar.grid(row=1, column=0, rowspan = 1, columnspan=1)
        #hbar.pack(side=BOTTOM,fill=X)
        hbar.config(command=self.mainPanel.xview)
        vbar=Scrollbar(self.frame,orient=VERTICAL)
        hbar.grid(row=1, column=0, rowspan = 1, columnspan=1)     
        #vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=self.mainPanel.yview)
        self.mainPanel.config(width=300,height=300)
        self.mainPanel.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        #self.mainPanel.pack(side=LEFT,expand=True,fill=BOTH)


        

        # Mouse
        self.mainPanel.bind("<ButtonPress-1>", self.mousePress)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.mainPanel.bind("<ButtonRelease-1>", self.mouseRelease)


        # Mask
        self.maskPanel = Label(self.frame, image = PhotoImage(None))
        self.maskPanel.grid(row = 1, column = 4)



        # Keyboard
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward

        # showing label info & delete label
        self.lb1 = Label(self.frame, text = 'Labels')
        self.lb1.grid(row = 1, column = 5, columnspan = 2, sticky = W+N)

        self.listbox = Listbox(self.frame, width = 22, height = 12)
        self.listbox.grid(row = 2, column = 5, columnspan = 2, sticky = N)
        self.listbox.select_set(0)        

        self.btnAdd = Button(self.frame, text = 'Add', command = self.addLabel)
        self.btnAdd.grid(row = 3, column = 5, columnspan = 1, sticky = W+E+N)  
        self.txtAdd = Entry(self.frame)
        self.txtAdd.grid(row = 3, column = 6, columnspan = 1, sticky = W+E)
        self.btnDel = Button(self.frame, text = 'Delete', command = self.delLabel)
        self.btnDel.grid(row = 4, column = 5, columnspan = 2, sticky = W+E+N)

        
        #self.listbox.bind("<ButtonPress-1>", self.labelPress)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)


        

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        self.drawing = False
        self.initial_x = 0
        self.initial_y = 0
        self.previous_x = 0
        self.previous_y = 0



    def loadDir(self, dbg = False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'

        # get image list
        self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))
        #self.imageList = glob.glob(os.path.join(self.imageDir, '*.JPEG'))
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        if len(self.imageList) == 0:
            print 'No .JPEG images found in the specified dir!'
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(r'./Labels', '%03d' %(self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        """
        # load example labeles
        self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        if not os.path.exists(self.egDir):
            return
        filelist = glob.glob(os.path.join(self.egDir, '*.JPEG'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])
        """

        self.loadImage()
        print '%d images loaded from %s' %(self.total, s)

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]

        self.cvimg = cv2.imread(imagepath)
        image = cv2.cvtColor( self.cvimg, cv2.COLOR_BGR2RGB )
        image = Image.fromarray(image)
        self.tkimg = ImageTk.PhotoImage(image)

        #self.img = Image.open(imagepath)       
        #self.tkimg = ImageTk.PhotoImage(self.img)

        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        #self.maskPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

        # load labels
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        label_cnt = 0
        """
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        label_cnt = int(line.strip())
                        continue
                    tmp = [int(t.strip()) for t in line.split()]
##                    print tmp
                    self.labelList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[2], tmp[3], \
                                                            width = 2, \
                                                            outline = COLORS[(len(self.labelList)-1) % len(COLORS)])
                    self.labelIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(tmp[0], tmp[1], tmp[2], tmp[3]))
                    self.listbox.itemconfig(len(self.labelIdList) - 1, fg = COLORS[(len(self.labelIdList) - 1) % len(COLORS)])
        """



    
    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.labelList))
            for label in self.labelList:
                f.write(' '.join(map(str, label)) + '\n')
        print 'Image No. %d saved' %(self.cur)

    # Freehand Mouse Callback Function
    def mousePress(self, event):
        self.drawing=True
        self.initial_x=event.x
        self.initial_y=event.y
        self.previous_x=event.x
        self.previous_y=event.y

    def mouseMove(self, event):
        # Listbox Selection
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        label = self.labelList[idx]  

        # Draw Line and Store
        if self.drawing==True:
            self.mainPanel.create_line(self.previous_x,self.previous_y,event.x,event.y, width=10, fill=self.labels[label]["color"])
            self.previous_x = event.x
            self.previous_y = event.y

    def mouseRelease(self, event):
        # Listbox Selection
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        label = self.labelList[idx]

        # Draw Line and Store
        self.drawing=False
        self.mainPanel.create_line(self.initial_x,self.initial_y,event.x,event.y, width=10, fill=self.labels[label]["color"])            
        

    """
    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.labelList.append((x1, y1, x2, y2))
            self.labelIdList.append(self.labelId)
            self.labelId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.labelIdList) - 1, fg = COLORS[(len(self.labelIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.labelId:
                self.mainPanel.delete(self.labelId)
            self.labelId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[len(self.labelList) % len(COLORS)])
    """




    def addLabel(self):
        # Fetch and Clear Entry
        s = self.txtAdd.get()
        self.txtAdd.delete(0, 'end')
        
        # Random Color
        color = random.sample(self.unused_colors,1)
        self.used_colors = list( set(self.used_colors) | set(color) )
        self.unused_colors = list( set(self.unused_colors) - set(color) )

        # Add Label to Dictionary
        self.labels[s] = {}
        self.labels[s]["lines"] = [] # Store Polygon Lines
        self.labels[s]["color"] = color # Store Color
        self.labels[s]["mask"] = np.zeros((self.tkimg.width(), self.tkimg.height()), dtype=bool)

        #self.mainPanel.create_image(0, 0, image = [ int(255*px) for px in self.labels[s]["mask"]], anchor=SE)


        # Keep Track of Label List Index
        self.labelList.append(s)
        self.listbox.insert(END, s)
        self.listbox.itemconfigure(END, background=color)

        # Reset Listbox Select
        self.listbox.select_set(0)         


    def delLabel(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        label = self.labelList[idx]
        
        #self.mainPanel.delete(self.labelIdList[idx])
        #self.labelIdList.pop(idx)

        # Free Color
        color = self.labels[label]["color"]
        self.used_colors = list( set(self.used_colors) - set(color) )
        self.unused_colors = list( set(self.unused_colors) | set(color) )

        # Delete Label
        del self.labels[ label ]

        # Clear Entry from Listbox
        self.labelList.pop(idx)
        self.listbox.delete(idx)

        # Reset Listbox Select
        self.listbox.select_set(0)        








    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.mainPanel.delete("all")
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.mainPanel.delete("all")                    
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.mainPanel.delete("all")            
            self.cur = idx
            self.loadImage()


if __name__ == '__main__':
    root = Tk()

    # Maximize Window
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h)) 

    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()

from __future__ import division
from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random
import numpy as np
import cv2

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        
        self.width, self.height = master.winfo_screenwidth(), master.winfo_screenheight()
        self.width -= 200
        self.height -= 200


        # Window
        self.parent = master
        self.parent.title("LabelTool")


        # Main Frame
        self.main_frame = Frame(self.parent, bg="Red")
        self.main_frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # Possible Colors
        self.palette = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green']
        self.used_colors = []
        self.unused_colors = self.palette

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.outDir = ''
        self.current_image = 0
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

        ##############################################################
        # Sub-Frames

        # Directory Frame (Load + Save)
        self.dir_frame = Frame(self.main_frame, bg="Blue")
        self.dir_frame.grid(row=0, column=0, sticky=NSEW)

        # Label Frame (Show Labels)
        self.label_frame = Frame(self.main_frame, bg="Green")
        self.label_frame.grid(row=1, column=0, sticky=NSEW)

        # Navigation Frame (Switch Between Images)
        self.nav_frame = Frame(self.main_frame, bg="Blue")
        self.nav_frame.grid(row=2, column=0, sticky=NSEW)

        # Grade Frame
        self.grade_frame = Frame(self.main_frame, bg="Yellow")
        self.nav_frame.grid(row=3, column=0, sticky=NSEW)


        # Image Frame (Show Images)
        self.img_frame = Frame(self.main_frame, bg="Green")
        self.img_frame.grid(row=0, rowspan=4, column=1, sticky=NSEW)

        ##############################################################


        ##############################################################
        # Directory Frame
        self.dir_label = Label(self.dir_frame, text="Image Directory")
        self.dir_label.pack(side=LEFT)

        self.dir_entry = Entry(self.dir_frame)
        self.dir_entry.pack(side=LEFT)

        self.dir_button = Button(self.dir_frame, text="Load", command = self.loadDir)
        self.dir_button.pack(side=LEFT)

        ##############################################################
        # Label Frame
        self.label_label = Label(self.label_frame, text="Labels")
        self.label_label.grid(row=0, column=0, columnspan=3)

        self.label_listbox = Listbox(self.label_frame, width=30, height=30)
        self.label_listbox.grid(row=1, column=0, columnspan=3)

        self.label_addLabel = Button(self.label_frame, text="ADD", command=self.addLabel)
        self.label_addLabel.grid(row=2, column=0)

        self.label_txtLabel = Entry(self.label_frame)
        self.label_txtLabel.grid(row=2, column=1)

        self.label_delLabel = Button(self.label_frame, text="DEL", command=self.delLabel)
        self.label_delLabel.grid(row=2, column=2)

        self.label_plot = Button(self.label_frame, text="PLOT", command=self.plotLabel)
        self.label_plot.grid(row=3, column=0, columnspan=3)

        ##############################################################
        # Navigation Frame
        self.prevBtn = Button(self.nav_frame, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.grid(row=0, column=0, columnspan=3)
        self.nextBtn = Button(self.nav_frame, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.grid(row=0, column=3, columnspan=3)

        self.progLabel = Label(self.nav_frame, text = "Progress:     /    ")
        self.progLabel.grid(row=1, column=0, columnspan=6)

        self.tmpLabel = Label(self.nav_frame, text = "Go to Image No.")
        self.tmpLabel.grid(row=2, column=0, columnspan=2)
        self.idxEntry = Entry(self.nav_frame, width = 5)
        self.idxEntry.grid(row=2, column=2, columnspan=2)
        self.goBtn = Button(self.nav_frame, text = 'Go', command = self.gotoImage)
        self.goBtn.grid(row=2, column=4,columnspan=2)






        # Display Mouse Position
        self.disp = Label(self.nav_frame, text='')
        self.disp.grid(row=3, column=0, columnspan = 6)        


        ##############################################################
        # Image Frame

        self.img_canvas = Canvas(self.img_frame, cursor='tcross', width=self.width, height=self.height)
        self.img_canvas.grid(row=0, column=0)

        self.img_mask = Canvas(self.img_frame, cursor='tcross', width=100, height=100)
        self.img_mask.grid(row=0, column=1)

        ##############################################################
        # Mouse
        self.img_canvas.bind("<ButtonPress-1>", self.mousePress)
        self.img_canvas.bind("<Motion>", self.mouseMove)
        self.img_canvas.bind("<ButtonRelease-1>", self.mouseRelease)

        ##############################################################
        # Keyboard Bindings
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward


        self.drawing = False
        self.initial_x = 0
        self.initial_y = 0
        self.previous_x = 0
        self.previous_y = 0



    def loadDir(self, dbg = False):
        if not dbg:
            s = self.dir_entry.get()
            self.parent.focus()
            self.category = int(s)


        # get image list
        self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))

        #self.imageList = glob.glob(os.path.join(self.imageDir, '*.JPEG'))
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        if len(self.imageList) == 0:
            print 'No .JPEG images found in the specified dir!'
            return

        # default to the 1st image in the collection
        self.current_image = 1
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
        imagepath = self.imageList[self.current_image - 1]

        self.cvimg = cv2.imread(imagepath)
        image = cv2.cvtColor( self.cvimg, cv2.COLOR_BGR2RGB )
        image = Image.fromarray(image)


        #self.image_width_original = image.width()
        #self.image_height_original = image.height()

        


        # Resize Image
        r = min(self.width / image.size[0], self.height / image.size[1])

        self.resize_factor = r

        new_size = int(r * image.size[0]), int(r * image.size[1])

        self.tkimg = ImageTk.PhotoImage(image.resize(new_size, Image.ANTIALIAS))
        #self.tkimg.config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])
        #self.tkimg = ImageTk.PhotoImage(image)




        #self.img = Image.open(imagepath)       
        #self.tkimg = ImageTk.PhotoImage(self.img)

        self.img_canvas.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        #self.img_canvas.config(width = 800, height = 800)
        self.img_canvas.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.current_image, self.total))

        #self.maskPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

        # load labels
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        label_cnt = 0

        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                
                print f

                for (i, line) in enumerate(f):


                    tmp = [t.strip() for t in line.split()]

                    #print tmp


                    label = tmp[0]
                    rect = [ int(self.resize_factor*int(t)) for t in tmp[4:8]]
                    
                    #print label, rect

                    #print i, line

                    #if i == 0:
                    #    label_cnt = int(line.strip())
                    #    continue
                    



                    # Add Label to Dictionary
                    if label not in self.labels.keys():

                        # Random Color
                        if len(self.unused_colors)==0:
                            self.unused_colors = self.palette

                        color = random.sample(self.unused_colors,1)
                        self.used_colors = list( set(self.used_colors) | set(color) )
                        self.unused_colors = list( set(self.unused_colors) - set(color) )

                        # Dictionary                        
                        self.labels[label] = {}
                        self.labels[label]["rect"] = []
                        self.labels[label]["lines"] = [] # Store Polygon Lines
                        self.labels[label]["color"] = color # Store Color

                        # Keep Track of Label List Index
                        self.labelList.append(label)
                        self.label_listbox.insert(END, label)
                        self.label_listbox.itemconfigure(END, background=color)

                        # Reset Listbox Select
                        self.label_listbox.select_set(0) 


                    # Draw Rectangle
                    self.labels[label]["rect"].append( (rect[0], rect[1], rect[2], rect[3]) )
                    
                    tmpId = self.img_canvas.create_rectangle(rect[0], rect[1], \
                                                            rect[2], rect[3], \
                                                            width = 2, \
                                                            outline = color)


 




    
    def saveImage(self):
        #with open(self.labelfilename, 'w') as f:
        #    f.write('%d\n' %len(self.labelList))
        #    for label in self.labelList:
        #        f.write(' '.join(map(str, label)) + '\n')
        print 'Image No. %d saved' %(self.current_image)

    # Freehand Mouse Callback Function
    def mousePress(self, event):
        self.drawing=True
        self.initial_x=event.x
        self.initial_y=event.y
        self.previous_x=event.x
        self.previous_y=event.y

    def mouseMove(self, event):

        # Mouse Coordinates
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))

        # Listbox Selection
        sel = self.label_listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        label = self.labelList[idx]  

        # Draw Line and Store
        if self.drawing==True:
            self.img_canvas.create_line(self.previous_x,self.previous_y,event.x,event.y, width=10, fill=self.labels[label]["color"])
            self.previous_x = event.x
            self.previous_y = event.y

    def mouseRelease(self, event):
        # Listbox Selection
        sel = self.label_listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        label = self.labelList[idx]

        # Draw Line and Store
        self.drawing=False
        self.img_canvas.create_line(self.initial_x,self.initial_y,event.x,event.y, width=10, fill=self.labels[label]["color"])            
        

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
                self.img_canvas.delete(self.hl)
            self.hl = self.img_canvas.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.img_canvas.delete(self.vl)
            self.vl = self.img_canvas.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.labelId:
                self.img_canvas.delete(self.labelId)
            self.labelId = self.img_canvas.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[len(self.labelList) % len(COLORS)])
    """




    def addLabel(self):
        # Fetch and Clear Entry
        s = self.label_txtLabel.get()
        self.label_txtLabel.delete(0, 'end')
        
        # Random Color
        if len(self.unused_colors)==0:
            self.unused_colors = self.palette

        color = random.sample(self.unused_colors,1)
        self.used_colors = list( set(self.used_colors) | set(color) )
        self.unused_colors = list( set(self.unused_colors) - set(color) )

        # Add Label to Dictionary
        self.labels[s] = {}
        self.labels[s]["rect"] = []
        self.labels[s]["lines"] = [] # Store Polygon Lines
        self.labels[s]["color"] = color # Store Color
        self.labels[s]["mask"] = np.zeros((self.tkimg.width(), self.tkimg.height()), dtype=bool)

        #self.img_canvas.create_image(0, 0, image = [ int(255*px) for px in self.labels[s]["mask"]], anchor=SE)


        # Keep Track of Label List Index
        self.labelList.append(s)
        self.label_listbox.insert(END, s)
        self.label_listbox.itemconfigure(END, background=color)

        # Reset Listbox Select
        self.label_listbox.select_set(0)         


    def delLabel(self):
        sel = self.label_listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        label = self.labelList[idx]
        
        #self.img_canvas.delete(self.labelIdList[idx])
        #self.labelIdList.pop(idx)

        # Free Color
        color = self.labels[label]["color"]
        self.used_colors = list( set(self.used_colors) - set(color) )
        self.unused_colors = list( set(self.unused_colors) | set(color) )

        # Delete Label
        del self.labels[ label ]

        # Clear Entry from Listbox
        self.labelList.pop(idx)
        self.label_listbox.delete(idx)

        # Reset Listbox Select
        self.label_listbox.select_set(0)        


    def plotLabel(self):

        sel = self.label_listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        label = self.labelList[idx]

        #color = self.labels[label]["color"]


        for x1,y1,x2,y2 in self.labels[label]["rect"]:


            print x1,y1,x2,y2

            image = cv2.cvtColor( self.cvimg, cv2.COLOR_BGR2RGB )
            image = image[y1:y2,x1:x2]
            
            #cv2.imshow("cropped", image)
            #cv2.waitKey(0)

            image = Image.fromarray(image)



            print image

            new_size = int(self.resize_factor * image.size[0]), int(self.resize_factor * image.size[1])

            #tk_image = ImageTk.PhotoImage(image.resize(new_size, Image.ANTIALIAS))
            tk_image = ImageTk.PhotoImage(image)        


            self.img_mask.config(width = max(tk_image.width(), 400), height = max(tk_image.height(), 400))
            self.img_mask.create_image(0, 0, image = tk_image, anchor=NW)







    def prevImage(self, event = None):
        self.saveImage()
        if self.current_image > 1:
            self.current_image -= 1
            self.img_canvas.delete("all")
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.current_image < self.total:
            self.current_image += 1
            self.img_canvas.delete("all")                    
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.img_canvas.delete("all")            
            self.current_image = idx
            self.loadImage()


"""
if __name__ == '__main__':
    root = Tk()

    # Maximize Window
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h)) 

    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
"""
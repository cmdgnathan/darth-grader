from __future__ import division
from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random
import numpy as np
import cv2

from grader_gui import LabelTool



if __name__ == '__main__':
    root = Tk()

    # Maximize Window
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h)) 

    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()

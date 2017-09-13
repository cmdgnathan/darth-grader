import numpy as numpy
import cv2
from matplotlib import pyplot as plt
import re
from PIL import Image
import pytesseract
import os
import pprint

from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random
import numpy as np
import cv2

import copy

from grader_gui import LabelTool



class GradeData():

    def __init__(self, hw_dirs, assignment, weights):



        # Parse String
        s_spaces = re.split('\s', assignment)
        s_problems = [filter(None, re.split('(.*\d)', s)) for s in s_spaces]
        s_subproblems = [ [filter(None, re.split(r"([a-zA-Z])", s)) for s in sp] for sp in s_problems ]

        s_grade = [ int(filter(None, re.split('(.*\d)', s))[0]) for s in re.split("\s", weights) ]


        print "----------------"
        print "Parse Assignment"
        print "Problems:", s_problems
        print "Sub-Problems:", s_subproblems
        print "Grade:", s_grade



        # Create Dictionary
        self.homework = {}
        for idx, prob in enumerate(s_subproblems):    
            self.homework[ prob[0][0] ] = {}

            self.homework[ prob[0][0] ][ 'all' ] = {}

            # Label   
            self.homework[ prob[0][0] ]["all"]["label"] = []

            # Grade
            self.homework[ prob[0][0] ]["all"]["grade"] = 0
            self.homework[ prob[0][0] ]["all"]["max_grade"] = s_grade[ idx ] 

            if len(prob)>1:
                for sub in prob[1]:
                    self.homework[ prob[0][0] ][ sub ] = {}
            

        print "--------------"
        print "Reading Labels"


        # Students ( Students )
        # Base keys off of folder names
        self.students = {}

        for dirs in os.listdir(hw_dirs):

            self.students[dirs] = {}


        for student in self.students.keys():

            print student

            self.students[student]["homework"] = self.homework

            for subdir, dirs, files in os.walk( os.path.join(hw_dirs, student) ):


                print subdir, dirs, files

                for file in files:



                    self.students[student][file] = os.path.join(subdir, file)

                    # Text File
                    if file.endswith(".txt"):

                        with open( os.path.join(subdir, file) ) as f:

                            labels = {}
                            print " "*5, "Reading", f
                            for line in f:
                                print " "*10, line,        
                                entry = line.split()

                                prob = filter(None, re.split('(.*\d)', entry[0]))

                                file_rect = {}
                                file_rect["file"] = os.path.join(subdir, file)
                                file_rect["rect"] = ( int(entry[4]), int(entry[5]), int(entry[6]), int(entry[7]) )

                                self.students[student]["homework"][prob[0]]["all"]["label"].append( \
                                    dict([ ( "file", os.path.join(subdir, file) ), \
                                           ( "rect", ( int(entry[4]), int(entry[5]), int(entry[6]), int(entry[7]) ) ) ]) )


        # Print Data Structure
        pprint.pprint(self.students)





    def show_problem(self, problem):

        for student in self.students.keys():

            label_array = self.students[student]["homework"][problem]["all"]["label"]

            for file_rect in label_array:


                print file_rect["file"]

                filename = file_rect["file"][0:-4]
                filename = filename+'.jpg'


                x1, y1, x2, y2 = file_rect["rect"]


                # Read Image
                img = cv2.imread(filename)   


                f, axarr = plt.subplots(1,2)

                img_rect = img.copy()
                img_rect = cv2.rectangle(img_rect, (x1,y1),(x2,y2),(255,0,0),10)

                # Isolated
                axarr[0].imshow(img_rect)


                axarr[1].set_title(student+" "+problem)
                axarr[1].imshow(img[y1:y2,x1:x2])


                mng = plt.get_current_fig_manager()
                mng.resize(*mng.window.maxsize())


                plt.draw()


                cid = f.canvas.mpl_connect('key_press_event', self.keypress)

                plt.waitforbuttonpress(0)

                plt.close(f)



                #pprint.pprint(self.students)






    def keypress(self, event):

        if (event.key).isdigit():
            self.students[student]["homework"][problem]["all"]["grade"] = int(event.key)














if __name__ == '__main__':

    # Data Structure
    directory = "../hw1"
    assignment = "2.1cdefg 2.7abd 2.21abcde"
    grade = "5 5 5"

    # Grade Data
    g = GradeData(directory, assignment, grade)

    g.show_problem("2.1")

    # GUI
    root = Tk()

    # Maximize Window
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h)) 

    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()

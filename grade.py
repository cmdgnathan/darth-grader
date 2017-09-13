import numpy as numpy
import cv2
from matplotlib import pyplot as plt
import re
from PIL import Image
import pytesseract
import os
import pprint

file_base = "hw1-page-001"

assignment = "2.1cdefg 2.7abd 2.21abcde"
grade = "5 5 5"


#assignment = "2.2ab 2.10abcd 2.11 2.12 2.13 2.15 2.18 2.19 2.28abc 2.38 2.62 2.63abc 2.78"

# Parse String
s_spaces = re.split('\s', assignment)
s_problems = [filter(None, re.split('(.*\d)', s)) for s in s_spaces]
s_subproblems = [ [filter(None, re.split(r"([a-zA-Z])", s)) for s in sp] for sp in s_problems ]

s_grade = [ int(filter(None, re.split('(.*\d)', s))[0]) for s in re.split("\s", grade) ]


print "----------------"
print "Parse Assignment"
print "Problems:", s_problems
print "Sub-Problems:", s_subproblems
print "Grade:", s_grade



# Create Dictionary
homework = {}
for idx, prob in enumerate(s_subproblems):    
    homework[ prob[0][0] ] = {}

    homework[ prob[0][0] ][ 'all' ] = {}

    # Label   
    homework[ prob[0][0] ]["all"]["label"] = []

    # Grade
    homework[ prob[0][0] ]["all"]["grade"] = 0
    homework[ prob[0][0] ]["all"]["max_grade"] = s_grade[ idx ] 

    if len(prob)>1:
        for sub in prob[1]:
            homework[ prob[0][0] ][ sub ] = {}
        

print "--------------"
print "Reading Labels"


# Students ( Students )
# Base keys off of folder names
students = {}

hw_dirs = './hw1'
for dirs in os.listdir(hw_dirs):

    students[dirs] = {}


for student in students.keys():

    print student

    students[student]["homework"] = homework

    for subdir, dirs, files in os.walk( os.path.join(hw_dirs, student) ):

        for file in files:

            students[student][file] = os.path.join(subdir, file)

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

                        students[student]["homework"][prob[0]]["all"]["label"].append( file_rect )

# Print Data Structure
pprint.pprint(students)



def keypress(event):

    if (event.key).isdigit():
        students[student]["homework"][problem]["all"]["grade"] = int(event.key)



# Show all specific problems

problem = "2.1"

for student in students.keys():

    label_array = students[student]["homework"][problem]["all"]["label"]



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

        axarr[0].imshow(img_rect)


        axarr[1].set_title(student+" "+problem)
        axarr[1].imshow(img[y1:y2,x1:x2])


        #x1, y1, x2, y2 = labels["2.21c"]

        #axarr[0,1].set_title("2.21c")
        #axarr[0,1].imshow(img[y1:y2,x1:x2])


        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())


        plt.draw()


        cid = f.canvas.mpl_connect('key_press_event', keypress)

        plt.waitforbuttonpress(0)

        plt.close(f)



        pprint.pprint(students)










input("HERE")

# Labels ( Regions )
labels = {}

# Read Text Files
file_name = "hw1-page-001.txt"
with open(file_name,"r") as file:
    print file_name
    for line in file:
        print line,        
        entry = line.split()
        labels[ entry[0] ] = ( int(entry[4]), int(entry[5]), int(entry[6]), int(entry[7]) )

print "------"
print "Labels"

# Populate Labels in Dictionary
for key in labels:

    prob = filter(None, re.split('(.*\d)', key))

    print prob

    if len(prob)>1:
        homework[ prob[0] ][ prob[1] ][ 'label' ] = labels[key]
    else:
        homework[ prob[0] ][ 'all'][ 'label' ] = labels[key]


print "-------------------"
print "Homework Dictionary"
print homework




# Image
img = cv2.imread("hw1-page-001.jpg")


# Iterate through Assignment
for sp in s_subproblems:

    problem = sp[0][0]

    for subproblem in sp[1]:

        x1, y1, x2, y2 = homework[problem][subproblem]["label"]


        f, axarr = plt.subplots(2,2)

        img_rect = img.copy()
        img_rect = cv2.rectangle(img_rect, (x1,y1),(x2,y2),(255,0,0),2)

        # OCR (Optical Character Recognition)
        #bw_img = cv2.cvtColor(img_rect, cv2.COLOR_BGR2GRAY)
        #(thresh, bw_img) = cv2.threshold(bw_img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        #img_test = Image.fromarray(bw_img)
        #txt = pytesseract.image_to_string(img_test)
        #print txt


        axarr[0,0].imshow(img)
        axarr[1,1].imshow(img_rect)

        #x1, y1, x2, y2 = labels["2.21c"]

        #axarr[0,1].set_title("2.21c")
        #axarr[0,1].imshow(img[y1:y2,x1:x2])



        axarr[1,0].set_title(problem+subproblem)
        axarr[1,0].imshow(img[y1:y2,x1:x2])


        axarr[0,0].tick_params('both',colors='c')

        plt.show()


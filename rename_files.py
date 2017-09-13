import os
import re

hw_source = "hw2"
hw_destination = "hw2_names"

# Students ( Students )
# Base keys off of folder names
students = {}

for dirs in os.listdir(hw_source):

    students[dirs] = {}


for student in students.keys():

    print student



    for subdir, dirs, files in os.walk( os.path.join(hw_source, student) ):


        print subdir, dirs, files

        for file in files:

            # Text File
            if file.endswith(".pdf") or file.endswith(".PDF"):

                print subdir,

                # Convert Subdirectory to Linux Parsable
                sub = re.sub(r'([(), ])', r'\\\1', subdir)
                f = re.sub(r'([(), ])', r'\\\1', file)

                stud = re.sub(r'([(), ])', r'\\\1', student)

                print sub



                command = "cp "+os.path.join(sub, f)+" "+hw_destination+"/"+stud+".pdf"

                print command

                os.system(command)


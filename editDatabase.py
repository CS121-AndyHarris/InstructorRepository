import os
import json
from updateDatabase import encryptDatabase as encrypt
from setup import decryptDatabase as decrypt
from setup import writeData
import subprocess

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("Missing dependency. Please run command pip install dotenv")

if __name__ == "__main__":
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
    COURSE_ID = os.getenv("COURSE_ID")
    BASE_URL = os.getenv("BASE_URL")
    CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")


def menu():
    """
    Prints the menu and returns the response
    """
    print()
    print("0) Quit")
    print("1) Edit Students")
    print("2) Edit Assignments")
    userInput = input("What would you like to do?: ")

    return userInput

def updateStudents(database):
    """
    Will be used to update the student's database
    """
    print()
    print("1) Edit Current Student Info")
    print("2) Add student")
    userInput = input("What would you like to do?: ")

    if userInput == "1":
    
        for number in range(len(database)):
            print(f"{number}) {database[number]}")
        
        userInput = input("Please enter number to edit: ")

        if userInput.isdigit():
            if int(userInput) in range(len(database)):
                currentlyEditing = database[int(userInput)]
                print("Click enter to not change field!")

                for field in currentlyEditing.keys():
                    userInput = input(f"{field} (Currently: {currentlyEditing[field]}): ")
                    
                    if userInput != "":
                        currentlyEditing[field] = userInput
                
                print("Succesfully updated!")
                print(json.dumps(currentlyEditing,indent=2))

            else:
                print(f"Please enter number 0-{len(database)-1}")
        
        else:
            print("Please enter a valid number!")
    
    elif userInput == "2":
        fields = ("name","id","github")
        newStudent = {}

        for item in fields:
            userInput = input(f"Please enter new student {item}: ")
            newStudent[item] = userInput
        
        database.append(newStudent)
        print("Succesfully updated!")
        print(json.dumps(newStudent,indent=2))

    else:
        print("Please enter valid option 1 or 2!")


def updateAssignments(database):
    """
    Will be used to update the assignments database
    """
    print("Current Assignments: ")
    print(json.dumps(database,indent=2))
    newAssignment= {}
    assignmentName = input("Enter Assignment Name: ")
    assignmentId = input("Enter Assignment ID: ")
    newAssignment[assignmentName] = assignmentId
    database.append(newAssignment)
    print("Succesfully updated!")
    print(json.dumps(newAssignment,indent=2))

def updateDatabase():
    """
    This will call the command line command to commit to 
    git and allow you to update your databse locally
    """
    try:
        subprocess.run(["git","add","."])
        subprocess.run(["git", "commit", "-m", "Updated Database via command line tool run locally"], check=True)
        subprocess.run(["git","push"])
    except:
        print("Unable to update database!")


def main():
    """
    This will keep track of menu response and run approriate functinos
    """

    keepGoing = True
    decryptedStudents = decrypt("canvasData/students.json",ENCRYPTION_KEY)
    decrytpedAssignments = decrypt("canvasData/assignments.json",ENCRYPTION_KEY)

    while keepGoing:
        userInput = menu()

        if userInput == "0":
            keepGoing = False
        elif userInput == "1":
            updateStudents(decryptedStudents)
        elif userInput == "2":
            updateAssignments(decrytpedAssignments)
        else:
            print("Please enter 0,1, or 2")
        
    writeData(encrypt(decryptedStudents,ENCRYPTION_KEY),"canvasData/students.json")
    writeData(encrypt(decrytpedAssignments,ENCRYPTION_KEY),"canvasData/assignments.json")
    updateDatabase()

if __name__ == "__main__":
    main()
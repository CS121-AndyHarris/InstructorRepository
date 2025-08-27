import os 
from setup import decryptDatabase as decrypt
import json
import base64
import requests

PAYLOAD = os.getenv("CLIENT_PAYLOAD")
PAYLOAD = json.loads(base64.b64decode(PAYLOAD).decode("utf-8"))
RESULTS = PAYLOAD["testResults"]
MAX_SCORE = PAYLOAD["points"]
ASSIGNMENT_NAME = PAYLOAD["assignmentName"]
GITHUB_USER = PAYLOAD["triggeredBy"]
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
COURSE_ID = os.getenv("COURSE_ID")
BASE_URL = os.getenv("BASE_URL")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
COMMENT = PAYLOAD["comment"]

def calculateScore():
    """
    Calculates and returns the score based off
    the test results. 
    """
    totalScore = 0

    for i in range(len(RESULTS)):

        if RESULTS[i] == "pass":
            totalScore += int(MAX_SCORE[i])

    return totalScore


def postScore(score):
    """
    Takes in a score as a parameter. Also gets the payload to
    post a score in canvas. 
    """
    decryptedStudents = decrypt("canvasData/students.json")
    decryptedAssignments = decrypt("canvasData/assignments.json")
    studentObject = findStudentInDatabase(GITHUB_USER,decryptedStudents)
    assignmentID = findAssignmentInDatabase(ASSIGNMENT_NAME,decryptedAssignments)

    if studentObject != None:

        if assignmentID != None:

            url = f"{BASE_URL}/api/v1/courses/{COURSE_ID}/assignments/{assignmentID}/submissions/{studentObject['id']}"
            header = {
                "Authorization": f"Bearer {CANVAS_TOKEN}"
            }
            data = {
                "submission": {
                    "posted_grade": score
                },
                "comment": {
                    "text_comment": COMMENT
                }
            }


            response = requests.put(url,headers=header,json=data)
            print(f"Response Code: {response.status_code}")

        else:
            print("Assignment grade was not able to be posted! Couldn't find Assignment!")

    else:
        print("Assignment grade was not able to be posted! Couldn't find student!")



def findStudentInDatabase(itemToFind,database):
    """
    Takes in string and database and searches the database. 
    Returns the dictionary object if it can find it and null if not
    """
    output = None

    for item in database:
        if item["github"] == itemToFind:
            output = item
    
    return output

def findAssignmentInDatabase(name,database):
    """
    Returns the assignment ID if the assignment can be found
    """
    output = None

    for item in database:

        if name in item:
            output = item[name]
    
    return output



def main():
    """
    Calculates the total score and then calls
    postScore() to post the grade to canvas
    """
    totalScore = calculateScore()
    postScore(totalScore)

if __name__ == "__main__":
    main()
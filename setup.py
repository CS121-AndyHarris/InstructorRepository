import requests
import json
import os
from cryptography.fernet import Fernet
import base64
import Exceptions

if __name__ == "__main__":
    COURSE_ID = os.getenv("COURSE_ID")
    BASE_URL = os.getenv("BASE_URL")
    CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
    PAT_GIT = os.getenv("PAT_GIT")
    REPO_NAME = os.getenv("REPO_NAME")


def getStudentData():
    """
    This function creates a request and returns the student's data.
    """
    url = f"{BASE_URL}/api/v1/courses/{COURSE_ID}/enrollments?type[]=StudentEnrollment"

    header = {
    "Authorization": f"Bearer {CANVAS_TOKEN}"
    }

    return requests.get(url,headers=header).json()


def parseStudentData(studentData):
    """
    This function takes in json object that contains the student data.
    It then parses the data and returns a dictionary in the format that
    we need it in.
    """
    encrypter = Fernet(ENCRYPTION_KEY)

    output = []

    for item in studentData:
        studentData = {}

        encryptedName = encrypter.encrypt(item["user"]["name"].encode()).decode()
        encryptedID = encrypter.encrypt(str(item["user"]["id"]).encode()).decode()

        output.append({
            encrypter.encrypt("name".encode()).decode():encryptedName,
            encrypter.encrypt("id".encode()).decode():encryptedID,
            encrypter.encrypt("github".encode()).decode():encrypter.encrypt("".encode()).decode()})
    
    return output


def getAssignmentData():
    """
    This function creates a request and returns student data
    """

    url = f"{BASE_URL}/api/v1/courses/{COURSE_ID}/assignments"
    
    header = {
    "Authorization": f"Bearer {CANVAS_TOKEN}"
    }

    response = requests.get(url,headers=header)
    Exceptions.validateStatusCode(response.status_code,"Canvas")

    return response.json()


def parseAssignmentData(assignmentData):
    """
    This function takes in json object that contains the assignment data.
    It then parses the data and returns a dictionary in the format that
    we need it in.
    """
    encrypter = Fernet(ENCRYPTION_KEY)

    output = []

    for item in assignmentData:
        assignmentData = {}

        encryptedAssignmentName = encrypter.encrypt(item["name"].encode()).decode()
        encryptedID = encrypter.encrypt(str(item["id"]).encode()).decode()
        assignmentData[encryptedAssignmentName] = encryptedID

        output.append(assignmentData)
    
    return output


def writeData(data,filePath):
    """
    This method takes in the student data and writes it
    to the correct file for storing.
    """

    with open(filePath,"w") as file:
        json.dump(data,file,indent=2)


def decryptDatabase(filePath,encrytpionKey):
    """
    This method will decrypt the database. It
    is given a file path then it will load the 
    file and return the decrypted one.
    """
    output = []
    decrypter = Fernet(encrytpionKey)

    with open(filePath, "r") as file:
        encryptedDatabase = json.load(file)
    
    for object in encryptedDatabase:
        data = {}
        for key,value in object.items():
            decryptedKey = decrypter.decrypt(key.encode()).decode()
            decryptedValue = decrypter.decrypt(value.encode()).decode()
            data[decryptedKey] = decryptedValue

        output.append(data)
    
    return output


def validateGitHubName(repositoryName):
    """
    This method validates a GitHub repository name. 
    If the name is not correct, it will return a corrected name.
    """
    invalidValues = [" ", "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "=", "+", "{", "}", "[", "]", ":", ";", '"', "'", "<", ">", ",", "?", "/", "\\", "|", "\n", "\r", "--", "-", "master", "main", "gh-pages", "support", "github", "help", "admin"]
    
    correctedName = repositoryName

    #Gets rid of spaces and replaces with dashes
    correctedName = correctedName.replace(" ", "-")


    cleanedName = []
    for char in correctedName:

        if char not in invalidValues:
            cleanedName.append(char)
        else:
            cleanedName.append("")
    correctedName = "".join(cleanedName)
    
    #Gets rid of leading dashes
    correctedName = correctedName.strip('-')
    
    #Fixes if there is double dashes
    while "--" in correctedName:
        correctedName = correctedName.replace("--", "-")
    
    if correctedName in invalidValues:
        correctedName = f"{correctedName}-repo"
    
    return correctedName


def createRepositories():
    """
    Decrypts that assignment database. Makes a repository
    for every key inside of the database. Uses GitHub API
    to make this happen
    """
    decrytpedAssignments = decryptDatabase("canvasData/assignments.json",ENCRYPTION_KEY)
    orgName = REPO_NAME.split("/")[0]
    url = f"https://api.github.com/orgs/{orgName}/repos"


    for object in decrytpedAssignments:

        for assignment in object.keys():

            fixedName = validateGitHubName(assignment)
            repositoryName = f"{fixedName}-template"

            payload = {
                "name": repositoryName,
                "description": f"Template repository for {fixedName}",
                "private": True,
                "auto_init": True,  
                "is_template":True
            }

            headers = {
                "Authorization": f"token {PAT_GIT}",
                "Accept": "application/vnd.github+json"
            }

            response = requests.post(url,headers=headers,json=payload)
            
            if Exceptions.validateStatusCode(response.status_code,"GitHub"):
                addWorkFlowFile(orgName,repositoryName)
                addRepositoryVariable(assignment,orgName,repositoryName)


def addWorkFlowFile(orgName,repositoryName):
    """
    Takes in a name of a repository. It will then add the
    workflow that update the workflow that is created by 
    GitHub once the instructor has created tests using the
    GitHub web interface. 
    """
    url = f"https://api.github.com/repos/{orgName}/{repositoryName}/contents/.github/workflows/addAutoGrade.yml"

    with open("utils/addAutoGrade.yml","rb") as file:
        content = base64.b64encode(file.read()).decode("utf-8")

    payload = {
        "message": "Added addAutoGrade workflow",
        "content": content,
        "branch": "main"
    }

    headers = {
        "Authorization": f"token {PAT_GIT}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.put(url,headers=headers,json=payload)

    if Exceptions.validateStatusCode(response.status_code,"GitHub"):
        url = f"https://api.github.com/repos/{orgName}/{repositoryName}/contents/autoGrading/addAutoGrade.py"

        with open("addAutoGrade.py","rb") as file:
            content = base64.b64encode(file.read()).decode("utf-8")

        response = requests.put(url,headers=headers,json=payload)

        Exceptions.validateStatusCode(response.status_code,"GitHub")


def addRepositoryVariable(orgName,repositoryName,assignmentName):
    """
    Takes in an assignment name and adds it 
    as a repository variable that the autograding
    script can access it. 
    """

    url = f"https://api.github.com/repos/{orgName}/{repositoryName}/actions/variables/ASSIGNMENT_NAME"

    payload = {
        "name":"ASSIGNMENT_NAME",
        "value":assignmentName
    }

    headers = {
        "Authorization": f"token {PAT_GIT}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.put(url,headers=headers,json=payload)

    Exceptions.validateStatusCode(response.status_code,"Github")


def main():
    """
    Grabs the student assignment data and parses it returning 
    it in a structure we will need to use then
    writes it to a file. It will also create template repositories
    for every assignment. 
    """

    studentData = getStudentData()
    parsedStudentData = parseStudentData(studentData)
    writeData(parsedStudentData,"canvasData/students.json")

    assignmentData = getAssignmentData()
    parsedAssignmentData = parseAssignmentData(assignmentData)
    writeData(parsedAssignmentData,"canvasData/assignments.json")

    createRepositories()


if __name__ == "__main__":
    main()

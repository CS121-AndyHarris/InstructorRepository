import textwrap 
import os

REPO_NAME = os.getenv("REPO_NAME")
ASSIGNMENT_NAME = os.getenv("ASSIGNMENT_NAME")

def updateYML():
    """
    This function will update the yml file used
    for autograding
    """

    testResults = []
    points = []

    with open("classroom.yml","r") as file:
        lines = file.readlines()
        length = len(lines)
        i = 0

        print(lines)
        
        while i < length:

            if "- name" in lines[i]:
                
                if "Checkout code" not in lines[i] and "Autograding Reporter" not in lines[i] and "Calculate and post grades" not in lines[i]:

                    i += 1
                    stepName = lines[i].split(":")[1].strip()
                    testResults.append('"${{' + f" steps.{stepName}.result " + '}}"')

                    i += 7
                    points.append(lines[i].split(":")[1].strip())
            
            i += 1

    autoGradeStep = textwrap.indent(f"""- name: Calculate and post grades
  run: |
    curl -X POST -H "Accept: application/vnd.github+json" \\
      -H "Authorization: Bearer ${{{{ secrets.PAT_GIT }}}}" https://api.github.com/repos/{REPO_NAME}/dispatches \\
      -d '{{"event_type":"calc-and-post-grades","client_payload":{{"testResults":[{','.join(testResults)}],"points":[{','.join(points)}],"comment":"","assignmentName":{ASSIGNMENT_NAME},"triggeredBy":"${{{{ github.actor }}}}"}}}}'
""", "      ")    


    autoGradeLineNum = containsAutoGrade(lines)
    if(autoGradeLineNum != -1):
        
        lines = lines[:autoGradeLineNum]
        lines.append(autoGradeStep)

        with open("classroom.yml.yml","w") as file:
            file.write(''.join(lines))
    
    else:

        with open("classroom.yml","a") as file:
            file.write("\n")
            file.write(autoGradeStep)


def containsAutoGrade(lines):
    """
    Checks if the document contains the appropriate
    autograde step. If it does will will override file
    instead of appending 
    """
    output = -1
    length = len(lines)

    for lineNumber in range(length):
        if "- name: Calculate and post grades" in lines[lineNumber]:
            output = lineNumber
    
    return output


def main():
    """
    Parses the document and adds appropriate step for autograding
    """
    updateYML()


if __name__ == "__main__":
    main()

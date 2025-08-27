# InstructorRepository
Welcome! Clone this repository and read this document to help you integrate GitHub classroom with canvas!

## Setup Repository
Below is an explanation on how to setup your repository. If you would highly recommend watching the video below for a more indepth explanation and to visually see how to set everything up:

![Thumbnail](https://github.com/user-attachments/assets/18fe0040-3983-4145-a821-8fbccb3642ac)

The first part of this process is to setup your repository with correct access keys. First go to GitHub secrets then Actions and add the following:

Instructor Repository Secrets:
```
CANVAS_TOKEN: Your personal access token
BASE_URL: Go to canvas and copy the url when you first enter the homescreen
COURSE_ID: When you click on your specific class it will be the numbers after courses
ENCRYPTION_KEY: Run generateEncryptionKey.py locally and copy that key into secrets
```

Organization Repository Secrets: 

```
PAT_GIT: GitHub personal access token to give authentication to automatically create repositories. Make sure that you have admin and repo permissions. This should be at hte level of the organization so all assignments can access it. 
```

I also recommend creating a finle named .env that you can keep track of your keys as well as use my command line tool I've developed.Make sure hte file name .env and that it's in the outer root directory not nested inside any folders. If the name is not .env it will not work! 

Once you have these tokens in place click the "Actions" tab at the tob of the repository. Then go ahead and click setup in the left sidebar and run workflow. This will automatically create a databse containing the student info, and assignment info both encrypted. We will need this information to post grades to canvas. It will also create template repositories that will be used to create assignments. Now that we have this there is one more crucial step in the setup. The databse needs to be able to match the GitHub username with the student info. Unfourtantly, there isn't a simple way to do this. You can either collect that information and update it manually or you can do it a much easier why by asking students to fill out a form and adding a little bit of logic to your Google spreadsheet to streamline this process. This repository comes built in with the capability to do this. First you should create a google form that asks for the person's first and last name as shown on cavnas, and asking them for the GitHub username. Then you will add an App Script to your google form with a trigger on submission(Watch setup video for help).

Copy and paste this code to store an api key(only have to do this once):
```
function saveApiKey() {
  const apiKey = 'your-api-key-here';  // Replace this with your actual API key
  PropertiesService.getScriptProperties().setProperty('API_KEY', apiKey);
}
```

Then run put this code in there and set a trigger so it will automatically send a request:

```
function onFormSubmit(e) {
  const responses = e.response.getItemResponses();
  const scriptProperties = PropertiesService.getScriptProperties();
  const GITHUB_TOKEN = scriptProperties.getProperty('GITHUB_KEY');
  const ORG_NAME = 'YOUR ORG NAME';
  const REPO_NAME = 'YOUR INSTRUCTOR REPOSITORY NAME';
  
  // Define the URL for the repository_dispatch event
  const URL = `https://api.github.com/repos/${ORG_NAME}/${REPO_NAME}/dispatches`;

  const payload = {
    event_type: "Update Database",
    client_payload: {
      name: `${responses[0].getResponse()} ${responses[1].getResponse()}`,
      github: responses[2].getResponse()
    }
  };

  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${GITHUB_TOKEN}`
    },
    payload: JSON.stringify(payload)
  };

  try {
    const response = UrlFetchApp.fetch(URL, options);
    Logger.log(response.getContentText());  // Log the response for debugging
  } catch (error) {
    Logger.log('Error triggering GitHub Action: ' + error.message);
  }
}
```

Keep in mind that this code only works if the form setup is done with the first question asking for first name, second question asking for last name, third question asking for GitHub username. Once you've done that everything should be good to go! 



## Assignment setup
When creating an assigment it is best to do it from a template. This allows us to change the .yml file generated when creating tests. This will be crucial so we can implement autograding. Check out this example file that will be generated after you add tests. 

```
name: Autograding Tests
'on':
- push
- repository_dispatch
permissions:
  checks: write
  actions: read
  contents: read
jobs:
  run-autograding-tests:
    runs-on: ubuntu-latest
    if: github.actor != 'github-classroom[bot]'
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Includes Documentation
      id: includes-documentation
      uses: classroom-resources/autograding-command-grader@v1
      with:
        test-name: Includes Documentation
        setup-command: ''
        command: test -f README.md
        timeout: 10
        max-score: 50
    - name: Compilies Correctly
      id: compilies-correctly
      uses: classroom-resources/autograding-command-grader@v1
      with:
        test-name: Compilies Correctly
        setup-command: cd tests
        command: make
        timeout: 10
        max-score: 20
    - name: Includes makefile
      id: includes-makefile
      uses: classroom-resources/autograding-command-grader@v1
      with:
        test-name: Includes makefile
        setup-command: ''
        command: test -f makefile
        timeout: 10
        max-score: 10
    - name: Includes horse.h
      id: includes-horse-h
      uses: classroom-resources/autograding-command-grader@v1
      with:
        test-name: Includes horse.h
        setup-command: ''
        command: test -f horse.h
        timeout: 10
        max-score: 3
    - name: Includes horse.cpp
      id: includes-horse-cpp
      uses: classroom-resources/autograding-command-grader@v1
      with:
        test-name: Includes horse.cpp
        setup-command: ''
        command: test -f horse.cpp
        timeout: 10
        max-score: 3
    - name: Includes race.h
      id: includes-race-h
      uses: classroom-resources/autograding-command-grader@v1
      with:
        test-name: Includes race.h
        setup-command: ''
        command: test -f race.cpp
        timeout: 10
        max-score: 3
    - name: Includes main.cpp
      id: includes-main-cpp
      uses: classroom-resources/autograding-command-grader@v1
      with:
        test-name: Includes main.cpp
        setup-command: ''
        command: test -f main.cpp
        timeout: 10
        max-score: 3
    - name: Autograding Reporter
      uses: classroom-resources/autograding-grading-reporter@v1
      env:
        INCLUDES-DOCUMENTATION_RESULTS: "${{steps.includes-documentation.outputs.result}}"
        COMPILIES-CORRECTLY_RESULTS: "${{steps.compilies-correctly.outputs.result}}"
        INCLUDES-MAKEFILE_RESULTS: "${{steps.includes-makefile.outputs.result}}"
        INCLUDES-HORSE-H_RESULTS: "${{steps.includes-horse-h.outputs.result}}"
        INCLUDES-HORSE-CPP_RESULTS: "${{steps.includes-horse-cpp.outputs.result}}"
        INCLUDES-RACE-H_RESULTS: "${{steps.includes-race-h.outputs.result}}"
        INCLUDES-MAIN-CPP_RESULTS: "${{steps.includes-main-cpp.outputs.result}}"
      with:
        runners: includes-documentation,compilies-correctly,includes-makefile,includes-horse-h,includes-horse-cpp,includes-race-h,includes-main-cpp

```

If you look we have the autograder report. Unfourtantly to calculate the grade that we want to be sent it has to be done progomatically. To set this up to be run you will just need to add this to your workflow: 

```
name: Calculate and post grades
run: |
  curl -X POST -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${{ secrets.PAT_GIT }}" \
    https://api.github.com/repos/OUR-ORG-Name/YOUR-Instructor-Repo-Name/dispatches \
    -d '{"event_type":"calc-and-post-grades","client_payload":{"testResults":[],"points":[],"comment":"",assignmentName:"AS SHOWN ON CANVAS","triggeredBy": ${{github.actor}}}}'
```

This will allow us to send a request to our private instructor repo. You will add the results of the test and the points for each of those tests into the approrpiate coloumns as so:

```
name: Calculate and post grades
run: |
  curl -X POST -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${{ secrets.PAT_GIT }}" \
    https://api.github.com/repos/YOUR-ORG-Name/YOUR-Instructor-Repo-Name/dispatches \
    -d '{
          "event_type":"calc-and-post-grades",
          "client_payload": {
            "testResults": [
              "${{ steps.includes-documentation.outputs.result }}",
              "${{ steps.compiles-correctly.outputs.result }}",
              "${{ steps.includes-makefile.outputs.result }}",
              "${{ steps.includes-horse-h.outputs.result }}",
              "${{ steps.includes-horse-cpp.outputs.result }}",
              "${{ steps.includes-race-h.outputs.result }}",
              "${{ steps.includes-main-cpp.outputs.result }}"
            ],
            "points": [50,20,10,3,3,3,3],
            "comment": "Preliminary grade done by autograder. Waiting for instructor review",
            "assignmentName": "(lab) Linux, vim, and git",
            "triggeredBy": ${{github.actor}
          }
        }'
```

It's important to make sure that you put the points in the same order for the test that corresponds. You can also specify a comment that will be posted with the grade.  Once you have added this into your assignment workflow this assignment will be able to be autograded with canvas.

## Using Command Line tool
This command line tool has to be run from the command line. In order to run this make sure you're in the directory and run the following commands:
```
python3 editDatabase.py
```
Additionally you can run this inside of any editor as well but running it from the command line is recommended. This will allow you to add assignments, add students, or update the current info of students! Lastly, make sure that you commit the changes so they will be updated on GitHub!

import os
import json
from setup import decryptDatabase as decrypt
from setup import writeData
from cryptography.fernet import Fernet
import base64

if __name__ == "__main__":
    PAYLOAD = os.getenv("CLIENT_PAYLOAD")
    PAYLOAD = json.loads(base64.b64decode(PAYLOAD).decode("utf-8"))
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()


def updateUser():
    """
    Searches for the correct person and adds their name to the database
    """

    nameToFind = PAYLOAD["name"]
    userNameToAdd = PAYLOAD["github"]

    database = decrypt("canvasData/students.json",ENCRYPTION_KEY)

    for object in database:

        if object["name"] == nameToFind:
            object["github"] = userNameToAdd
            print("Succesfully added")
    
    return database


def encryptDatabase(database,encryptionKey):
    """
    Takes in a database and rencrypts it and returns it
    """

    output = []
    encrypter = Fernet(encryptionKey)
    
    for object in database:
        data = {}
        for key,value in object.items():
            encryptedKey = encrypter.encrypt(key.encode()).decode()
            encryptedValue = encrypter.encrypt(value.encode()).decode()
            data[encryptedKey] = encryptedValue

        output.append(data)
    
    return output


def main():
    """
    Updates the user the rencrypts and writes file back
    """

    updatedDatabase = updateUser()
    print(updatedDatabase)
    rencryptedDatabse = encryptDatabase(updatedDatabase,ENCRYPTION_KEY)
    writeData(rencryptedDatabse,"canvasData/students.json")


if __name__ == "__main__":
    main()

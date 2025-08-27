"""
This file contains custom exceptions to
help with error handling. Also contains a
function that raises exception based off 
error code. 
"""

class AuthorizationError(Exception):

    def __init__(self,name,message="Authorization Error! Make sure you have configured your PAT correctly!"):
        self.message = f"{name} {message}"
        super().__init__(self.message)


class ResourceNotFoundError(Exception):

    def __init__(self,name,message="No Resource Found Error! Please make sure that what you're requesting exists"):
        self.message = f"{name} {message}"
        super().__init__(self.message)


def validateStatusCode(statusCode,apiName):
    """
    Takes in an error code and api name. It throws
    exception based off the error code. or nothing
    if the error code is successful! Also returns true
    """
    if statusCode == 201:
        print("Success!")
    elif statusCode == 401 or statusCode == 403:
        raise AuthorizationError(apiName)
    elif statusCode == 404:
        raise ResourceNotFoundError(apiName)
    

    return True

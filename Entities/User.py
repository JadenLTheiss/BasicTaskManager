class User:
    def __init__(self, username, password, userKey=None, groupKeys=None):
        self.username = username
        self.password = password
        self.userKey = userKey
        self.groupKeys = list()
        if groupKeys is not None: # if groupKeys is not null they are not a new user
            self.groupKeys.extend(groupKeys)
        else: # but if they are we add the default
            self.groupKeys.append('-NvTisEfuHnpjK0TpcAf')

    def toDict(self): # Allows Class to be JSON Serializable to send between files
        return {
            'username': self.username,
            'password': self.password,
            'groupKeys': self.groupKeys,
            'userKey': self.userKey,
        }
    
    def getUsername(self):
        return self.username
    
    def getPassword(self):
        return self.password
    
    def show(self):
        print("Username: " + str(self.username) + "\nPassword: " + str(self.password))
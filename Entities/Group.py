class Group:
    def __init__(self, name, description, managers, groupKey=None):
        self.name = name
        self.description = description
        self.managers = list()
        self.managers.extend(managers)
        self.groupKey = groupKey

    def toDict(self): # Allows Class to be JSON Serializable to send between files
        return {
            'name': self.name,
            'description': self.description,
            'managers': self.managers,
            'groupKey': self.groupKey,
        }
    
    def getName(self):
        return self.name
    
    def getDescription(self):
        return self.description
    
    def show(self):
        print("Group " + str(self.name))
        for manager in self.managers:
            print(str(manager))

class Task():
    def __init__(self, title, description, date, groupKey, status=None, assignedTo=None, updates=None, taskKey=None, hidden=None):
        self.title = title
        self.description = description
        self.date = date
        self.groupKey = groupKey
        if status is None:
            self.status = "Not yet started"
        else:
            self.status = status
        if assignedTo is None:
            self.assignedTo = "Unassigned"
        else:
            self.assignedTo = assignedTo
        self.updates = list()
        if updates is not None:
            self.updates.extend(updates)
        else:
            self.updates.append("First Update")
        self.taskKey = taskKey
        if hidden is None:
            self.hidden = False
        else:
            self.hidden = hidden

    def toDict(self): # Allows Class to be JSON Serializable to send between files
        return {
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'groupKey': self.groupKey,
            'status': self.status,
            'assignedTo': self.assignedTo,
            'updates': self.updates,
            'taskKey': self.taskKey,
            'hidden': self.hidden,
        }
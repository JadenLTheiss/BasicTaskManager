import firebase_admin
from firebase_admin import credentials, db
import Entities.User as User
import Entities.Task as Task
import hashlib

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://taskmanagerproject-54928-default-rtdb.firebaseio.com"
})

ref = db.reference('/')

def HashPassword(password):
    pwBytes = password.encode()
    pwHash = hashlib.sha3_256(pwBytes)
    return pwHash.hexdigest()

def CheckUser(givenUser):
    result = ref.child('users').get()

    for user_id, user_data in result.items():
        if givenUser['username'] == user_data.get('username') and givenUser['password'] == user_data.get('password'):
            return user_id, user_data
    return None, None
        
def GetUserByKey(givenKey):
    result = ref.child('users').get()
    for user_id, user_data in result.items():
        if user_id == givenKey:
            return user_data
    return None

def AddUser(user):
    result = ref.child('users').push(user)
    user['userKey'] = result.key
    ref.child('users').child(result.key).update(user)
    return result.key

def UpdateUser(user):
    ref.child('users').child(user['userKey']).update(user)

def DeleteUser(user):
    ref.child('users').child(user['userKey']).delete()

def GetUserByName(userName):
    result = ref.child('users').get()
    for user_id, user_data in result.items():
        if user_data['username'] == userName:
            return user_data
    return None

def GetUsersByGroupKey(givenKey):
    usersResult = ref.child('users').get()
    usersInGroup = list()
    for user_id, user_data in usersResult.items():
        for groupKey in user_data['groupKeys']:
            if groupKey == givenKey:
                usersInGroup.append(user_data)
    return usersInGroup

def CreateGroup(group):
    result = ref.child('groups').push(group)
    group['groupKey'] = result.key
    ref.child('groups').child(result.key).update(group)
    return result.key 

def GetGroupByKey(givenKey):
    result = ref.child('groups').get()
    for group_id, group_data in result.items():
        if group_id == givenKey:
            return group_data
    return None

def GetGroupByName(group_name):
    result = ref.child('groups').get()
    for group_id, group_data in result.items():
        if group_data.get('name') == group_name:
            return group_data
    return None

def GetGroupsByManagerKey(managerKey):
    result = ref.child('groups').get()
    groupKeys = list()
    for group_id, group_data in result.items():
        if managerKey in group_data['managers']:
            groupKeys.append(group_id)
    return groupKeys

def CreateTask(task):
    result = ref.child('tasks').push(task)
    task['taskKey'] = result.key
    ref.child('tasks').child(result.key).update(task)
    return result.key

def UpdateTask(task):
    ref.child('tasks').child(task['taskKey']).update(task)

def GetTaskByTaskKey(taskKey):
    result = ref.child('tasks').get()
    for task_id, task_data in result.items():
        if task_id == taskKey:
            return task_data
    return None 

def GetTaskByGroupKey(groupKey):
    result = ref.child('tasks').order_by_child('date').limit_to_first(20).get()
    tasks = list()
    for task_id, task_data in result.items():
        if task_data['groupKey'] == groupKey:
            tasks.append(task_data)
    return tasks

def GetTasksByAssignedTo(assignedTo):
    result = ref.child('tasks').get()
    taskKeys = list()
    for task_id, task_data in result.items():
        if assignedTo == task_data['assignedTo']:
            taskKeys.append(task_id)
    return taskKeys

#user = {
#    "firstName": "John",
#   "lastName": "Smith"
#}

#result = ref.child('users').push(user)

# updates = list()

# task = {
#     "title": "Default Task", 
#     "description": "Default Task for Default Group", 
#     "date": "2024-4-21", 
#     "groupKey": "-NvTisEfuHnpjK0TpcAf",
#     "status": "Not yet started",
#     "assignedTo": "Unassigned",
#     "updates": updates
# }

# result = ref.child('tasks').push(task)



from flask import Flask, render_template, request, session, redirect, url_for
import datetime
import firebaseConnection as FireBaseConnection
import Entities.User as User
import Entities.Group as Group
import Entities.Task as Task

app = Flask(__name__)
app.secret_key = 'COP4521TaskManagerKey'    # placeholder secret key

@app.route('/') #home directory - views all current groups and allows user to add new group
def home():
    groupList = list()
    user_id = session.get('user_id')
    if user_id:
        user_data = FireBaseConnection.GetUserByKey(user_id)
        user = User.User(user_data['username'], user_data['password'], user_data['userKey'], user_data['groupKeys'])
        currentUsername = user.getUsername()
        
        for groupKey in user.groupKeys:         #get data for groups
            group_data = FireBaseConnection.GetGroupByKey(groupKey)
            groupDic = dict()
            manList = list()
            for man_id in group_data['managers']:   #get groups managers
                manager = FireBaseConnection.GetUserByKey(man_id)
                if manager is not None:
                    managerUsername = manager['username']
                    manList.append(managerUsername)

            groupDic = {                        #set dic for printing
                'name': group_data['name'],
                'description': group_data['description'],
                'managers': ", ".join(manList),
            }
            groupList.append(groupDic)

    else:
        currentUsername = ''                    #for not signed in

    rows = groupList                            #rows set to group dic
    return render_template('home.html', currentUsername = currentUsername, rows = rows)

@app.route('/profile', methods=['POST', 'GET']) #profile directory - allows user to change password/username and view managed groups
def profile():
    user_id = session.get('user_id')
    if not user_id:                         #redirect if user is not signed in
        return redirect(url_for('login'))
    
    user_data = FireBaseConnection.GetUserByKey(user_id)
    user = User.User(user_data['username'], user_data['password'], user_data['userKey'], user_data['groupKeys'])

    managerOf_keys = FireBaseConnection.GetGroupsByManagerKey(user_id)
    managerOf_names = list()
    for key in managerOf_keys:              #get groups user is manager of for profile print
        groupName = FireBaseConnection.GetGroupByKey(key)['name']
        managerOf_names.append(groupName)

    currentUsername = user.getUsername()

    if request.method == 'POST':
        currentPassword = request.form['CurrentPassword']
        hashedCurrentPassword = FireBaseConnection.HashPassword(currentPassword)

        newUsername = request.form['NewUsername']
        newPassword = request.form['NewPassword']

        checkUsername = FireBaseConnection.GetUserByName(newUsername)
        if checkUsername is not None:               #check if new username already exists
            msg = "This username already exist, please select another!"
            return render_template('profile.html', currentUsername = currentUsername, managerOf = managerOf_names, msg=msg)

        if hashedCurrentPassword == user.getPassword():     #verify current password
            if newUsername and newUsername != currentUsername: #set new username if not current, else do nothing
                user.username = newUsername
                currentUsername = newUsername
            if newPassword:                                 #if new password, set new password
                hashedNewPassword = FireBaseConnection.HashPassword(newPassword)
                user.password = hashedNewPassword
            blob1 = user.toDict()
            FireBaseConnection.UpdateUser(blob1)            #update new username/password

    return render_template('profile.html', currentUsername = currentUsername, managerOf = managerOf_names)


@app.route('/login', methods=['POST', 'GET']) #login directory - allows users to login or travel to create account
def login():
    msg = ''
    flag = False
    user_id = session.get('user_id')        #gets current session, if any
    if user_id:
        currentUsername = FireBaseConnection.GetUserByKey(user_id)['username']
    else:
        currentUsername = ''

    if request.method == 'POST':
        userKey = "POST"
        try:
            username = request.form['Username']
            password = request.form['Password']
            hashedPassword = FireBaseConnection.HashPassword(password) #hashes password

            user = User.User(username, hashedPassword)
            blob = user.toDict()

            userKey, msg = FireBaseConnection.CheckUser(blob) #return key and msg

            session['user_id'] = userKey
            currentUsername = msg['username']

        except Exception as ex:
            msg = "Incorrect username or password."
        
        finally:
            if userKey:
                return redirect(url_for('home'))

    return render_template("login.html", msg = msg, currentUsername = currentUsername)

@app.route('/logout')   #clears session and logs out user, redirecting to login
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/deleteAccount/', methods=['POST', 'GET']) #allows user to delete their account if not a manager
def deleteAccount():
    flag = False
    user_id = session.get('user_id')
    if user_id and not FireBaseConnection.GetGroupsByManagerKey(user_id):   #if user is signed in and not a manger
        currentUsername = FireBaseConnection.GetUserByKey(user_id)['username']
        user = FireBaseConnection.GetUserByKey(user_id)
    else:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        try:
            answer = request.form['answer']
            if answer == "True":
                flag = True
                # unassigning tasks before deleting user
                taskKeys = FireBaseConnection.GetTasksByAssignedTo(user_id)
                for key in taskKeys:
                    task_data = FireBaseConnection.GetTaskByTaskKey(key)
                    task = Task.Task(task_data['title'], task_data['description'], task_data['date'], task_data['groupKey'], 
                    task_data['status'], task_data['assignedTo'], task_data['updates'], task_data['taskKey'], 
                    task_data['hidden'])
                    task.assignedTo = 'Unassigned'
                    blob = task.toDict()
                    FireBaseConnection.UpdateTask(blob)

        except Exception as ex:
            msg = str(ex)
            return redirect(url_for('home'))
        
        finally:
            if flag:
                FireBaseConnection.DeleteUser(user)
                return redirect(url_for('logout'))
            else:
                return redirect(url_for('profile'))
    # only if method != POST
    return render_template('deleteAccount.html', currentUsername = currentUsername)

@app.route('/createAccount', methods=['POST', 'GET']) #create account directory - allows user to create a new account
def createAccount():
    msg = ''
    if request.method == 'POST':
        try:
            username = request.form['Username']
            password = request.form['Password']
            confirmPassword = request.form['ConfirmPassword']

            checkUsername = FireBaseConnection.GetUserByName(username) #check if username already exists
            if checkUsername is not None:
                msg = "Username already created. Pick another one!"
                return render_template('createAccount.html', msg=msg)

            if password != confirmPassword:                           #check if passwords match
                msg = "Passwords do not match."
                return render_template('createAccount.html', msg=msg)

            hashedPassword = FireBaseConnection.HashPassword(password)

            user = User.User(username, hashedPassword) #create new user
            blob = user.toDict()

            userKey = FireBaseConnection.AddUser(blob) #add new user

            session['user_id'] = userKey
            msg = userKey

        except Exception as ex:
            msg = str(ex)
            return render_template('createAccount.html', msg=msg)

        finally:
            return redirect(url_for('home'))            #redirect home if user is create
    return render_template('createAccount.html', msg=msg)
        

@app.route('/createGroup', methods=['POST', 'GET']) #create group page - allows users to create new group
def createGroup():                                      #NOTE: users are automatically managers of any group they create
    msg = ''
    user_id = session.get('user_id')
    if user_id:                                         #Check if user exists and get username
        user_data = FireBaseConnection.GetUserByKey(user_id)
        user = User.User(user_data['username'], user_data['password'], user_data['userKey'], user_data['groupKeys'])
        currentUsername = user.getUsername()
    else:
        return redirect(url_for('login'))               #redirect to login if not signed in
    
    if request.method == 'POST':
        try:
            name = request.form['Name']
            description = request.form['Description']
            user_data = FireBaseConnection.GetUserByKey(user_id)

            if (FireBaseConnection.GetGroupByName(name) == None): #if group does not exist already
                managersList = list()
                managersList.append(user_id)                      #add user as default manager
                group = Group.Group(name, description, managersList)    #create group
                blob = group.toDict()
                groupKey = FireBaseConnection.CreateGroup(blob)   #add group to firebase
                user.groupKeys.append(groupKey)                   #add groupKey to user
                blob1 = user.toDict()
                result = FireBaseConnection.UpdateUser(blob1)     #update user with new keys
                msg = groupKey
            else:
                msg = "Group already exists, please select a different name!"
        except Exception as ex:
            msg = str(ex)
            return render_template("createGroup.html", msg=msg, currentUsername = currentUsername)

        finally:
            return redirect(url_for('home'))
    return render_template("createGroup.html", msg=msg, currentUsername = currentUsername)

@app.route('/addToGroup/<groupName>', methods=['POST', 'GET'])  #add to group page - allows managers to add users to group
def addToGroup(groupName):
    msg = ''  
    if request.method == 'POST':
        try:
            flag = False
            user_id = session.get('user_id')
            formName = request.form['Name']
            group_id = FireBaseConnection.GetGroupByName(groupName)['groupKey']
            managerList = FireBaseConnection.GetGroupByName(groupName)['managers']
            for manager in managerList:     #return if current user is a manager
                if user_id == manager:
                    managerID = user_id
                    break
                else:
                    managerID = None
                    msg = "You do not haver permission to add users!"
            if group_id and managerID:
                blob = FireBaseConnection.GetUserByName(formName)
                if blob != None:                    #check if user is already in a group
                    flag = False
                    for keys in blob['groupKeys']:
                        if keys == group_id:
                            flag = True
                    if flag == False:               #if user is not in a group, add them
                        user = User.User(blob['username'], blob['password'], blob['userKey'], blob['groupKeys'])
                        user.groupKeys.append(group_id)
                        print(user.userKey)
                        blob1 = user.toDict()
                        print(blob1['userKey'])
                        result = FireBaseConnection.UpdateUser(blob1)
                        msg = group_id
                    else:
                        msg = "This user is already in this group!"
                        return render_template("addToGroup.html", msg=msg, groupName = groupName)

                else:
                    msg = "User does not exist!"
                    return render_template("addToGroup.html", msg=msg, groupName = groupName)

        except Exception as ex:
            msg = str(ex)
            return render_template("addToGroup.html", msg=msg, groupName = groupName)
        
        finally:
            return redirect(url_for('groupView', groupName = groupName))
    return render_template("addToGroup.html", msg=msg, groupName = groupName)

@app.route('/removeFromGroup/<groupName>', methods=['POST', 'GET']) #remove from group page - allows managers to remove users from gorup
def removeFromGroup(groupName):
    msg = '' 
    user_id = session.get('user_id')
    group_id = FireBaseConnection.GetGroupByName(groupName)['groupKey']
    membersList = FireBaseConnection.GetUsersByGroupKey(group_id)
    memList = list()
    for member in membersList:                  #member list for managers
        userDic = dict()
        userDic = {
            'name': member['username'],
        }
        memList.append(userDic)
    rows = memList
    if request.method == 'POST':
        try:
            flag = False

            formName = request.form['Name']
            managerList = FireBaseConnection.GetGroupByName(groupName)['managers']
            for manager in managerList: #return if current user is a manager
                if user_id == manager:
                    managerID = user_id
                    break
                else:
                    managerID = None
            if group_id and managerID:
                blob = FireBaseConnection.GetUserByName(formName)
                isManager = False
                for manager in managerList:         #check if user to be removed is a manager
                    if blob['userKey'] == manager:
                        isManager = True
                if blob != None and isManager == False: #if user is not a manager, set flag for removal
                    flag = False
                    for keys in blob['groupKeys']:
                        if keys == group_id:
                            flag = True
                    if flag == True:
                        user = User.User(blob['username'], blob['password'], blob['userKey'], blob['groupKeys'])
                        user.groupKeys.remove(group_id)
                        blob1 = user.toDict()
                        result = FireBaseConnection.UpdateUser(blob1)       #remove user from group
                        msg = group_id
                    else:
                        msg = "This user is NOT in this group!"
                        return render_template("removeFromGroup.html", msg=msg, groupName = groupName)

                else:
                    msg = "User does not exist/is a manager!"
                    return render_template("removeFromGroup.html", msg=msg, groupName = groupName)

        except Exception as ex:
            msg = str(ex)
            return render_template("removeFromGroup.html", msg=msg, groupName = groupName)
        
        finally:
            return redirect(url_for('groupView', groupName = groupName))
    return render_template("removeFromGroup.html", msg=msg, groupName = groupName, rows = rows)
        
@app.route('/createTask/<groupName>', methods=['POST', 'GET']) #create task page - allows managers to create tasks
def createTask(groupName):
    msg = '' 
    if request.method == 'POST':
        try:
            name = request.form['Name']
            description = request.form['Description']
            date = request.form['Date']
            group_id = FireBaseConnection.GetGroupByName(groupName)['groupKey']

            task = Task.Task(name, description, date, group_id) #create new task
            blob = task.toDict()
            taskKey = FireBaseConnection.CreateTask(blob)       #add task to group

            msg = taskKey

        except Exception as ex:
            msg = str(ex)
            return render_template("createTask.html", msg=msg, groupName=groupName)

        finally:
            return redirect(url_for('groupView', groupName = groupName))
    return render_template("createTask.html", msg=msg, groupName=groupName)
    
@app.route('/groupView/<groupName>')    #group view page - allows users to view a group they are in
def groupView(groupName):
    user_id = session.get('user_id')
    group_id = FireBaseConnection.GetGroupByName(groupName)['groupKey']
    managerList = FireBaseConnection.GetGroupByName(groupName)['managers']
    for manager in managerList:         #check if current user is a manager
        if user_id == manager:
            managerID = user_id
            break
        else:
            managerID = None
    taskList = FireBaseConnection.GetTaskByGroupKey(group_id)   #get group task list
    rows = list()
    
    if managerID == None:                   #if current user isn't a manager, see non hidden tasks
        tasksNonHidden = list()
        for task in taskList:
            if task['hidden'] is False:
                tasksNonHidden.append(task)
        taskList.clear()
        taskList.extend(tasksNonHidden)
        tasksNonHidden.clear()

    for task in taskList:                   #else, print all tasks
        taskDict = dict()
        if task['assignedTo'] == "Unassigned":
            username = "Unassigned"
        else:
            username = FireBaseConnection.GetUserByKey(task['assignedTo'])['username']
        taskDict = {
            'taskKey': task['taskKey'],
            'title': task['title'],
            'description': task['description'],
            'status': task['status'],
            'assignedTo': username,
            'date': task['date'],
        }
        rows.append(taskDict)

    return render_template('groupView.html', groupName = groupName, rows = rows, managerID = managerID)

@app.route('/updateTask/<taskKey>', methods=['POST', 'GET']) #update task page - allows users to update a task
def updateTask(taskKey):
    msg = ""
    user_id = session.get('user_id')
    task_data = FireBaseConnection.GetTaskByTaskKey(taskKey)
    group_data = FireBaseConnection.GetGroupByKey(task_data['groupKey'])
    blob = task_data
    manager = False

    if user_id == None or task_data == None:
        return redirect(url_for('home'))
    
    else:                                           #setting assigned data
        if task_data['assignedTo'] == 'Unassigned':
            assignedUser = 'Unassigned'
        else:
            assignedUser = FireBaseConnection.GetUserByKey(task_data['assignedTo'])['username']

        if user_id in group_data['managers']:       #check if user is a manager
            manager = True

        if request.method == 'POST':
            try:
                taskStatus = request.form['status']
                update = request.form['updates']

                if update != '':                    #if update is not blank
                    task = Task.Task(task_data['title'], task_data['description'], task_data['date'], task_data['groupKey'], 
                                    task_data['status'], task_data['assignedTo'], task_data['updates'], task_data['taskKey'], 
                                        task_data['hidden'])    #create task
                    task.status = taskStatus
                    task.updates.append(update)                 #add task update
                    if (taskStatus == 'Completed'):             #hide if completed
                        task.hidden = True
                    blob = task.toDict()
                    FireBaseConnection.UpdateTask(blob)         #update task

                else:
                    msg = "Please fill out the update log!"     #error message for blank update

            except Exception as ex:
                msg = str(ex)

            finally:
                return render_template("updateTask.html", msg=msg, taskData=blob, groupData=group_data, assignedUser=assignedUser, manager=manager)
    return render_template("updateTask.html", msg=msg, taskData=blob, groupData=group_data, assignedUser=assignedUser, manager=manager)

@app.route('/unassignTask/<taskKey>')   #unassign task - managers may unassign a user from a task
def unassignTask(taskKey):
    task_data = FireBaseConnection.GetTaskByTaskKey(taskKey)
    group_data = FireBaseConnection.GetGroupByKey(task_data['groupKey'])

    task = Task.Task(task_data['title'], task_data['description'], task_data['date'], task_data['groupKey'], 
                    task_data['status'], task_data['assignedTo'], task_data['updates'], task_data['taskKey'], 
                    task_data['hidden'])        #create new task based on previous task
    task.assignedTo = 'Unassigned'              #set status to unassigned
    blob = task.toDict()
    FireBaseConnection.UpdateTask(blob)         #update task
    return redirect(url_for('groupView', groupName=group_data['name']))

@app.route('/assignTask/<taskKey>', methods=['POST', 'GET'])    #assign task page - allows managers to assign task or users to accept task
def assignTask(taskKey):
    msg = ""
    user_id = session.get('user_id')
    task_data = FireBaseConnection.GetTaskByTaskKey(taskKey)
    group_data = FireBaseConnection.GetGroupByKey(task_data['groupKey'])
    membersList = FireBaseConnection.GetUsersByGroupKey(task_data['groupKey'])
    manager = False
    flag = False
    memList = list()
    for member in membersList:                  #member list for managers
        userDic = dict()
        userDic = {
            'name': member['username'],
        }
        memList.append(userDic)
    rows = memList

    if user_id == None or task_data == None:    #redirect home if user is not signed in
        return redirect(url_for('home'))
    
    else:
        if user_id in group_data['managers']:   #check if user is a manager
            manager = True

        if request.method == 'POST':
            try:
                if manager:                                                         #manager version
                    username = request.form['Name']
                    blobUser = FireBaseConnection.GetUserByName(username)
                    if blobUser and task_data['groupKey'] in blobUser['groupKeys']: #if user is apart of this group
                        task = Task.Task(task_data['title'], task_data['description'], task_data['date'], task_data['groupKey'], 
                                        task_data['status'], task_data['assignedTo'], task_data['updates'], task_data['taskKey'], 
                                            task_data['hidden'])                    #get task
                        task.assignedTo = blobUser['userKey']                       #change assigned to
                        blob = task.toDict()
                        FireBaseConnection.UpdateTask(blob)                         #update task
                        msg = username + " has been assigned to Task!"
                    else:
                        msg = "User could not be found in this group."
                        flag = True

                else:                                                               #member version
                    answer = request.form['answer']

                    if answer == "True":                                            #if user accepts task, get task
                        task = Task.Task(task_data['title'], task_data['description'], task_data['date'], task_data['groupKey'], 
                                        task_data['status'], task_data['assignedTo'], task_data['updates'], task_data['taskKey'], 
                                            task_data['hidden'])
                        task.assignedTo = user_id                                   #change assigned to current user
                        blob = task.toDict()
                        FireBaseConnection.UpdateTask(blob)                         #update task
                        msg = "You have been assigned to Task!"

            except Exception as ex:
                msg = str(ex)

            finally:
                if flag: # only if user not found in group
                    return render_template("assignTask.html", msg=msg, taskData=task_data, groupData=group_data, manager=manager)
                else:
                    return redirect(url_for('groupView', groupName=group_data['name']))
    # only if method != POST
    return render_template("assignTask.html", msg=msg, taskData=task_data, groupData=group_data, manager=manager, rows = rows)

if __name__ == '__main__':
    app.run(debug=True)
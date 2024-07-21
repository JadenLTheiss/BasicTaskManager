# COP4521_Project

# Group 25: Task Manager Application
This application was developed to solve the problem of managing a collection
of tasks as a group. It allows users to create groups and be added to existing
groups. The managers of a group can create tasks for the group, add or remove
users from the group, and assign users to tasks. Users can post updates to the
tasks in their group, including the task's current status and a message to log
the update.


## User Instructions
The application can be accessed by either following this link:
https://jadenltheiss.pythonanywhere.com/
or by cloning this repository, executing the command 'python app.py',
and following the link provided in the terminal, which accesses the frontend
of the application on your machine locally.

Once you've accessed the application's frontend, you must create an account
or log in to an existing account.

Once you're logged in, the home page will display a list of groups that you
are a member of. You can also create a new group in which you will be the manager.

From the home page, clicking on a group will take you to a page displaying that
group's tasks. You can click on a task to view its update logs and to add new
updates or change the task's status. If a task is unassigned, you can assign
yourself to that task. If you are the manager of the group, you can instead
assign the task to any user in the group. Managers can also create new tasks
as well as add or remove members of the group.

The profile page allows users to change their username or password and to
delete their account. You cannot delete your account if you are a manager of
a group.

A testing account that is a manager of multiple groups can be logged into
with username 'Jaden' and password '12345'.


## Libraries Used
- hashlib - Python library used to hash passwords.
- datetime - Python library used to access/manipulate dates and times.
- firebase_admin - Python library used to manage the Firebase database.
- flask - Python library used to implement the html web application frontend.


## Other Resources
- static/styles.css, which is used to style the header on every page, is taken
from https://www.w3schools.com/howto/howto_js_topnav.asp
- This application was deployed using https://www.pythonanywhere.com/, allowing
anyone with the link access to the web application.
- https://firebase.google.com/ was used to store our application's data (including users, groups, and
tasks) on the cloud, so the same database is accessed no matter which machine
is running the application.
- Firebase Documentation for Firebase Admin on Python
  - https://firebase.google.com/docs/reference/admin/python


## Extra Features
- Profile page: user can change username/password and delete account.
- Navbar: each page has a navigation bar at the top, allowing users to
easily access the home, profile, and login pages as well as logout.
- Deployment: the application can be accessed without downloading or
running the source code by following this link:
https://jadenltheiss.pythonanywhere.com/


Ilya Kogan:
- Began setup for task filtering based on priority/category
- Created a new table called tasks in DB
- Set up html pages/templates
- Set up firebase


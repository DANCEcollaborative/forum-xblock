# This project has been archived and is no longer being actively maintained. Fork at your own risk.

# forum-xblock

Django based forum application that will be integrated into an edX XBlock

# Quick Install

To quickly install a local instance of the current version of the forum Django application, follow the steps outlined below.

1. virtualenv <Name_of_virtual_env>
2. cd <Name_of_virtual_env>
3. source ./bin/activate # This activates the virtual environment
4. cd ../django-source/ # This takes you to the Django source folder
5. ./setup.py install
6. sudo pip install -r requirements.txt # Installs all the necessary requirements
6. cd ../django-app # Navigate to the django app folder
7. sudo pip install -r requirements.txt # Installs all requirements of the app inside the virtualenv
8. cd basic_project
9. ./manage.py syncdb
10. ./manage.py collectstatic
11. ./manage.py runserver

And you are off. Since the home page isn't configured yet. Navigate to http://127.0.0.1:8000/forum/

# The Technical Document

The technical document detailing the development of the XBlock and providing instructions for custom modifications can be found here. https://docs.google.com/document/d/1tzesucF4w6fDEYQRAjB7Qkj-KUxjaXiSa1BMc4ILc6Q/edit?usp=sharing

# Feature Walkthrough

This document provides a walkthrough of the features currently provided by the forum x-block. https://docs.google.com/document/d/171CftSVqSD9zAYlguj6MXzgvwVz9JvXw2npDjz_eVfE/edit?usp=sharing

# The Design Document

This document describes the overarching goals behind the conception, subsequent development and future directions of the forum-xblock. https://docs.google.com/document/d/1jd51EXsTxGbd8vDTFHLnzysnk4n7GDpKYlbbZpogrew/edit?usp=sharing

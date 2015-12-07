#from xblock.core import XBlock
#from xblock.fields import Scope, Integer, String
import settings as s
from datetime import date, datetime, timedelta
import mysql.connector as db_connector
import pkg_resources
import sys
        
user_id = ''
parent_comment_id = -1 #This should be set in case the user clicks 'reply to an existing comment'
thread_id = -1 #This should be fetched using the parent_comment_id to fetch it's thread_id
comment = ''
db = None #This is the DB connection. WE NEED TO ENSURE THIS IS CLOSED!

def resource_string( path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")

def get_error_msg():
    return(str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

def exec_query(query, prefix_msg = ""):
    cursor = db.cursor()
    try:
        cursor.execute(query)
    except:
        print(prefix_msg + " Error :" + get_error_msg()) # PROBABLY NEED TO REPLACE THIS WITH A LOGGING STATEMENT!
    else:
        db.commit()
    cursor.close()


def setup_db():
    global db
    config_file = open("db_settings.txt", 'r')
    config = dict()
    for line in config_file:
        (key, value) = line.strip(' \t\r\n').split(':', 1)
        if str(value).strip() == 'True':
            config[str(key).strip()] = True
        else:
            config[str(key).strip()] = str(value).strip()
    print(config)
    config_file.close()
    db = db_connector.connect(**config)
    """
    settings.py contains a dictionary of key value pairs that define the mysql user name + password, the host on
    which the mysql user has been configured, the name of the database to use (the user specified here must be
    granted access to it on the host specified) and whether warnings should raise exceptions (which will show up in
    lms logs.)
    """
    create_query = (resource_string( "./discussion_setup.sql"))
    exec_query( create_query, "Initial Table Create Query")
    test_query = ("INSERT INTO discussion_table (thread_id, user_id, comment, parent_id) VALUES (1, 11, 'Akash made this comment', 1)")
    exec_query( test_query, "Table Insert Query")


def format_row(row):
    #Need to add logic here to escape quotes etc.
    return str(row[0]), str(row[1]), row[2].decode("utf-8"), row[3].decode("utf-8"), str(row[4]), str(row[5])


def get_all_data(cursor):
    ret_val = 0
    try:
        #cursor.execute("set session group_concat_max_len = 4096;")#Prevents row truncation errors due to group concat
        #May have to increase this value based on size of a row
        #cursor.execute('''SELECT CONCAT("[", GROUP_CONCAT( CONCAT("{comment_id:",comment_id), CONCAT("comment:'",comment,"'}") ) , "]") AS JSON FROM discussion_table;''')
        #cursor.execute("set session group_concat_max_len = 4096;")#Prevents row truncation errors due to group concat
        #May have to increase this value based on size of a row
        #cursor.execute('''SELECT CONCAT("[", GROUP_CONCAT( CONCAT("{'",comment_id,"':"), CONCAT("{comment_id:",comment_id), CONCAT(",comment:'",comment,"'}}") ) , "]") AS JSON FROM discussion_table;''');
        cursor.execute("SELECT * FROM discussion_table")
    except:
        print(" Error in fetch") # PROBABLY NEED TO REPLACE THIS WITH A LOGGING STATEMENT!
        ret_val = 1
    if(ret_val == 0):
        return ret_val
    else:
        return None

def get_db():
    #ajax_comment = data.get('comment_id')
    """
    The ajax supplied comment may have ' (apostrophe/single quote) embedded in it. These must be escaped before
    being put into the SQL query (which itself relies on single quotes when inserting strings).
    """
    global db
    cursor = db.cursor()
    ret_val = get_all_data(cursor)
    template = '"{0}" : {{ "comment_id" : "{0}", "thread_id" : "{1}", "user_id" : "{2}", "comment" : "{3}", "parent_id" : "{4}", "creation_date" : "{5}" }},'
    if(ret_val != None):
        ret_data = "{"
        #for row in cursor:
        for (comment_id, thread_id, user_id, comment, parent_id, creation_data) in cursor:
            #Some fields are returned as byte arrays in python. These will have to be converted into strings using the decode function
            #row_formatted = format_row(row)
            ret_data += template.format(*row_formatted)
        ret_data = ret_data[:-1] + "}"
        print(ret_data)
        return {'update_status': "Success", 'ret_data': ret_data}
    else:
        return {'update_status': "Failure"}

setup_db()
get_db()

db.close()
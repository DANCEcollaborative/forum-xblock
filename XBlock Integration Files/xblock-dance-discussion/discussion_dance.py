from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
import settings
import logging
import sys
import mysql.connector as db_connector
import pkg_resources
from xblock.fragment import Fragment
import unicodedata
import urllib3
from student.models import user_by_anonymous_id


"""
TO DO:
db_settings.py IS NOT COPIED TO THE XBLOCK INSTALL DIRECTORY by pip. SOLVE THIS!!
    -Same goes for discussion_setup.sql and all static assets
    -Currently both these files need to be copied to /edx/app/edxapp/venvs/edxapp/local/lib/python2.7/site-packages/
Add exception handling for ALL database operations.
Replace console prints with logging statements
Separate out functions into their own modules (ex. All DB functions into a separate DB module)
Add more documentation when possible
#Conform to conventions (dance-discussion vs. discussion-dance for ids)
#CHECK DOUBLE QUOTES AND WILDCARD CHARACTER CASES which may be embedded in the user comment supplied via Ajax
Change the requirements file so that the mysql connector can be installed directly via pip using the requirements file

"""

class DiscussionDance(XBlock):

    """
    This XBlock creates a discussion thread that conforms to the requirements of DiscourseDB
    (see https://groups.google.com/forum/#!topic/dancecollab/R9UQ5DysfmQ), which is an initiative of the DANCE group at
    CMU (http://www.cs.cmu.edu/~dance/)
    """
    config_file_path = "/home/akashb/dev-stuff/XBlock/xblock-dance-discussion/xblock-dance-discussion/db_settings.txt"
    user_id = ''
    parent_comment_id = -1 #This should be set in case the user clicks 'reply to an existing comment'
    thread_id = -1 #This should be fetched using the parent_comment_id to fetch it's thread_id
    comment = ''
    db = None #This is the DB connection. WE NEED TO ENSURE THIS IS CLOSED!
    last_poll_id = -1
    xblock_login = ""

    def student_id(self):
        return self.xmodule_runtime.anonymous_student_id

    def resource_string(self, path):
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def remote_resource_string(self, url):
        return((urllib3.PoolManager()).request('GET', url).data)

    def get_error_msg(self):
        return(str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    def exec_query(self, query, prefix_msg = ""):
        cursor = DiscussionDance.db.cursor()
        ret_val = 0
        try:
            cursor.execute(query)
        except:
            print(prefix_msg + " Error :" + self.get_error_msg()) # PROBABLY NEED TO REPLACE THIS WITH A LOGGING STATEMENT!
            #Currently, this print statement will print out the workbench server console. This may not happen fo the EdX server
            #log = logging.getLogger(__name__)
            #log.info("Log message")
            ret_val = 1
        else:
            DiscussionDance.db.commit()
        cursor.close()
        return ret_val

    def get_all_data(self, cursor):
        ret_val = "Success"
        try:
            cursor.execute("SELECT * FROM discussion_table")
        except Exception as e:
            ret_val = " Error in fetch " + str(e) # PROBABLY NEED TO REPLACE THIS WITH A LOGGING STATEMENT!
        return ret_val

    def format_row(self, row):
        return (str(row[0]), str(row[1]), row[2].decode("utf-8"), row[3].decode("utf-8"), row[4].decode("utf-8"), str(row[5]), str(row[6]))

    @XBlock.json_handler
    def post_comment(self, data, suffix=''):
        #IT MIGHT BE BETTER TO MAINTAIN THE PRIMARY KEYS than rely on SQL auto increment since it is hard to get back the primary key.
        ajax_comment = data.get('comment')
        """
        The ajax supplied comment may have ' (apostrophe/single quote) embedded in it. These must be escaped before
        being put into the SQL query (which itself relies on single quotes when inserting strings).
        """
        safe_comment = ""
        self.xblock_login = self.student_id()
        current_user = user_by_anonymous_id(self.xblock_login)
        for char in ajax_comment:
            if (char != "'"):
                safe_comment += char
            else:
                safe_comment +="\\'" #Escaping the embedded single quote using a single \. We use \\ to escape it in python as well
                #ALSO CHECK DOUBLE QUOTES AND WILDCARD CHARACTER CASES!!!
        insert_query = ("INSERT INTO discussion_table (thread_id, user_id, user_name, comment, parent_id) VALUES (2, '" + self.xblock_login + "', '" + current_user.username + "', '" + safe_comment + "', -1)")
        ret_val = self.exec_query(insert_query,"Inserting user comment")
        if(ret_val == 0):
            return {'update_status': "Success"}
        else:
            return {'update_status': "Failure"}

    @XBlock.json_handler
    def post_reply(self, data, suffix=''):
        #IT MIGHT BE BETTER TO MAINTAIN THE PRIMARY KEYS than rely on SQL auto increment since it is hard to back the primary key.
        ajax_reply = data.get('comment')
        ajax_parent = data.get('parent_id')
        """
        The ajax supplied comment may have ' (apostrophe/single quote) embedded in it. These must be escaped before
        being put into the SQL query (which itself relies on single quotes when inserting strings).
        """
        safe_comment = ""
        self.xblock_login = self.student_id()
        current_user = user_by_anonymous_id(self.xblock_login)
        for char in ajax_reply:
            if (char != "'"):
                safe_comment += char
            else:
                safe_comment +="\\'" #Escaping the embedded single quote using a single \. We use \\ to escape it in python as well
                #ALSO CHECK DOUBLE QUOTES AND WILDCARD CHARACTER CASES!!!
        #insert_query = ("INSERT INTO discussion_table (thread_id, user_id, comment, parent_id) VALUES (2, '" + self.xblock_login + "', '" + safe_comment + "', " + ajax_parent + " )")
        insert_query = ("INSERT INTO discussion_table (thread_id, user_id, user_name, comment, parent_id) VALUES (2, '" + self.xblock_login + "', '" + current_user.username + "', '" + safe_comment + "', " + ajax_parent + " )")
        ret_val = self.exec_query(insert_query,"Inserting user comment")
        if(ret_val == 0):
            return {'update_status': "Success"}
        else:
            return {'update_status': "Failure"}

    @XBlock.json_handler
    def get_db(self, data, suffix=''):
        """
        The ajax supplied comment may have ' (apostrophe/single quote) embedded in it. These must be escaped before
        being put into the SQL query (which itself relies on single quotes when inserting strings).
        """
        cursor = DiscussionDance.db.cursor()
        ret_val = self.get_all_data(cursor)
        #template = '"{0}" : {{ "comment_id" : "{0}", "thread_id" : "{1}", "user_id" : "{2}", "comment" : "{3}", "parent_id" : "{4}", "creation_date" : "{5}" }},'
        template = '"{0}" : {{ "comment_id" : "{0}", "thread_id" : "{1}", "user_id" : "{2}", "user_name" : "{3}", "comment" : "{4}", "parent_id" : "{5}", "creation_date" : "{6}" }},'
        if(ret_val == "Success"):
            ret_data = "{"

            for row in cursor:
                #Some fields are returned as byte arrays in python. These will have to be converted into strings using the decode function
                #ret_data += str(row)[13:-4]
                #NEED TO ADD COMMA, EXCEPT ON FIRST ITERATION
                row_formatted = self.format_row(row)
                ret_data += template.format(*row_formatted)
            ret_data = ret_data[:-1] + "}"
            if ret_data == "}":
                ret_data = "{}"
            return {'fetch_status': ret_val, 'db_data': ret_data}
        else:
            return {'fetch_status': ret_val, 'db_data': "No data"}


    @XBlock.json_handler
    def get_incremental_db(self, data, suffix=''):
        """
        The ajax supplied comment may have ' (apostrophe/single quote) embedded in it. These must be escaped before
        being put into the SQL query (which itself relies on single quotes when inserting strings).
        """
        cursor = DiscussionDance.db.cursor()
        ret_val = self.get_all_data(cursor)
        template = '"{0}" : {{ "comment_id" : "{0}", "thread_id" : "{1}", "user_id" : "{2}", "user_name" : "{3}", "comment" : "{4}", "parent_id" : "{5}", "creation_date" : "{6}" }},'
        if(ret_val == "Success"):
            ret_data = "{"

            for row in cursor:
                #Some fields are returned as byte arrays in python. These will have to be converted into strings using the decode function
                #ret_data += str(row)[13:-4]
                #NEED TO ADD COMMA, EXCEPT ON FIRST ITERATION
                row_formatted = self.format_row(row)
                ret_data += template.format(*row_formatted)
            ret_data = ret_data[:-1] + "}"
            return {'fetch_status': ret_val, 'db_data': ret_data}
        else:
            return {'fetch_status': ret_val, 'db_data': "No data"}

    @XBlock.json_handler
    def get_asset(self, data, suffix=''):
        """
        This handler is used to fetch assets (HTML with embedded CSS/JS).
        """
        error = ''
        html = ''
        try:
            html = self.resource_string('static/html/' + data.get('asset'))
        except:
            error = self.get_error_msg()
        return{'asset': html, 'error': error}


    @XBlock.json_handler
    def get_remote_asset(self, data, suffix=''):
        """
        This handler is used to fetch assets (HTML with embedded CSS/JS).
        """
        error = ''
        html = ''
        try:
            html = self.remote_resource_string(data.get('asset'))
        except:
            error = self.get_error_msg()
        return{'asset': html, 'error': error}

    def setup_db(self):
        config_file = self.resource_string("db_settings.txt")
        config_file = config_file.strip(' \t').split('\n')
        config = dict()
        for line in config_file:
            (key, value) = line.strip(' \t\r\n').split(':', 1)
            if str(value).strip() == 'True':
                config[str(key).strip()] = True
            else:
                config[str(key).strip()] = str(value).strip()
        print(config)

        DiscussionDance.db = db_connector.connect(**config)
        """
        settings.py (imported as s) contains a dictionary of key value pairs that define the mysql user name + password, the host on
        which the mysql user has been configured, the name of the database to use (the user specified here must be
        granted access to it on the host specified) and whether warnings should raise exceptions (which will show up in
        lms logs.)
        """
        create_query = (self.resource_string("discussion_setup.sql"))
        self.exec_query(create_query, "Creating Table")

    def student_view(self, context):
        """
        Create a fragment used to display the XBlock to a student.
        `context` is a dictionary used to configure the display (unused).

        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        to display.
        """
        js_url = 'https://raw.githubusercontent.com/DANCEcollaborative/collab-xblock/master/xblock-dance-discussion/static/js/discussion_dance.js'
        css_url = 'https://raw.githubusercontent.com/DANCEcollaborative/collab-xblock/master/xblock-dance-discussion/static/css/discussion_dance.css'
        html_url = 'https://raw.githubusercontent.com/DANCEcollaborative/collab-xblock/master/xblock-dance-discussion/static/html/student_view.html'
        self.setup_db()
        #html = self.remote_resource_string(html_url)
        html = self.resource_string('static/html/student_view.html')
        frag = Fragment(unicode(html).format(self=self,comment=self.comment))
        #css = self.remote_resource_string(css_url)
        css = self.resource_string('static/css/discussion_dance.css')
        frag.add_css(unicode(css))
        #js = self.remote_resource_string(js_url)
        js = self.resource_string('static/js/discussion_dance.js')
        frag.add_javascript(unicode(js))
        frag.initialize_js('discussion_dance')
        return frag

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("Discussion XBlock for DANCE",
            """
            <vertical_demo>
                <discussion_dance/>
            </vertical_demo>
            """)
        ]
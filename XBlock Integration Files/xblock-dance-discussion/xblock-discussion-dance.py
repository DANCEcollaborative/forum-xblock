from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
import settings as s
import sys
import mysql.connector as db_connector
import pkg_resources


"""
TO DO:
Add exception handling for ALL database operations.
Replace console prints with logging statements
Separate out functions into their own modules (ex. All DB functions into a separate DB module)
Add more documentation when possible

"""

class DiscussionDance(XBlock):

    """
    This XBlock creates a discussion thread that conforms to the requirements of DiscourseDB
    (see https://groups.google.com/forum/#!topic/dancecollab/R9UQ5DysfmQ), which is an initiative of the DANCE group at
    CMU (http://www.cs.cmu.edu/~dance/)
    """

    user_id = ''
    parent_comment_id = -1 #This should be set in case the user clicks 'reply to an existing comment'
    thread_id = -1 #This should be fetched using the parent_comment_id to fetch it's thread_id
    comment = ''
    db = None #This is the DB connection. WE NEED TO ENSURE THIS IS CLOSED!

    @staticmethod
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_error_msg(self):
        return(str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    def exec_query(self,query, prefix_msg = ""):
        cursor = self.db.cursor()
        try:
            cursor.execute(query)
        except:
            print(prefix_msg + " Error :" + self.get_error_msg(self)) # PROBABLY NEED TO REPLACE THIS WITH A LOGGING STATEMENT!
        else:
            self.db.commit()
        cursor.close()


    def make_db_connection(self):
        self.db = db_connector.connect(**s.database)
        """
        settings.py (imported as s) contains a dictionary of key value pairs that define the mysql user name + password, the host on
        which the mysql user has been configured, the name of the database to use (the user specified here must be
        granted access to it on the host specified) and whether warnings should raise exceptions (which will show up in
        lms logs.)
        """
        create_query = (self.resource_string( "./discussion_setup.sql"))
        self.exec_query(self, create_query, "Initial Table Create Query")
        test_query = ("INSERT INTO discussion_table (thread_id, user_id, comment, parent_id) VALUES (1, 11, 'Akash made this comment', 1)")
        self.exec_query(self, test_query, "Table Insert Query")

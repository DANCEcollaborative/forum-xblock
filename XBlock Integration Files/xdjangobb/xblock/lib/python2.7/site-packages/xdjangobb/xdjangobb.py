"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer
from xblock.fragment import Fragment
import requests
import re

class DjangoBBXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=0, scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )

    service_url = 'http://127.0.0.1:8000/forum/'
    html_service_endpoint_extension = 'testhtml/'
    css_service_endpoint_extension = 'testcss/'
    js_service_endpoint_extension = 'testjs/'

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the DjangoBBXBlock, shown to students
        when viewing courses.
        """
        #html = self.resource_string("static/html/xdjangobb.html")
        response = requests.get(self.service_url + self.html_service_endpoint_extension)
        #html = str(response.text).strip(' \t\r\n').replace('href="/', 'href="http://localhost:12345/')
        #html = str(response.text).strip(' \t\r\n').decode('utf8')
        html = str(response.text).strip(' \t\r\n')
        #pattern = r'<body>.*</body>'
        #start = re.search(pattern, html).start()
        #end = re.search(pattern, html).end()
        #html = html[start + 6 : end - 7]

        response = requests.get(self.service_url + self.css_service_endpoint_extension)
        css = str(response.text).strip(' \t\r\n')
        #if len(css) > 0:
        #    html += '<p> The css has length ' + str(len(css)) + 'and has the content ' + css + ' </p>'
        #else:
        #    html += '<p> NO CSS! </p>'
        #css = "#my-div{	border-style: solid;    border-width: 5px;	}"
        response = requests.get(self.service_url + self.js_service_endpoint_extension)
        js = str(response.text).strip(' \t\r\n')
        #if len(js) > 0:
        #    html += '<p> The js has length ' + str(len(js)) + 'and has the content ' + js + ' </p>'
        #else:
        #    html += '<p> NO JS! </p>'
        #js = 'function djangobb(runtime, element){alert("This works!");}'
        frag = Fragment(unicode(html).format(self=self))
        frag.add_javascript(unicode(js))
        frag.add_css(unicode(css))
        frag.initialize_js('xdjangobb')
        return frag

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 1
        return {"count": self.count}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.

    @XBlock.json_handler
    def get_django_assets(self, data, suffix=''):
        """
        This handler is used to fetch assets (HTML with embedded CSS/JS).
        """
        original_url_extension = data.get('url')
        original_url_extension = original_url_extension[original_url_extension.find('forum') + 6:]
        response = requests.get(self.service_url + original_url_extension)
        body_contents= re.findall('<body>(.*?)</body>', response.text, re.DOTALL)
        js_contents = ''
        #for js in re.findall('(<script(.*)>(.*?)</script>)', response.text, re.DOTALL):
            #js_contents += js
        return({'html': body_contents, 'js' : js_contents})
        """
        error = ''
        html = ''
        try:
            html = self.remote_resource_string(data.get('asset'))
        except:
            error = self.get_error_msg()
        return{'asset': html, 'error': error}
        """


    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("DjangoBBXBlock",
             """<vertical_demo>
                <xdjangobb/>
                </vertical_demo>
             """),
        ]

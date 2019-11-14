""" https://rahmonov.me/posts/write-python-framework-part-two/
Part I
WSGI compatibility
Request Handlers
Routing: simple and parameterized
 
Part II
Check for duplicate routes
Class Based Handlers
"""

from api import API
app=API()
@app.route('/home')
def home(request,response):
    response.text='Hello Home'
@app.route('/hello/{name}')
def greeting(request,response,name):
    response.text=f'hello {name}'
@app.route('/book')
class BookHandler:
    def get(self,request,response):
        response.text='Some Books!'
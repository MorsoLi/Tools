""" 
Reference: https://rahmonov.me/posts/write-python-framework-part-two/
Part I
WSGI compatibility
Request Handlers
Routing: simple and parameterized
 
Part II
Check for duplicate routes
Class Based Handlers

Part III
Alternative way to add routes (like Django)
Support for templates
"""

from api import API
app=API()

@app.route('/hello/{name}')
def greeting(request,response,name):
    response.text=f'hello {name}'

@app.route('/book')
class BookHandler:
    def get(self,request,response):
        response.text='Some Books!'

def home(request,response):
    response.text='Hello Home'
app.add_route('/home',home)


@app.route('/template')
def template_handler(request,response):
    response.body=app.template('index.html',{'title':'Cheer Up!','name':'demo'}).encode()
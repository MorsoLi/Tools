""" https://rahmonov.me/posts/write-python-framework-part-two/
Part I
WSGI compatibility
Request Handlers
Routing: simple and parameterized
"""

from api import API
app=API()
@app.route('/home')
def home(request,response):
    response.text='Hello Home'
@app.route('/about')
def about(request,response):
    response.text='Hello About'
@app.route('/hello/{name}')
def greeting(request,response,name):
    response.text=f'hello {name}'

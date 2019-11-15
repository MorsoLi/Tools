from flask import Flask,Response

flask_app=Flask('flask_app')

@flask_app.route('/hello')
def hello():
    return Response(
        'Hello World from Flask!\n',
        mimetype='text/plain'
    )

app=flask_app.wsgi_app
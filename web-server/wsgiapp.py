def app(environ,start_response):
    status='200 OK!'
    response_header=[('Content-Type','text/plain')]
    start_response(status,response_header)
    return [b'This is a simple WSGI app!',b'{}'.format(environ['wsgi.version'])]

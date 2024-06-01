from flask import Flask, request, Response
import requests
from flask_cors import CORS
from diskcache import Cache
from config import target_url

app = Flask(__name__)
CORS(app)

cache = Cache('webcache')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def reverse_proxy(path):
    if "asset" in path:
        response = cache.get(path)
        if response:
            return response
    # Forward the request to the target URL
    url = target_url + '/' + path
    headers = {key: value for (key, value) in request.headers if key != 'Host'}
    # Make sure the requests are not in Gzip encoding
    headers['Accept-Encoding'] = 'identity'
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=True,
        stream=False,
    )

    # Create a Flask response with the target server's response
    resp = Response(response.content, response.status_code, headers.items())
    
    orig = request.headers.get('Origin')
    if orig:
        resp.headers['Access-Control-Allow-Origin'] = orig
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    if "assets" in path:
        cache.set(path, resp)
    return resp



@app.route('/setWebSite', methods=['GET', 'POST'])
def set_website():
    global target_url
    target_url = request.args.get('url')
    return 'Target URL set to ' + target_url

"""javascript

function setWebsite(webSite) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:5000/setWebSite?url=" + webSite, true);
    xhr.send();
}

"""

@app.route('/getWebSite', methods=['GET'])
def get_website():
    return target_url



if __name__ == '__main__':
    app.run(debug=True)

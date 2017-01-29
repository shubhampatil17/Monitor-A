from werkzeug.contrib.fixers import ProxyFix
from application import app
import uuid

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == "__main__":
    app.secret_key = str(uuid.uuid4())
    app.run(host='0.0.0.0', debug=True)
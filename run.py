from app import create_app
from waitress import serve
import os

app = create_app(config_name='production')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    serve(app, host='0.0.0.0', port=port)

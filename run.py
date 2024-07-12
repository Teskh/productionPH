from app import create_app
from app.utils import init_excel_file
from config import Config

app = create_app(config_class=Config)

if __name__ == '__main__':
    init_excel_file()
    app.run(debug=app.config['DEBUG'])

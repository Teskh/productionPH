from app import create_app
from app.utils import init_excel_file

app = create_app()

if __name__ == '__main__':
    init_excel_file()
    app.run(debug=True)
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_ckeditor import CKEditor

from config import Config

import os

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy()
csrf = CSRFProtect()
ckeditor = CKEditor()
login_manager = LoginManager(app)

if not os.path.exists("instance"):
    os.makedirs("instance")

db_path = os.path.join("instance", "forum.db")
if not os.path.exists(db_path):
    open(db_path, "w").close()

db.init_app(app)
csrf.init_app(app)
ckeditor.init_app(app)

from views import main
app.register_blueprint(main)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "forum.db")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # CKEditor configuration
    CKEDITOR_PKG_TYPE = os.environ.get('CKEDITOR_PKG_TYPE', 'full')
    CKEDITOR_ENABLE_CODESNIPPET = os.environ.get('CKEDITOR_ENABLE_CODESNIPPET', 'True') == 'True'
    CKEDITOR_TOOLBAR = eval(os.environ.get('CKEDITOR_TOOLBAR', "[['Source', '-', 'Bold', 'Italic', '-', 'Link', 'Unlink', '-', 'CodeSnippet']]"))

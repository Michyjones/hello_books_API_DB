import os
from app import create_app
from app.users.views import user
from app.books.views import book

app = create_app(config_name="development")

app.register_blueprint(user)
app.register_blueprint(book)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

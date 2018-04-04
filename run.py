import os
from app import create_app
from app.users.views import user

app = create_app(config_name="development")

app.register_blueprint(user)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

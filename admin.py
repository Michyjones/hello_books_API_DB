import sys
from sqlalchemy.exc import IntegrityError
from app.models import User
from app import create_app

app = create_app(config_name="development")
app.app_context().push()

if len(sys.argv) != 3:
    print("Run this command- python admin.py email password")
    exit()

email = sys.argv[1]
password = sys.argv[2]

new_admin = User(email=email.strip(), password=password, IsAdmin=True)

try:
    new_admin.save()
    print("Admin create successfully!")
except IntegrityError:
    print()

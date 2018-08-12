import sys
from sqlalchemy.exc import IntegrityError
from app.models import User
from app import create_app

app = create_app(config_name="development")
app.app_context().push()

if len(sys.argv) != 7:
    print("Run this command- python admin.py email password")
    exit()

first_name = sys.argv[1]
last_name = sys.argv[2]
address = sys.argv[3]
email = sys.argv[4]
password = sys.argv[5]
confirm_password = sys.argv[6]

person = User.query.filter_by(email=email).first()
if person:
    print("User already exist")

elif password == confirm_password:

    new_admin = User(first_name=first_name.strip(),
                     last_name=last_name.strip(),
                     address=address,
                     email=email.strip(),
                     password=password,
                     IsAdmin=True)

    try:
        new_admin.save()
        print("Admin create successfully!")
    except IntegrityError:
        print()
else:
    print("Password mismatch")

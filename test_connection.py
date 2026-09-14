from sqlalchemy.orm import sessionmaker
from models import User
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

new_user = User(email="test@example.com", password_hash="fakehash123")
session.add(new_user)
session.commit()

users = session.query(User).all()
print(users)
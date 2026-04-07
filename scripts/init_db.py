import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import engine
from database.models import Base

Base.metadata.create_all(bind=engine)

print("Database created")

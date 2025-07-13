from dotenv import load_dotenv
import os

load_dotenv()  # load .env from current directory

print("DATABASE_URL =", os.getenv("DATABASE_URL"))

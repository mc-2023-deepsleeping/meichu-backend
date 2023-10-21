import pymysql
from pathlib import Path
from dotenv import load_dotenv
import os

dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)

# 資料庫參數設定
db_settings = {
    "host": os.getenv('HOST_IP'),
    "port": int(os.getenv('PORT')),
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "db": os.getenv('DB_NAME'),
    "charset": "utf8"
}

conn = pymysql.connect(**db_settings)
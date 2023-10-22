import os
import tkinter as tk
import tkinter.ttk as ttk
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from sqlalchemy import create_engine

# 設定 GCP MySQL 連接資訊
host = "35.236.171.211"
port = "3306"
user = "root"
password = "mc2023"
db_name = "meichu"
os.environ['OPENAI_API_KEY'] = "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"


# 創建 MySQL 連接字串
database_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"

# Create the agent executor
db = SQLDatabase.from_uri(database_uri)
toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))
agent_executor = create_sql_agent(
    llm=OpenAI(temperature=0),
    toolkit=toolkit,
    verbose=True
)

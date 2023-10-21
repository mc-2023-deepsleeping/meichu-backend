from bardapi import Bard
from pathlib import Path
from dotenv import load_dotenv
import os

dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)

bard = Bard(token=os.getenv('BARD_TOKEN'), language='chinese (traditional)')
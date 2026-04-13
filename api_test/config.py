import os
from dotenv import load_dotenv

load_dotenv()

MOIS_API_KEY = os.getenv("MOIS_API_KEY")   # 행정안전부
MOLIT_API_KEY = os.getenv("MOLIT_API_KEY")  # 국토교통부
SEMAS_API_KEY = os.getenv("SEMAS_API_KEY")  # 소상공인시장진흥공단

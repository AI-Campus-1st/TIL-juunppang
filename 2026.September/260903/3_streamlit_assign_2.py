import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

load_dotenv()

host = os.getenv('DB_HOST1', 'localhost')
port = int(os.getenv('DB_PORT1', 3306))
user = os.getenv('DB_USER1', 'analyst')
password = os.getenv('DB_PASSWORD1', '')
database = os.getenv('DB_NAME1', 'stock_db')

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

def load_stock_infos():
    with engine.connect() as conn:
        query = 'SELECT * FROM tb_stock'
        return pd.read_sql(query, conn)

def load_data(stock_id):
    with engine.connect() as conn:
        query = 'SELECT * FROM tb_price WHERE stock_id=%s ORDER BY created_at DESC LIMIT 100'
        return pd.read_sql(query, conn, params=(stock_id,))

st.title('주식 데이터베이스 연동')

stocks = load_stock_infos()

selected_name = st.selectbox('종목을 선택하세요', options=stocks['name'])

selected_id = stocks.loc[stocks['name'] == selected_name, 'id'].iloc[0]

data = load_data(selected_id)
st.dataframe(data)
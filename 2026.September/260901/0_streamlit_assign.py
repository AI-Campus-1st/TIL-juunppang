import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv('cars.csv')

st.title('자동차 데이터')
st.markdown('<p style="font-weight: 700; color:green;">자동차 데이터 테이블<p>', unsafe_allow_html=True)
# st.markdown('**자동차 데이터 테이블**')

df = load_data()

select_manufacturer = st.selectbox('제조사 선택', options=df['Manufacturer'].unique())
sort_columns_select = st.selectbox('정렬할 컬럼 선택', options= df.columns)

sort_method_select = st.radio('정렬 순서 선택',['오름차순', '내림차순'])
ascending = True if sort_method_select == '오름차순' else False
sort_df = df[df['Manufacturer']== select_manufacturer].sort_values(by=sort_columns_select, ascending=ascending)

st.dataframe(sort_df)
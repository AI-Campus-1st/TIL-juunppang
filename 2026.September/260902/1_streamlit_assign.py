import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# 1. matplotlib
iris = sns.load_dataset('iris')
print(iris)

fig, ax = plt.subplots()
ax.scatter(iris['sepal_length'], iris['sepal_width'], color='blue', label='Sepal')
ax.set_xlabel('Sepal Length')
ax.set_ylabel('Sepal Width')
ax.set_title('Iris Sepal Dimensions')
ax.legend()

st.pyplot(fig)

st.divider()

# 2. seaborn
 
# histplot
fig, ax = plt.subplots()
sns.histplot(iris['petal_length'], bins=10, kde=True)
ax.set_title('Petal Length Distribution')
st.pyplot(fig)

# boxplot
fig, ax = plt.subplots()
sns.boxplot(data=iris, x= iris['species'], y= iris['petal_length'])
ax.set_title('Petal Length by Species')
st.pyplot(fig)


# 3 plotly
fig = px.scatter(data_frame=iris, x="sepal_width", y="sepal_length", color="species", symbol="species",
                 title='Interactive Iris Sepal Scatter Plot')
st.plotly_chart(fig)


fig = px.line(data_frame=iris, x="sepal_length", y="sepal_width", color='species',
              title='Interactive Iris Sepal Line Chart')
st.plotly_chart(fig)


# 인터랙티브 그래프 구현
fig = px.scatter(data_frame=iris, x="sepal_length", y="sepal_width", color="species", symbol="species",
                 title='Interactive Iris Sepal Scatter Plot')

fig.update_layout(
    updatemenus=[
        {'type':'dropdown',
         'buttons':[{
             'label': 'All', 'method':'update','args':[{'visible':[True]*len(iris['species'].unique())}]
        }] +
        [{'label': species, 'method': 'update',
          'args': [{'visible': [species == s for s in iris['species'].unique()]}]} for species in iris['species'].unique()],
          'direction': 'down'}
    ]
)

st.plotly_chart(fig)
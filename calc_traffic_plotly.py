#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import streamlit as st

@st.cache_data  # Decorador de cache
def load_data():
    # Carregue seu arquivo Excel ou faça qualquer processamento demorado aqui
    df = pd.read_excel("trafego_dados_criticos.xlsx")
    return df

# Defina o caminho dos arquivos
caminho_dados_criticos = "trafego_dados_criticos.xlsx"

# Carregue os arquivos em DataFrames
df_dados_criticos_full = load_data()


# In[3]:


# Valores a serem excluídos
valores_excluir = ['NAO DETERMINADO', 'NAO SE APLICA']

# Calcular a quantidade de valores a serem dropados
qtd_dropados = df_dados_criticos_full['DSC_STATION'].isin(valores_excluir).sum()

# Filtrar o DataFrame
df_dados_criticos = df_dados_criticos_full[~df_dados_criticos_full['DSC_STATION'].isin(valores_excluir)]

# Exibir a quantidade de valores dropados
print(f"Quantidade de valores dropados: {qtd_dropados}")


# In[4]:


# Substituir vírgulas por pontos nas colunas de latitude e longitude
#df_dados_criticos['COD_LATITUDE'] = df_dados_criticos['COD_LATITUDE'].str.replace(',', '.')
#df_dados_criticos['COD_LONGITUDE'] = df_dados_criticos['COD_LONGITUDE'].str.replace(',', '.')

# Converter para numérico, forçando erros a NaN
df_dados_criticos['COD_LATITUDE'] = pd.to_numeric(df_dados_criticos['COD_LATITUDE'], errors='coerce')
df_dados_criticos['COD_LONGITUDE'] = pd.to_numeric(df_dados_criticos['COD_LONGITUDE'], errors='coerce')


# In[6]:


# Dividindo os valores por 1.000.000 e formatando com 1 casa decimal
df_dados_criticos['QTD_BYTE_TOTAL'] = (df_dados_criticos['QTD_BYTE_TOTAL'] / 1000000).round(1)
df_dados_criticos['QTD_DOWNLOAD'] = (df_dados_criticos['QTD_DOWNLOAD'] / 1000000).round(1)
df_dados_criticos['QTD_UPLOAD'] = (df_dados_criticos['QTD_UPLOAD'] / 1000000).round(1)


# In[27]:


import pandas as pd

# Filtrando para abril
df_abril = df_dados_criticos[df_dados_criticos['DAT_SESSAO'].dt.month == 4]
df_abril['mês'] = 'abril'

# Filtrando para maio
df_maio = df_dados_criticos[df_dados_criticos['DAT_SESSAO'].dt.month == 5]
df_maio['mês'] = 'maio'

# Concatenando os DataFrames de abril e maio
df_consolidado = pd.concat([df_abril, df_maio], ignore_index=True)


# In[10]:


import streamlit as st
import plotly.express as px

# Título da aplicação
st.title("Recorrentes Nubank: Abril x Maio")
st.subheader("Mapa de Tráfego [MB]")

# Selecionando as tecnologias disponíveis e adicionando a opção "Todas"
tecnologias = df_consolidado['TECNOLOGIA_TRAFEGO'].unique().tolist()
tecnologias = ["Todas"] + list(tecnologias)  # Adiciona "Todas" no início
selected_tec = st.selectbox("Selecione a Tecnologia de Tráfego:", tecnologias)

# Caixa de texto para filtragem por número de telefone
search_term = st.text_input("Digite um número de telefone para filtrar:")

# Filtrando o DataFrame com base na tecnologia selecionada
df_filtrado = df_consolidado

if selected_tec != "Todas":
    df_filtrado = df_filtrado[df_filtrado['TECNOLOGIA_TRAFEGO'] == selected_tec]

if search_term:
    df_filtrado = df_filtrado[df_filtrado['NUM_TEL_ASS_VISIT'].astype(str).str.contains(search_term)]

# Criando o gráfico
grafico_consolidado = px.scatter_mapbox(df_filtrado, 
                                         lon="COD_LONGITUDE", 
                                         lat="COD_LATITUDE", 
                                         size="QTD_BYTE_TOTAL",  
                                         color="mês",  
                                         color_discrete_map={"abril": "blue", "maio": "orange"},  
                                         mapbox_style="open-street-map",
                                         zoom=3, 
                                         title="Distribuição de Dados por Mês")

grafico_consolidado.update_layout(margin={"r": 0, "t": 0, "b": 0, "l": 0})

# Exibindo o gráfico em um tamanho controlado
st.plotly_chart(grafico_consolidado, use_container_width=True)


# In[26]:


# Filtrando os dados para abril e maio
top_abril = df_filtrado[df_filtrado['mês'] == 'abril'].groupby('NUM_TEL_ASS_VISIT')['QTD_BYTE_TOTAL'].sum().reset_index()
top_maio = df_filtrado[df_filtrado['mês'] == 'maio'].groupby('NUM_TEL_ASS_VISIT')['QTD_BYTE_TOTAL'].sum().reset_index()

# Ordenando e pegando os top 10
top_abril = top_abril.sort_values(by='QTD_BYTE_TOTAL', ascending=False).head(10).reset_index(drop=True)
top_maio = top_maio.sort_values(by='QTD_BYTE_TOTAL', ascending=False).head(10).reset_index(drop=True)

# Adicionando o ranking
top_abril['Ranking'] = top_abril.index + 1
top_maio['Ranking'] = top_maio.index + 1

# Exibindo os resultados lado a lado
st.subheader("Top 10 NTC x Volume Total [MB]")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h5 style='font-weight: bold;'>Abril</h5>", unsafe_allow_html=True)
    st.dataframe(top_abril[['Ranking', 'NUM_TEL_ASS_VISIT', 'QTD_BYTE_TOTAL']], hide_index=True)

with col2:
    st.markdown("<h5 style='font-weight: bold;'>Maio</h5>", unsafe_allow_html=True)
    st.dataframe(top_maio[['Ranking', 'NUM_TEL_ASS_VISIT', 'QTD_BYTE_TOTAL']], hide_index=True)


# In[ ]:


# Filtrando os dados para abril e maio
top_abril = df_filtrado[df_filtrado['mês'] == 'abril'].groupby('DSC_STATION')['QTD_BYTE_TOTAL'].sum().reset_index()
top_maio = df_filtrado[df_filtrado['mês'] == 'maio'].groupby('DSC_STATION')['QTD_BYTE_TOTAL'].sum().reset_index()

# Ordenando e pegando os top 10
top_abril = top_abril.sort_values(by='QTD_BYTE_TOTAL', ascending=False).head(10).reset_index(drop=True)
top_maio = top_maio.sort_values(by='QTD_BYTE_TOTAL', ascending=False).head(10).reset_index(drop=True)

# Adicionando o ranking
top_abril['Ranking'] = top_abril.index + 1
top_maio['Ranking'] = top_maio.index + 1

# Exibindo os resultados lado a lado
st.subheader("Top 10 Estações x Volume Total [MB]")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h5 style='font-weight: bold;'>Abril</h5>", unsafe_allow_html=True)
    st.dataframe(top_abril[['Ranking', 'DSC_STATION', 'QTD_BYTE_TOTAL']], hide_index=True)

with col2:
    st.markdown("<h5 style='font-weight: bold;'>Maio</h5>", unsafe_allow_html=True)
    st.dataframe(top_maio[['Ranking', 'DSC_STATION', 'QTD_BYTE_TOTAL']], hide_index=True)


# In[36]:


import streamlit as st
import plotly.express as px
import pandas as pd

# Título da aplicação
st.subheader("Distribuição de Tráfego [MB]")

# Agrupando os dados por mês e tecnologia de tráfego
df_resumo = df_filtrado.groupby(['mês', 'TECNOLOGIA_TRAFEGO']).agg({'QTD_BYTE_TOTAL': 'sum'}).reset_index()

# Calculando a porcentagem por mês
df_resumo['Porcentagem'] = df_resumo.groupby('mês')['QTD_BYTE_TOTAL'].apply(lambda x: x / x.sum() * 100).reset_index(drop=True)

# Criando o gráfico de barras empilhadas
fig = px.bar(df_resumo, 
             x='mês', 
             y='QTD_BYTE_TOTAL', 
             color='TECNOLOGIA_TRAFEGO',
             text='QTD_BYTE_TOTAL',
             #title='Volume Total por Tecnologia de Tráfego por Mês',
             labels={'QTD_BYTE_TOTAL': 'Volume Total'})

# Adicionando as porcentagens no rótulo
for t in fig.data:
    tecnologia = t.name
    porcentagem = df_resumo.loc[df_resumo['TECNOLOGIA_TRAFEGO'] == tecnologia, 'Porcentagem'].values
    t.text = [f"{val} ({porcentagem[i]:.2f}%)" for i, val in enumerate(t.y)]

# Exibindo o gráfico
st.plotly_chart(fig, use_container_width=True)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





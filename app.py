#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Configuração da página da Web
st.set_page_config(page_title="Processador DRX", layout="wide")

st.title("🔬 Aplicativo Interativo para Tratamento de DRX")
st.write("Modifique os parâmetros na barra lateral para ver o impacto direto no gráfico e na identificação dos picos.")

# =======================================================
# BARRA LATERAL: Controles de tudo o que pode ser alterado
# =======================================================
st.sidebar.header("1. Configurações de Leitura")

separador = st.sidebar.selectbox(
    "Separador de Colunas (sep):",
    options=[",", ";", "\\t"],
    format_func=lambda x: "Vírgula (,)" if x=="," else "Ponto e Vírgula (;)" if x==";" else "Tabulação (Tab)"
)

linhas_pular = st.sidebar.number_input(
    "Linhas de cabeçalho a pular (skiprows):",
    min_value=0, max_value=100, value=15
)

st.sidebar.header("2. Filtro de Linha de Base")
tamanho_janela = st.sidebar.slider(
    "Tamanho da Janela (window):",
    min_value=10, max_value=1500, value=500, step=10
)

st.sidebar.header("3. Detecção de Picos")
altura_minima = st.sidebar.slider(
    "Altura Mínima do Pico (height):",
    min_value=5, max_value=2000, value=90, step=5
)

distancia_picos = st.sidebar.slider(
    "Distância Mínima entre Picos (distance):",
    min_value=5, max_value=200, value=60, step=5
)

# =======================================================
# CORPO PRINCIPAL: Upload e Processamento Dinâmico
# =======================================================
arquivo_subido = st.file_uploader("Arraste seu arquivo .txt de DRX aqui", type=["txt"])

if arquivo_subido is not None:
    try:
        # Lendo os dados com as variáveis dinâmicas da barra lateral
        dados = pd.read_csv(
            arquivo_subido, 
            sep=separador, 
            skiprows=linhas_pular, 
            names=['angulo', 'intensidade']
        )

        # Aplicando a borracha deslizante com a janela dinâmica do slider
        linha_de_base = dados['intensidade'].rolling(window=tamanho_janela, center=True, min_periods=1).min()
        dados['intensidade_subtraida'] = dados['intensidade'] - linha_de_base

        # Caçando os picos com os parâmetros dinâmicos dos sliders
        picos_indices, _ = find_peaks(
            dados['intensidade_subtraida'], 
            height=altura_minima, 
            distance=distancia_picos
        )

        # Montando a tabela de picos atualizável
        tabela_picos = dados.iloc[picos_indices][['angulo', 'intensidade_subtraida']]
        ticos_tabela = tabela_picos.rename(columns={'angulo': '2-Theta', 'intensidade_subtraida': 'Intensidade'})

        # Criando o layout de duas colunas na Web (Gráfico na esquerda, Tabela na direita)
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Gráfico de DRX Tratado")
            plt.close('all')
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(dados['angulo'], dados['intensidade_subtraida'], color='blue', label='DRX Limpo')
            ax.plot(dados['angulo'].iloc[picos_indices], dados['intensidade_subtraida'].iloc[picos_indices], "x", color='red', label='Picos')
            ax.set_xlabel('2-Theta')
            ax.set_ylabel('Intensidade')
            ax.legend()
            st.pyplot(fig) # Envia o gráfico para a página web

        with col2:
            st.subheader("Tabela de Picos")
            st.dataframe(ticos_tabela.round(2), use_container_width=True) # Desenha a tabela interativa

            # Botão para baixar a tabela gerada
            csv = ticos_tabela.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Tabela de Picos", data=csv, file_name="picos_calculados.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo. Verifique se o separador e as linhas a pular estão corretos. Detalhe: {e}")


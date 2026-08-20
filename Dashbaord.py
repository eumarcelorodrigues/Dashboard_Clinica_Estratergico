import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Dashboard - Serviços Odontológicos",
    page_icon="🦷",
    layout="wide",
)


# 1. Carregamento e Tratamento de Dados
@st.cache_data
def carregar_dados():
    # Carrega a base Excel
    df = pd.read_excel("Base_Servicos_Odontologicos_Consolidada.xlsx")

    # Limpeza básica
    df["DATA_ATENDIMENTO"] = pd.to_datetime(df["DATA_ATENDIMENTO"])
    df["VALOR_SERVICO"] = pd.to_numeric(
        df["VALOR_SERVICO"], errors="coerce"
    ).fillna(0)

    # Filtrar valores válidos/positivos para análises financeiras
    df["VALOR_AJUSTADO"] = df["VALOR_SERVICO"].apply(
        lambda x: x if x > 0 else 0
    )

    # Extração de Ano e Mês para filtros
    df["ANO"] = df["DATA_ATENDIMENTO"].dt.year
    df["MES_NOME"] = df["DATA_ATENDIMENTO"].dt.strftime("%Y-%m")

    return df


df = carregar_dados()

# 2. Barra Lateral (Filtros)
st.sidebar.header("🔍 Filtros de Análise")

# Filtro de Ano
anos_disponiveis = sorted(df["ANO"].unique(), reverse=True)
ano_selecionado = st.sidebar.multiselect(
    "Selecione o(s) Ano(s):", anos_disponiveis, default=anos_disponiveis
)

# Filtro de Convênio
convenios_disponiveis = df["CONVENIO"].unique()
convenio_selecionado = st.sidebar.multiselect(
    "Selecione o Convênio:",
    convenios_disponiveis,
    default=convenios_disponiveis,
)

# Aplicação dos Filtros
df_filtrado = df[
    (df["ANO"].isin(ano_selecionado))
    & (df["CONVENIO"].isin(convenio_selecionado))
]

# 3. Título Principal
st.title("🦷 Dashboard de Gestão de Serviços Odontológicos")
st.markdown("Visão geral do desempenho financeiro, operacional e de pacientes.")

st.divider()

# 4. Cálculo dos Principais KPIs
df_concluidos = df_filtrado[df_filtrado["STATUS"] == "Concluído"]

faturamento_total = df_concluidos["VALOR_AJUSTADO"].sum()
total_atendimentos = len(df_filtrado)
total_concluidos = len(df_concluidos)
ticket_medio = (
    (faturamento_total / total_concluidos) if total_concluidos > 0 else 0
)

total_faltas = len(df_filtrado[df_filtrado["STATUS"] == "Faltou"])
taxa_falta = (
    (total_faltas / total_atendimentos * 100) if total_atendimentos > 0 else 0
)

# Exibição dos Cartões de Métricas (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Faturamento Concluído", f"R$ {faturamento_total:,.2f}")

with col2:
    st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

with col3:
    st.metric("Total de Agendamentos", f"{total_atendimentos:,}")

with col4:
    st.metric("Taxa de Absenteísmo (Faltas)", f"{taxa_falta:.1f}%")

st.divider()

# 5. Visualizações de Dados (Gráficos)

# Linha 1: Faturamento Temporals & Status dos Atendimentos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Faturamento Mensal (Serviços Concluídos)")
    df_mensal = (
        df_concluidos.groupby("MES_NOME")["VALOR_AJUSTADO"]
        .sum()
        .reset_index()
    )
    fig_mensal = px.line(
        df_mensal,
        x="MES_NOME",
        y="VALOR_AJUSTADO",
        labels={"MES_NOME": "Mês", "VALOR_AJUSTADO": "Faturamento (R$)"},
        markers=True,
    )
    st.plotly_chart(fig_mensal, use_container_width=True)

with col_graf2:
    st.subheader("Distribuição do Status do Atendimento")
    df_status = df_filtrado["STATUS"].value_counts().reset_index()
    df_status.columns = ["STATUS", "QUANTIDADE"]
    fig_status = px.pie(
        df_status,
        names="STATUS",
        values="QUANTIDADE",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(fig_status, use_container_width=True)

# Linha 2: Faturamento por Dentista & Procedimentos Frequentes
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.subheader("Faturamento por Profissional (Dentista)")
    df_dentista = (
        df_concluidos.groupby("DENTISTA")["VALOR_AJUSTADO"]
        .sum()
        .reset_index()
        .sort_values(by="VALOR_AJUSTADO", ascending=True)
    )
    fig_dentista = px.bar(
        df_dentista,
        x="VALOR_AJUSTADO",
        y="DENTISTA",
        orientation="h",
        labels={"VALOR_AJUSTADO": "Faturamento (R$)", "DENTISTA": "Dentista"},
        color="VALOR_AJUSTADO",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_dentista, use_container_width=True)

with col_graf4:
    st.subheader("Faturamento por Procedimento")
    df_proc = (
        df_concluidos.groupby("PROCEDIMENTO")["VALOR_AJUSTADO"]
        .sum()
        .reset_index()
        .sort_values(by="VALOR_AJUSTADO", ascending=False)
    )
    fig_proc = px.bar(
        df_proc,
        x="PROCEDIMENTO",
        y="VALOR_AJUSTADO",
        labels={
            "PROCEDIMENTO": "Procedimento",
            "VALOR_AJUSTADO": "Faturamento (R$)",
        },
        color_discrete_sequence=["#2b5c8f"],
    )
    st.plotly_chart(fig_proc, use_container_width=True)

# 6. Tabela Detalhada dos Dados
st.divider()
st.subheader("📋 Visualização Detalhada dos Registros")
st.dataframe(
    df_filtrado[
        [
            "ID_SERVICO",
            "NOME_PACIENTE",
            "PROCEDIMENTO",
            "CONVENIO",
            "DENTISTA",
            "VALOR_SERVICO",
            "STATUS",
            "DATA_ATENDIMENTO",
        ]
    ]
)
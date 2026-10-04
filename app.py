import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="FinanceDash",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# ESTILO
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stMetric"] {
    background-color: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stMetricValue"] {
    font-size: 28px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNÇÕES
# =========================================================

def formatar_brl(valor):
    valor_formatado = f"{valor:,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"


# =========================================================
# CARREGAR DADOS
# =========================================================

df = pd.read_csv("dados/financeiro.csv")

df["data"] = pd.to_datetime(df["data"])


# =========================================================
# CABEÇALHO
# =========================================================

st.title("📊 FinanceDash")

st.write(
    "Dashboard para controle, acompanhamento e análise financeira."
)


# =========================================================
# FILTROS
# =========================================================

st.sidebar.header("🔎 Filtros")


# Tipo

tipos = st.sidebar.multiselect(
    "Tipo",
    options=df["tipo"].unique(),
    default=df["tipo"].unique()
)


# Categoria

categorias = st.sidebar.multiselect(
    "Categoria",
    options=df["categoria"].unique(),
    default=df["categoria"].unique()
)


# Período

st.sidebar.subheader("Período")

data_minima = df["data"].min().date()
data_maxima = df["data"].max().date()

periodo = st.sidebar.date_input(
    "Selecione o período",
    value=(data_minima, data_maxima),
    min_value=data_minima,
    max_value=data_maxima,
    format="DD/MM/YYYY"
)


# =========================================================
# APLICAR FILTROS
# =========================================================

df_filtrado = df[
    (df["tipo"].isin(tipos)) &
    (df["categoria"].isin(categorias))
].copy()


if len(periodo) == 2:

    inicio = pd.to_datetime(periodo[0])
    fim = pd.to_datetime(periodo[1])

    df_filtrado = df_filtrado[
        (df_filtrado["data"] >= inicio) &
        (df_filtrado["data"] <= fim)
    ]


# =========================================================
# CÁLCULOS
# =========================================================

receitas = df_filtrado[
    df_filtrado["tipo"] == "Receita"
]["valor"].sum()


despesas = df_filtrado[
    df_filtrado["tipo"] == "Despesa"
]["valor"].sum()


saldo = receitas - despesas


total_movimentacoes = len(df_filtrado)


despesas_df = df_filtrado[
    df_filtrado["tipo"] == "Despesa"
]


if not despesas_df.empty:

    gastos_categoria = (
        despesas_df
        .groupby("categoria")["valor"]
        .sum()
    )

    categoria_maior_gasto = gastos_categoria.idxmax()

    valor_maior_gasto = gastos_categoria.max()

else:

    categoria_maior_gasto = "Nenhuma"
    valor_maior_gasto = 0


# =========================================================
# RESUMO FINANCEIRO
# =========================================================

st.subheader("💰 Resumo Financeiro")


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "📈 Receitas",
    formatar_brl(receitas)
)


col2.metric(
    "📉 Despesas",
    formatar_brl(despesas)
)


col3.metric(
    "💵 Saldo",
    formatar_brl(saldo)
)


col4.metric(
    "📋 Movimentações",
    total_movimentacoes
)


# =========================================================
# MAIOR GASTO
# =========================================================

st.markdown("#### 🏷️ Categoria com maior gasto")


if not despesas_df.empty:

    st.info(
        f"**{categoria_maior_gasto}** — "
        f"{formatar_brl(valor_maior_gasto)}"
    )

else:

    st.info(
        "Nenhuma despesa encontrada para os filtros selecionados."
    )


st.divider()


# =========================================================
# GRÁFICOS PRINCIPAIS
# =========================================================

col1, col2 = st.columns(2)


# ---------------------------------------------------------
# DESPESAS POR CATEGORIA
# ---------------------------------------------------------

with col1:

    st.subheader("Despesas por Categoria")

    despesas_categoria = (
        despesas_df
        .groupby("categoria")["valor"]
        .sum()
        .reset_index()
    )


    if not despesas_categoria.empty:

        grafico_categoria = px.pie(
            despesas_categoria,
            names="categoria",
            values="valor",
            hole=0.45
        )

        grafico_categoria.update_layout(
            legend_title_text="Categorias"
        )

        st.plotly_chart(
            grafico_categoria,
            use_container_width=True
        )

    else:

        st.info(
            "Nenhuma despesa encontrada."
        )


# ---------------------------------------------------------
# RECEITAS X DESPESAS
# ---------------------------------------------------------

with col2:

    st.subheader("Receitas x Despesas")

    resumo = (
        df_filtrado
        .groupby("tipo")["valor"]
        .sum()
        .reset_index()
    )


    if not resumo.empty:

        grafico_tipo = px.bar(
            resumo,
            x="tipo",
            y="valor",
            text_auto=".2f"
        )

        grafico_tipo.update_layout(
            xaxis_title="",
            yaxis_title="Valor (R$)"
        )

        st.plotly_chart(
            grafico_tipo,
            use_container_width=True
        )

    else:

        st.info(
            "Nenhuma movimentação encontrada."
        )


# =========================================================
# EVOLUÇÃO FINANCEIRA
# =========================================================

st.subheader("📅 Evolução Financeira Mensal")


df_mensal = df_filtrado.copy()


if not df_mensal.empty:

    df_mensal["mes"] = (
        df_mensal["data"]
        .dt.to_period("M")
        .astype(str)
    )


    mensal = (
        df_mensal
        .groupby(["mes", "tipo"])["valor"]
        .sum()
        .reset_index()
    )


    grafico_mensal = px.line(
        mensal,
        x="mes",
        y="valor",
        color="tipo",
        markers=True
    )


    grafico_mensal.update_layout(
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        legend_title_text="Tipo"
    )


    st.plotly_chart(
        grafico_mensal,
        use_container_width=True
    )

else:

    st.info(
        "Não existem dados para gerar o gráfico mensal."
    )


# =========================================================
# MOVIMENTAÇÕES
# =========================================================

st.subheader("📋 Movimentações")


tabela = df_filtrado[
    [
        "data",
        "tipo",
        "categoria",
        "descricao",
        "valor"
    ]
].copy()


tabela = tabela.sort_values(
    by="data",
    ascending=False
)


tabela["data"] = (
    tabela["data"]
    .dt.strftime("%d/%m/%Y")
)


tabela["valor"] = tabela["valor"].apply(
    formatar_brl
)


st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DOWNLOAD DOS DADOS
# =========================================================

st.subheader("📥 Exportar Dados")


dados_download = df_filtrado.copy()


dados_download["data"] = (
    dados_download["data"]
    .dt.strftime("%d/%m/%Y")
)


csv = dados_download.to_csv(
    index=False,
    sep=";"
).encode("utf-8-sig")


st.download_button(
    label="⬇️ Baixar movimentações em CSV",
    data=csv,
    file_name="financeiro_filtrado.csv",
    mime="text/csv"
)


# =========================================================
# RODAPÉ
# =========================================================

st.divider()


st.caption(
    "FinanceDash • Desenvolvido com Python, Pandas, Streamlit e Plotly"
)
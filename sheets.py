import streamlit as st
import pandas as pd

st.set_page_config(page_title="KPI Analyzer", layout="wide")
st.title("📊 Consolidador de KPIs por Nível de Atendimento")

# Upload dos arquivos
csat_file = st.file_uploader("Upload do arquivo CSAT", type=["xlsx"])
aht_file = st.file_uploader("Upload do arquivo AHT", type=["xlsx"])
e2e_file = st.file_uploader("Upload do arquivo E2E", type=["xlsx"])
cases_file = st.file_uploader("Upload do arquivo Cases", type=["xlsx"])

if csat_file and aht_file and e2e_file and cases_file:
    # Leitura dos arquivos
    csat_df = pd.read_excel(csat_file)
    aht_df = pd.read_excel(aht_file)
    e2e_df = pd.read_excel(e2e_file)
    cases_df = pd.read_excel(cases_file)

    # Padronizar nomes de colunas
    for df in [csat_df, aht_df, e2e_df, cases_df]:
        df.columns = df.columns.astype(str).str.strip().str.lower()

    # Verificação de colunas obrigatórias
    required_cols = ['l4_name', 'l5_name', 'l6_name']
    for df_name, df in zip(['CSAT', 'AHT', 'E2E', 'Cases'], [csat_df, aht_df, e2e_df, cases_df]):
        for col in required_cols:
            if col not in df.columns:
                st.error(f"A planilha {df_name} está faltando a coluna obrigatória: '{col}'")
                st.stop()

    # Formatação das colunas
    if 'csat' in csat_df.columns:
        csat_df["csat"] = (csat_df["csat"] * 100).round(1)

    if 'aht' in aht_df.columns:
        aht_df["aht"] = aht_df["aht"].round(0).astype(int)

    if 'e2e_d' in e2e_df.columns:
        e2e_df["e2e_d"] = e2e_df["e2e_d"].round(1)

    # Renomear colunas
    csat_df = csat_df.rename(columns={"csat": "CSAT (%)"})
    aht_df = aht_df.rename(columns={"aht": "AHT (s)"})
    e2e_df = e2e_df.rename(columns={"e2e_d": "E2E (dias)"})
    cases_df = cases_df.rename(columns={"cases": "Total de Cases"})

    # Merge completo com base em l4, l5, l6
    merged = csat_df.merge(aht_df, on=['l4_name', 'l5_name', 'l6_name'], how="outer")
    merged = merged.merge(e2e_df, on=['l4_name', 'l5_name', 'l6_name'], how="outer")
    merged = merged.merge(cases_df, on=['l4_name', 'l5_name', 'l6_name'], how="outer")
    
    # Adicionar símbolo de "%" na coluna "CSAT (%)"
    if "CSAT (%)" in merged.columns:
        merged["CSAT (%)"] = merged["CSAT (%)"].apply(lambda x: f"{x}%" if pd.notnull(x) else x)
    
    # Filtro para a coluna l4_name a partir da planilha Cases
    opcoes_l4 = cases_df["l4_name"].unique().tolist()
    l4_selecionados = st.sidebar.multiselect("Filtrar por l4_name", options=opcoes_l4, default=opcoes_l4)
    
    # Filtrar a tabela consolidada
    merged = merged[merged["l4_name"].isin(l4_selecionados)]

    st.success("✅ Tabela final consolidada com sucesso!")
    st.dataframe(merged)

    # Download
    csv = merged.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 Baixar CSV Consolidado", data=csv, file_name="kpis_consolidados.csv", mime="text/csv")
else:
    st.info("🔼 Faça o upload dos 4 arquivos para iniciar a consolidação.")
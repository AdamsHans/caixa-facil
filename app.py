import streamlit as st
import pandas as pd
from datetime import date
import io
import zipfile

st.set_page_config(page_title="Caixa Fácil", page_icon="💰", layout="centered")

st.title("💰 Caixa Fácil")
st.caption("Sistema pessoal de ensino de caixa")

# -------------------------------
# ESTADO GLOBAL
# -------------------------------
if "pagamentos" not in st.session_state:
    st.session_state.pagamentos = []

if "contador_id" not in st.session_state:
    st.session_state.contador_id = 1

if "caixa_fechado" not in st.session_state:
    st.session_state.caixa_fechado = False

if "historico" not in st.session_state:
    st.session_state.historico = []

# -------------------------------
# DATA DO CAIXA
# -------------------------------
st.markdown("### 📅 Dados do caixa")
data_caixa = st.date_input("Data", value=date.today(), disabled=st.session_state.caixa_fechado)

# -------------------------------
# NOVO PAGAMENTO
# -------------------------------
st.markdown("### ➕ Novo pagamento")

if st.session_state.caixa_fechado:
    st.info("🔒 Caixa fechado. Não é possível adicionar pagamentos.")
else:
    with st.form("form_pagamento"):
        nome = st.text_input("Nome do cliente")
        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
        forma = st.selectbox("Forma de pagamento", ["PIX", "Dinheiro", "Cartão"])

        enviar = st.form_submit_button("Adicionar pagamento")

        if enviar:
            st.session_state.pagamentos.append({
                "ID": st.session_state.contador_id,
                "Data": str(data_caixa),
                "Cliente": nome,
                "Valor": valor,
                "Forma": forma
            })
            st.session_state.contador_id += 1
            st.success("Pagamento adicionado!")

# -------------------------------
# LISTA DE PAGAMENTOS
# -------------------------------
st.markdown("### 📋 Pagamentos do dia")

if st.session_state.pagamentos:
    df = pd.DataFrame(st.session_state.pagamentos)

    for _, row in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 1])

        col1.write(row["ID"])
        col2.write(row["Cliente"])
        col3.write(f"R$ {row['Valor']:.2f}")
        col4.write(row["Forma"])

        if not st.session_state.caixa_fechado:
            if col5.button("🗑", key=f"del_{row['ID']}"):
                st.session_state["confirmar_delete"] = row["ID"]

else:
    st.info("Nenhum pagamento registrado.")

# -------------------------------
# CONFIRMAÇÃO DE EXCLUSÃO
# -------------------------------
if "confirmar_delete" in st.session_state:
    st.warning("⚠️ Deseja realmente excluir este pagamento?")
    c1, c2 = st.columns(2)

    if c1.button("✅ Sim"):
        st.session_state.pagamentos = [
            p for p in st.session_state.pagamentos
            if p["ID"] != st.session_state.confirmar_delete
        ]
        del st.session_state["confirmar_delete"]
        st.experimental_rerun()

    if c2.button("❌ Não"):
        del st.session_state["confirmar_delete"]

# -------------------------------
# TOTAIS
# -------------------------------
st.markdown("### 📊 Totais")

if st.session_state.pagamentos:
    df = pd.DataFrame(st.session_state.pagamentos)
    total_pix = df[df["Forma"] == "PIX"]["Valor"].sum()
    total_geral = df["Valor"].sum()
else:
    total_pix = total_geral = 0

st.metric("PIX total", f"R$ {total_pix:.2f}")
st.metric("💵 Total geral", f"R$ {total_geral:.2f}")

# -------------------------------
# FECHAR CAIXA
# -------------------------------
st.markdown("### 🔒 Fechamento")

if not st.session_state.caixa_fechado:
    if st.button("Fechar caixa"):
        st.session_state.caixa_fechado = True
        st.session_state.historico.append({
            "data": str(data_caixa),
            "pagamentos": st.session_state.pagamentos.copy(),
            "total": total_geral
        })
        st.success("Caixa fechado com sucesso!")
else:
    st.success("✅ Caixa fechado")

# -------------------------------
# RELATÓRIO
# -------------------------------
st.markdown("### 📥 Relatório")

def gerar_relatorio_zip(df, data):
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr(f"relatorio_caixa_{data}.xlsx", excel_buffer.read())

    zip_buffer.seek(0)
    return zip_buffer

if st.session_state.caixa_fechado and st.session_state.pagamentos:
    df = pd.DataFrame(st.session_state.pagamentos)
    relatorio = gerar_relatorio_zip(df, data_caixa)

    st.download_button(
        "⬇️ Baixar relatório",
        data=relatorio,
        file_name=f"caixa_{data_caixa}.zip",
        mime="application/zip"
    )
else:
    st.info("Feche o caixa para liberar o relatório.")

# -------------------------------
# HISTÓRICO
# -------------------------------
st.markdown("### 🗂 Histórico da sessão")

if st.session_state.historico:
    hist_df = pd.DataFrame(st.session_state.historico)
    st.dataframe(hist_df)
else:
    st.caption("Nenhum caixa fechado ainda.")

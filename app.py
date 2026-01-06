import streamlit as st
import pandas as pd
from datetime import date
import io
import zipfile

st.set_page_config(page_title="Caixa Fácil", page_icon="💰", layout="centered")

st.title("💰 Caixa Fácil")
st.caption("Sistema pessoal de ensino de caixa")

# ===============================
# ESTADO
# ===============================
if "pagamentos" not in st.session_state:
    st.session_state.pagamentos = []

if "contador_id" not in st.session_state:
    st.session_state.contador_id = 1

if "caixa_fechado" not in st.session_state:
    st.session_state.caixa_fechado = False

# ===============================
# DATA
# ===============================
st.markdown("### 📅 Dados do caixa")
data_caixa = st.date_input(
    "Data",
    value=date.today(),
    disabled=st.session_state.caixa_fechado
)

# ===============================
# NOVO PAGAMENTO
# ===============================
st.markdown("### ➕ Novo pagamento")

if not st.session_state.caixa_fechado:
    with st.form("form_pagamento"):
        nome = st.text_input("Nome do cliente")
        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")

        forma = st.selectbox(
            "Forma de pagamento",
            ["PIX", "Crédito", "Débito", "Dinheiro"]
        )

        comprovante = st.file_uploader(
            "Comprovante (opcional)",
            type=["jpg", "jpeg", "png", "pdf"]
        )

        enviar = st.form_submit_button("Adicionar pagamento")

        if enviar:
            arquivo_nome = None
            arquivo_bytes = None

            if comprovante:
                ext = comprovante.name.split(".")[-1]
                arquivo_nome = f"{data_caixa}_{forma}_{nome}_{valor:.2f}.{ext}".replace(" ", "_")
                arquivo_bytes = comprovante.read()

            st.session_state.pagamentos.append({
                "ID": st.session_state.contador_id,
                "Data": str(data_caixa),
                "Cliente": nome,
                "Valor": valor,
                "Forma": forma,
                "Arquivo": arquivo_nome,
                "Bytes": arquivo_bytes
            })

            st.session_state.contador_id += 1
            st.success("Pagamento adicionado!")
else:
    st.info("🔒 Caixa fechado.")

# ===============================
# LISTAGEM
# ===============================
st.markdown("### 📋 Pagamentos do dia")

if st.session_state.pagamentos:
    for p in st.session_state.pagamentos:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 1])
        col1.write(p["ID"])
        col2.write(p["Cliente"])
        col3.write(f"R$ {p['Valor']:.2f}")
        col4.write(p["Forma"])

        if not st.session_state.caixa_fechado:
            if col5.button("🗑", key=f"del_{p['ID']}"):
                st.session_state.pagamentos = [
                    x for x in st.session_state.pagamentos if x["ID"] != p["ID"]
                ]
                st.experimental_rerun()
else:
    st.info("Nenhum pagamento registrado.")

# ===============================
# TOTAIS (COMPLETOS)
# ===============================
st.markdown("### 📊 Totais")

if st.session_state.pagamentos:
    df = pd.DataFrame(st.session_state.pagamentos)

    total_pix = df[df["Forma"] == "PIX"]["Valor"].sum()
    total_credito = df[df["Forma"] == "Crédito"]["Valor"].sum()
    total_debito = df[df["Forma"] == "Débito"]["Valor"].sum()
    total_dinheiro = df[df["Forma"] == "Dinheiro"]["Valor"].sum()
    total_geral = df["Valor"].sum()

    c1, c2 = st.columns(2)
    c1.metric("💳 PIX", f"R$ {total_pix:.2f}")
    c2.metric("💳 Crédito", f"R$ {total_credito:.2f}")

    c3, c4 = st.columns(2)
    c3.metric("💳 Débito", f"R$ {total_debito:.2f}")
    c4.metric("💵 Dinheiro", f"R$ {total_dinheiro:.2f}")

    st.divider()
    st.metric("💰 Total geral", f"R$ {total_geral:.2f}")
else:
    st.info("Sem pagamentos para calcular totais.")

# ===============================
# FECHAR CAIXA
# ===============================
st.markdown("### 🔒 Fechamento")

if not st.session_state.caixa_fechado:
    if st.button("Fechar caixa"):
        st.session_state.caixa_fechado = True
        st.success("Caixa fechado com sucesso!")
else:
    st.success("Caixa já fechado.")

# ===============================
# RELATÓRIO
# ===============================
st.markdown("### 📥 Relatório")

def gerar_zip(pagamentos, data):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        df = pd.DataFrame(pagamentos).drop(columns=["Bytes"])
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        zipf.writestr(f"relatorio_caixa_{data}.xlsx", excel_buffer.getvalue())

        for p in pagamentos:
            if p["Arquivo"] and p["Bytes"]:
                zipf.writestr(f"comprovantes/{p['Arquivo']}", p["Bytes"])

    zip_buffer.seek(0)
    return zip_buffer

if st.session_state.caixa_fechado and st.session_state.pagamentos:
    zip_file = gerar_zip(st.session_state.pagamentos, data_caixa)

    st.download_button(
        "⬇️ Baixar relatório completo",
        data=zip_file,
        file_name=f"caixa_{data_caixa}.zip",
        mime="application/zip"
    )
else:
    st.info("Feche o caixa para liberar o relatório.")

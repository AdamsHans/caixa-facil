import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import zipfile

st.set_page_config(page_title="💰 Caixa Fácil", layout="wide")

# ================== ESTADO ==================
if "pagamentos" not in st.session_state:
    st.session_state.pagamentos = []

if "caixa_fechado" not in st.session_state:
    st.session_state.caixa_fechado = False

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0  # Para resetar o file_uploader

# ================== FUNÇÕES ==================
def calcular_totais(pagamentos):
    totais = {"PIX": 0, "Crédito": 0, "Débito": 0, "Dinheiro": 0}
    for p in pagamentos:
        totais[p["Forma"]] += p["Valor"]
    return totais

def gerar_relatorio_zip(pagamentos, data_caixa):
    df = pd.DataFrame(
        [
            {
                "Data": p["Data"],
                "Cliente": p["Cliente"],
                "Valor": p["Valor"],
                "Forma": p["Forma"],
                "Comprovante": "SIM" if p["Comprovante"] else "NÃO",
            }
            for p in pagamentos
        ]
    )

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False, sep=";", encoding="utf-8-sig")
        zipf.writestr(f"relatorio_{data_caixa}.csv", csv_buffer.getvalue())

        for i, p in enumerate(pagamentos):
            if p["Comprovante"] is not None:
                nome = f"{i+1}_{p['Cliente']}_{p['Forma']}.jpg"
                zipf.writestr(f"comprovantes/{nome}", p["Comprovante"].getvalue())

    zip_buffer.seek(0)
    return zip_buffer

def cor_card(forma):
    cores = {
        "PIX": "#d4f7dc",
        "Crédito": "#d0e0ff",
        "Débito": "#ffe6d4",
        "Dinheiro": "#fff3b0"
    }
    return cores.get(forma, "#f0f0f0")

# ================== INTERFACE ==================
st.title("💰 Caixa Fácil")
st.caption("Sistema pessoal de ensino de caixa")
data_caixa = st.date_input("📅 Data do caixa", value=date.today())

st.divider()

# ================== NOVO PAGAMENTO ==================
st.subheader("➕ Novo pagamento")
if st.session_state.caixa_fechado:
    st.info("🔒 Caixa fechado.")
else:
    with st.form("novo_pagamento"):
        cliente = st.text_input("Nome do cliente")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        forma = st.selectbox(
            "Forma de pagamento",
            ["PIX", "Crédito", "Débito", "Dinheiro"]
        )
        comprovante = st.file_uploader(
            "Comprovante (opcional)",
            type=["jpg", "jpeg", "png"],
            key=st.session_state.uploader_key
        )
        enviar = st.form_submit_button("Adicionar")
        if enviar and cliente and valor > 0:
            st.session_state.pagamentos.append(
                {
                    "Data": data_caixa.strftime("%Y-%m-%d"),
                    "Cliente": cliente,
                    "Valor": float(valor),
                    "Forma": forma,
                    "Comprovante": comprovante,
                }
            )
            st.session_state.uploader_key += 1  # reset uploader
            st.success("Pagamento registrado.")

# ================== LISTAGEM MODERNA ==================
st.divider()
st.subheader("📋 Pagamentos do dia")
if not st.session_state.pagamentos:
    st.info("Nenhum pagamento registrado.")
else:
    for i, p in enumerate(st.session_state.pagamentos):
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:{cor_card(p['Forma'])};
                            padding:15px;
                            border-radius:10px;
                            margin-bottom:5px;">
                <b>{i+1}. {p['Cliente']}</b> | R$ {p['Valor']:.2f} | {p['Forma']} 
                {"| ✅ Comprovante" if p['Comprovante'] else ""}
                </div>
                """,
                unsafe_allow_html=True
            )
            if not st.session_state.caixa_fechado:
                if st.button("🗑️ Apagar", key=f"del_{i}"):
                    st.session_state.pagamentos.pop(i)
                    st.experimental_rerun()

# ================== TOTAIS ==================
st.divider()
st.subheader("📊 Totais")
totais = calcular_totais(st.session_state.pagamentos)
total_geral = sum(totais.values())

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💳 PIX", f"R$ {totais['PIX']:.2f}")
col2.metric("💳 Crédito", f"R$ {totais['Crédito']:.2f}")
col3.metric("💳 Débito", f"R$ {totais['Débito']:.2f}")
col4.metric("💵 Dinheiro", f"R$ {totais['Dinheiro']:.2f}")
col5.metric("💰 Total geral", f"R$ {total_geral:.2f}")

# ================== FECHAMENTO ==================
st.divider()
st.subheader("🔒 Fechamento")
if not st.session_state.caixa_fechado:
    if st.button("Fechar caixa"):
        st.session_state.caixa_fechado = True
        st.success("Caixa fechado.")
else:
    st.info("Caixa já fechado.")

# ================== RELATÓRIO ==================
st.divider()
st.subheader("📥 Relatório")
if not st.session_state.caixa_fechado:
    st.warning("Feche o caixa para gerar o relatório.")
elif not st.session_state.pagamentos:
    st.warning("Nenhum pagamento para relatório.")
else:
    zip_file = gerar_relatorio_zip(st.session_state.pagamentos, data_caixa)
    st.download_button(
        "📦 Baixar relatório (CSV + comprovantes)",
        data=zip_file,
        file_name=f"fechamento_caixa_{data_caixa}.zip",
        mime="application/zip",
    )

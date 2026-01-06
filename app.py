import streamlit as st
import sqlite3
import pandas as pd
import os
import zipfile
import re
from io import BytesIO
from datetime import date

# ---------------- CONFIGURAÇÃO ----------------
st.set_page_config(page_title="Caixa Fácil", page_icon="💰", layout="centered")

DB_NAME = "pagamentos.db"
PASTA_COMPROVANTES = "comprovantes"

os.makedirs(PASTA_COMPROVANTES, exist_ok=True)

# ---------------- FUNÇÕES AUXILIARES ----------------
def limpar_nome(texto):
    texto = texto.strip().replace(" ", "_")
    texto = re.sub(r"[^a-zA-Z0-9_-]", "", texto)
    return texto.lower()

def conectar_db():
    return sqlite3.connect(DB_NAME)

def criar_tabela():
    with conectar_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            cliente TEXT,
            valor REAL,
            forma TEXT,
            comprovante TEXT
        )
        """)

def salvar_pagamento(data, cliente, valor, forma, comprovante):
    with conectar_db() as conn:
        conn.execute(
            "INSERT INTO pagamentos VALUES (NULL, ?, ?, ?, ?, ?)",
            (data, cliente, valor, forma, comprovante)
        )

def carregar_pagamentos(data):
    with conectar_db() as conn:
        return pd.read_sql(
            "SELECT * FROM pagamentos WHERE data = ?",
            conn,
            params=(data,)
        )

def gerar_relatorio_zip(df, data_caixa):
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Excel
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        zipf.writestr(f"relatorio_{data_caixa}.xlsx", excel_buffer.getvalue())

        # Comprovantes
        for _, row in df.iterrows():
            if row["comprovante"]:
                caminho = os.path.join(PASTA_COMPROVANTES, row["comprovante"])
                if os.path.exists(caminho):
                    zipf.write(caminho, arcname=f"comprovantes/{row['comprovante']}")

    buffer.seek(0)
    return buffer

# ---------------- INICIALIZAÇÃO ----------------
criar_tabela()

# ---------------- INTERFACE ----------------
st.title("💰 Caixa Fácil")
st.caption("Sistema pessoal de fechamento de caixa")

data_caixa = st.date_input("📅 Data do caixa", value=date.today()).isoformat()

st.divider()
st.subheader("➕ Novo pagamento")

with st.form("form_pagamento", clear_on_submit=True):
    nome_cliente = st.text_input("Nome do cliente")
    valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01, format="%.2f")
    forma_pagamento = st.selectbox(
        "Forma de pagamento",
        ["PIX", "DéBITO", "CRÉDITO", "ESPÉCIE"]
    )
    comprovante = st.file_uploader(
        "Comprovante (opcional)",
        type=["jpg", "jpeg", "png", "pdf"]
    )

    enviar = st.form_submit_button("Salvar pagamento")

    if enviar:
        if nome_cliente and valor > 0:
            arquivo_nome = None

            if comprovante:
                extensao = os.path.splitext(comprovante.name)[1]
                nome_limpo = limpar_nome(nome_cliente)
                valor_fmt = f"{valor:.2f}"

                arquivo_nome = f"{data_caixa}_{forma_pagamento}_{nome_limpo}_{valor_fmt}{extensao}"
                caminho = os.path.join(PASTA_COMPROVANTES, arquivo_nome)

                with open(caminho, "wb") as f:
                    f.write(comprovante.getbuffer())

            salvar_pagamento(
                data_caixa,
                nome_cliente,
                valor,
                forma_pagamento,
                arquivo_nome
            )

            st.success("Pagamento salvo com sucesso ✅")
        else:
            st.error("Preencha o nome e um valor válido.")

# ---------------- LISTAGEM ----------------
st.divider()
st.subheader("📋 Pagamentos do dia")

df = carregar_pagamentos(data_caixa)

if not df.empty:
    st.dataframe(
        df[["cliente", "valor", "forma", "comprovante"]],
        use_container_width=True
    )

    st.subheader("📊 Totais")
    total_pix = df[df["forma"] == "PIX"]["valor"].sum()
    total_geral = df["valor"].sum()

    st.metric("Total PIX", f"R$ {total_pix:.2f}")
    st.metric("💵 Total Geral", f"R$ {total_geral:.2f}")

    st.divider()
    st.subheader("📥 Relatório do dia")

    relatorio = gerar_relatorio_zip(df, data_caixa)

    st.download_button(
        label="📦 Baixar relatório (Excel + comprovantes)",
        data=relatorio,
        file_name=f"relatorio_caixa_{data_caixa}.zip",
        mime="application/zip"
    )
else:
    st.info("Nenhum pagamento registrado para esta data.")

import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO
from datetime import date

# =============================
# CONFIGURAÇÃO INICIAL
# =============================
st.set_page_config(
    page_title="Caixa Fácil",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Caixa Fácil")
st.caption("Sistema pessoal de fechamento de caixa")

# =============================
# PASTA DE DADOS
# =============================
BASE_DIR = "dados"
COMPROVANTES_DIR = os.path.join(BASE_DIR, "comprovantes")
os.makedirs(COMPROVANTES_DIR, exist_ok=True)

# =============================
# DATA DO CAIXA
# =============================
data_caixa = st.date_input("📅 Data do caixa", value=date.today())
arquivo_csv = os.path.join(BASE_DIR, f"caixa_{data_caixa}.csv")

# =============================
# CARREGAR DADOS
# =============================
if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
else:
    df = pd.DataFrame(columns=["data", "cliente", "valor", "forma", "comprovante"])

# =============================
# NOVO PAGAMENTO
# =============================
st.subheader("➕ Novo pagamento")

cliente = st.text_input("Nome do cliente")
valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0, format="%.2f")
forma = st.selectbox("Forma de pagamento", ["PIX", "Débito", "Crédito", "Espécie"])
arquivo = st.file_uploader(
    "Comprovante (opcional)",
    type=["jpg", "jpeg", "png", "pdf"]
)

if st.button("Salvar pagamento"):
    if cliente and valor > 0:
        caminho_comprovante = ""

        if arquivo:
            nome_arquivo = f"{data_caixa}_{cliente}_{valor:.2f}.{arquivo.name.split('.')[-1]}"
            caminho_comprovante = os.path.join(COMPROVANTES_DIR, nome_arquivo)

            with open(caminho_comprovante, "wb") as f:
                f.write(arquivo.getbuffer())

        novo = {
            "data": data_caixa,
            "cliente": cliente,
            "valor": valor,
            "forma": forma,
            "comprovante": caminho_comprovante
        }

        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(arquivo_csv, index=False)
        st.success("Pagamento salvo com sucesso!")
        st.rerun()
    else:
        st.warning("Preencha corretamente cliente e valor.")

# =============================
# PAGAMENTOS DO DIA
# =============================
st.subheader("📋 Pagamentos do dia")

if not df.empty:
    st.dataframe(df[["cliente", "valor", "forma"]], use_container_width=True)

    st.subheader("📊 Totais")
    total_pix = df[df["forma"] == "PIX"]["valor"].sum()
    total_geral = df["valor"].sum()

    st.write(f"**Total PIX:** R$ {total_pix:.2f}")
    st.write(f"**💵 Total Geral:** R$ {total_geral:.2f}")
else:
    st.info("Nenhum pagamento registrado.")

# =============================
# FUNÇÃO DE RELATÓRIO (ANTI-ERRO)
# =============================
def gerar_relatorio_zip(df, data_caixa):
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:

        # TENTAR EXCEL
        try:
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False)
            zipf.writestr(
                f"relatorio_{data_caixa}.xlsx",
                excel_buffer.getvalue()
            )
            formato = "Excel (.xlsx)"

        except Exception:
            # FALLBACK CSV
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
            zipf.writestr(
                f"relatorio_{data_caixa}.csv",
                csv_buffer.getvalue()
            )
            formato = "CSV (.csv)"

        # COMPROVANTES
        for _, row in df.iterrows():
            if isinstance(row["comprovante"], str) and row["comprovante"]:
                if os.path.exists(row["comprovante"]):
                    zipf.write(
                        row["comprovante"],
                        arcname=os.path.basename(row["comprovante"])
                    )

    return zip_buffer.getvalue(), formato

# =============================
# DOWNLOAD DO RELATÓRIO
# =============================
st.subheader("📥 Relatório do dia")

if not df.empty:
    relatorio, formato = gerar_relatorio_zip(df, data_caixa)

    st.download_button(
        label=f"📥 Baixar relatório ({formato})",
        data=relatorio,
        file_name=f"caixa_{data_caixa}.zip",
        mime="application/zip"
    )

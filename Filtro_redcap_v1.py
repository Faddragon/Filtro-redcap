import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Filtro REDCap - CCP IAVC", layout="wide")
st.title("📄 Filtro de Planilhas do REDCap - CCP IAVC")

# 📍 1. Identificação do Usuário
st.subheader("👤 Identificação do Usuário")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.email = ""
    st.session_state.telefone = ""

if not st.session_state.autenticado:
    email = st.text_input("E-mail:", placeholder="seuemail@exemplo.com")
    telefone = st.text_input("Telefone (WhatsApp):", placeholder="(11) 91234-5678")
    entrar = st.button("🔐 Entrar")

    if entrar:
        if not email.strip() or not telefone.strip():
            st.warning("⚠️ Por favor, preencha *todos os campos* para continuar.")
            st.stop()
        else:
            st.session_state.autenticado = True
            st.session_state.email = email.strip()
            st.session_state.telefone = telefone.strip()
            st.success(f"✅ Acesso liberado para: {email}")
            st.experimental_rerun()
    else:
        st.stop()
else:
    st.success(f"✅ Acesso liberado para: {st.session_state.email}")

# 📥 2. Upload do CSV do REDCap
st.subheader("📥 Upload da Planilha (.csv) do REDCap")
uploaded_file = st.file_uploader(
    "Selecione o arquivo CSV exportado do REDCap",
    type=["csv"]
)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, sep=",", encoding="utf-8", engine="python")
    except Exception as e:
        st.error(f"❌ Erro ao ler o CSV: {e}")
        st.stop()

    # 3️⃣ Agrupamento por hospital_registry (primeiro preenchimento não nulo por coluna)
    df_grouped = df.groupby("hospital_registry", as_index=False).first()

    # 4️⃣ Seleção de colunas
    colunas_relevantes = [  # <- encurtado para exemplo
        "hospital_registry", "record_id", "incl_date", "dob", "age", "sex",
        "thyroid_disease", "hn_site"
    ]
    df_filtrado = df_grouped[[col for col in colunas_relevantes if col in df_grouped.columns]].copy()

    # 5️⃣ Subdivisão em abas
    abas = {"Todos Casos": df_filtrado}

    if "thyroid_disease" in df_filtrado.columns:
        abas["Tireoide"] = df_filtrado[df_filtrado["thyroid_disease"].notna()]

    if "hn_site" in df_filtrado.columns:
        mapa_subsitios = {
            1: "Pele e anexos", 2: "Lábio", 3: "Boca", 4: "Orofaringe", 5: "Laringe",
            6: "Hipofaringe", 7: "Cavidade nasal", 8: "Rinofaringe", 9: "Maxila",
            10: "Seios paranasais", 12: "Glândula salivar", 13: "Outros", 14: "Tumor primário oculto"
        }
        for k, v in mapa_subsitios.items():
            abas[v] = df_filtrado[df_filtrado["hn_site"] == k]

    # 6️⃣ Geração do Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for nome, tabela in abas.items():
            tabela.to_excel(writer, sheet_name=nome[:31], index=False)

    st.success("✅ Arquivo processado com sucesso!")
    st.download_button(
        label="📥 Baixar planilha Excel filtrada",
        data=buffer.getvalue(),
        file_name=f"planilha_filtrada_{datetime.today().date()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Rodapé
st.markdown("""
<hr style="margin-top: 2em; margin-bottom: 1em;">
<div style='text-align: center; font-size: 14px; color: gray;'>
    🔬 Desenvolvido por <strong>CECI</strong> · <em>Computational Engine for Clinical Insights</em><br>
    📧 Contato: <a href='mailto:franciscoadias@gmail.com'>franciscoadias@gmail.com</a>
</div>
""", unsafe_allow_html=True)


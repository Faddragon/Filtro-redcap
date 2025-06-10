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
            st.rerun()

    else:
        st.stop()
else:
    st.success(f"✅ Acesso liberado para: {st.session_state.email}")

# 📥 2. Upload do CSV do REDCap
st.subheader("📥 Upload da Planilha (.csv) do REDCap")
uploaded_file = st.file_uploader("Selecione o arquivo CSV exportado do REDCap", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, sep=",", encoding="utf-8", quotechar='"', on_bad_lines='skip', engine="python")
    except Exception as e:
        st.error(f"❌ Erro ao ler o CSV: {e}")
        st.stop()


    # 3️⃣ Agrupamento por hospital_registry (primeiro preenchimento não nulo por coluna)
    df_grouped = df.groupby("hospital_registry", as_index=False).first()

    # 4️⃣ Seleção de colunas
    colunas_relevantes = ["hospital_registry", "record_id", "incl_date", "dob", "age", "sex", "race",
        "weigh_time0", "height", "bmi_time0", "ecog_time0", "state", "schooling", "job",
        "profession", "religion", "income", "identificacao_e_dados_demograficos_r2_complete",
        "tabacco", "alcohol", "sun", "wood_smoke", "radiation", "burn", "trauma", "family_hist",
        "sexual_risk", "risk_fact_other", "cancer_family", "risk_other", "tabacco_type", "tabacco_other",
        "cigar_pack", "age_tabacco", "actual_smoke", "age_stop_tobacco", "tabacco_time", "tabacco_load",
        "alcohol_type", "alcohol_other", "distilled", "wine", "bier", "age_alcool", "age_stop_alcohol",
        "alcohol_time", "alcohol_load", "general_other", "complaint_history", "dysphonia", "dysphagia",
        "dyspnea", "globus", "nodule", "dislalia", "otalgia", "odynophagia", "ulcer", "epistaxis",
        "rino_otorrhea", "buzz", "nasal_obst", "eye", "edema_pain", "cranial_nerve", "weight_loss",
        "night_dysp", "orthopnea", "effort_dysp", "speak_dysp", "weight_kg", "weight_time",
        "antecedentes___1", "antecedentes___2", "antecedentes___3", "antecedentes___4",
        "antecedentes___5", "antecedentes___6", "past_surgery", "comorbidities_y_n", "comorbidities___1",
        "comorbidities___2", "comorbidities___3", "comorbidities___4", "comorbidities___5",
        "comorbidities___6", "comorbidities___7", "comorbidities___8", "comorbidities_other",
        "meds_y_n", "meds", "skin", "face", "cranial_nerve_2", "lip", "mouth", "nasopharynx", "larynx",
        "lymph_node", "thyroid_nod", "neck_tumor", "salivar_gland", "skin_region",
        "skin_region_other_which", "skin_side", "skin_nodule", "skin_ulcer", "skin_lesion", "skin_other",
        "skin_other_which", "skin_size", "skin_mobility", "skin_nodule_consistency", "skin_descript",
        "face_region", "face_region_other", "face_side", "face_tumor", "face_eye", "face_trismus",
        "face_other", "face_other_which", "mouth_opening", "cranial_nerve_which",
        "cranial_nerve_mult___1", "cranial_nerve_mult___2", "cranial_nerve_mult___3",
        "cranial_nerve_mult___4", "cranial_nerve_mult___5", "cranial_nerve_mult___6",
        "cranial_nerve_mult___7", "cranial_nerve_mult___8", "cranial_nerve_mult___9",
        "cranial_nerve_mult___10", "cranial_nerve_mult___11", "cranial_nerve_mult___12",
        "cranial_nerve_mult___13", "cranial_nerve_side", "vii_branch", "vii_branch_multi___1",
        "vii_branch_multi___2", "vii_branch_multi___3", "vii_branch_multi___4", "vii_house_brack_scale",
        "cranial_nerve_details", "lip_exam", "lip_region", "lip_subregion", "lip_side", "lip_commissure",
        "lip_size", "lip_thickness", "lip_extension", "lip_multi_which___2", "lip_multi_which___3",
        "lip_multi_which___4", "lip_multi_which___5", "lip_multi_which___6", "lip_exam_other",
        "mouth_trismus", "mouth_opening_2", "tooth", "mouth_prosthesis", "oral_hygiene", "mouth_lesion",
        "mouth_lesion_which", "mouth_lesion_other", "mouth_lesion_region", "mouth_lesion_size",
        "mouth_lesion_laterality", "mouth_lesion_depth", "mouth_lesion_extension",
        "mouth_lesion_description", "nasopharyx_wich", "nasal_side", "nasal_rhinorrhea",
        "nasal_epistaxis", "nasal_lesion", "nasal_local", "nasal_lesion_type", "nasal_lesion_describe",
        "nasopharyx_local", "nasopharyx_multi___1", "nasopharyx_multi___2", "nasopharyx_lesion_type",
        "nasopharyx_lesion_descrip", "larynx_lesion", "larynx_mobility", "larynx_aspiration",
        "larynx_salivar", "larynx_obstruct", "tqt", "g_tube", "larynx_lesion_local",
        "larynx_lesion_side", "larynx_lesion_type", "larynx_lesion_descript", "larynx_mob_side",
        "larynx_mob_type", "larynx_obst_local", "larynx_obst_degree", "thy_feature", "thy_other",
        "thyroid_nodule", "thy_size", "thy_consistency", "thy_mobility", "lymph_side", "lymph_chain",
        "lymph_chain_mult___1", "lymph_chain_mult___2", "lymph_chain_mult___3", "lymph_chain_mult___4",
        "lymph_chain_mult___5", "lymph_chain_mult___6", "lymph_size", "lymph_consistency",
        "lymph_mobility", "salivar_which", "salivar_signal", "salivar_side", "salivar_size",
        "salivar_consistency", "salivar_mobility", "neck_tu_side", "neck_tu_size",
        "neck_tu_consistency", "neck_tu_mobility", "neck_tu_pulse", "ex_compl_other", "rx", "eda",
        "biopsy", "bx_date", "tc", "rnm", "paaf", "paaf_other", "paaf_thyroid", "paaf_thy_notes",
        "usg_which", "usg_other", "usg_thyroid", "tirads_1", "composition_points", "tirads_2",
        "echogenicity_points", "tirads_3", "shape_points", "tirads_4", "margin_points",
        "calcification_usg", "calcification_none", "macrocalcification", "rim_calcification",
        "microcalcification", "calcification_points", "tirads_points", "disease_which",
        "thyroid_disease", "thy_disease_other", "type_thy_nodule", "thy_nod_cancer", "hn_site",
        "hn_site_other", "staging_ct_time0", "staging_cn_time0", "staging_cm_time0",
        "staging_clinic_1", "t_melanoma_dx", "c_melanoma_dx", "m_melanoma_dx", "estadio_melanoma_dx",
        "diagnoses", "surgery", "non_operatory_conduct", "non_operatory_other", "palliation",
        "palliation_oher", "tqt_paliativo", "gtt_paliativo", "sne_paliativo", "oral_sex",
        "anal_sex", "vaginal_sex", "sexual_age", "number_sex_partner", "conduct_other"]
    
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


import streamlit as st
import pandas as pd

from scraper import coletar_manchetes
from sentiment import analisar_sentimento
from visualizacoes import (
    grafico_sentimentos,
    grafico_comparativo_portais,
    grafico_quantidade_portais,
    grafico_comparacao_temas,
    timeline_dupla,
    nuvem_palavras,
    timeline_noticias,
    heatmap_portais,
    timeline_por_portal,
    tabela_palavras_por_portal,
)
from ia_resumo import gerar_resumo
from banco import salvar_analise, carregar_historico, carregar_manchetes_por_analise, deletar_analise, ultimos_temas
from utils import logger, CORES

st.set_page_config(
    page_title="Analisador de Manchetes | Enquadramento Midiático",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
    .stApp {{ background: {CORES["fundo"]}; }}

    .navbar {{
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: {CORES["navbar"]};
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid {CORES["borda"]};
        padding: 0.75rem 2rem;
        display: flex; align-items: center; justify-content: center; gap: 0.75rem;
    }}
    .navbar-icon {{ font-size: 1.5rem; }}
    .navbar-title {{ font-size: 1.2rem; font-weight: 700; color: {CORES["texto"]}; letter-spacing: -0.3px; }}
    .navbar-sub {{ font-size: 0.75rem; color: {CORES["accent"]}; font-weight: 400; margin-left: 0.5rem; }}
    .navbar-spacer {{ height: 4rem; }}

    .section-title {{
        font-size: 1.15rem; font-weight: 600; color: {CORES["texto"]};
        margin: 1.75rem 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;
    }}
    .section-title::after {{
        content: ''; flex: 1; height: 1px;
        background: linear-gradient(90deg, {CORES["accent"]}44, transparent);
        margin-left: 0.75rem;
    }}

    .glass {{
        background: {CORES["card"]}; backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid {CORES["borda"]};
        border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }}

    .metric-row {{
        display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem; margin: 1.5rem 0;
    }}
    .metric-card {{
        background: {CORES["card"]}; backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid {CORES["borda"]};
        border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        padding: 1.25rem 1rem; text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .metric-card:hover {{ transform: translateY(-2px); box-shadow: 0 12px 40px rgba(0,0,0,0.35); }}
    .metric-label {{ font-size: 0.7rem; font-weight: 500; color: {CORES["texto_muted"]}; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 0.3rem; }}
    .metric-value {{ font-size: 2rem; font-weight: 800; letter-spacing: -1px; line-height: 1.1; }}
    .metric-sub {{ font-size: 0.72rem; color: {CORES["texto_muted"]}; margin-top: 0.2rem; }}

    .news-card {{
        background: {CORES["card"]}; backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid {CORES["borda"]};
        border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        padding: 1rem 1.25rem; margin-bottom: 0.75rem;
        border-left: 4px solid {CORES["texto_muted"]};
        transition: transform 0.15s, box-shadow 0.15s;
        display: flex; align-items: flex-start; gap: 1rem;
    }}
    .news-card:hover {{ transform: translateX(3px); box-shadow: 0 8px 28px rgba(0,0,0,0.3); }}
    .news-card.border-positivo {{ border-left-color: {CORES["positivo"]}; }}
    .news-card.border-negativo {{ border-left-color: {CORES["negativo"]}; }}
    .news-card.border-neutro {{ border-left-color: {CORES["neutro"]}; }}
    .news-badge {{
        font-size: 0.6rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.8px; padding: 0.2rem 0.6rem; border-radius: 6px;
        white-space: nowrap; flex-shrink: 0;
        background: rgba(255,255,255,0.06); color: {CORES["texto_muted"]};
    }}
    .news-content {{ flex: 1; min-width: 0; }}
    .news-title {{ font-size: 0.9rem; font-weight: 500; color: {CORES["texto"]}; line-height: 1.4; margin-bottom: 0.25rem; }}
    .news-meta {{ font-size: 0.72rem; color: {CORES["texto_muted"]}; display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }}
    .news-link {{ color: {CORES["accent"]}; text-decoration: none; font-weight: 500; transition: opacity 0.15s; }}
    .news-link:hover {{ opacity: 0.7; text-decoration: underline; }}
    .news-tag {{ display: inline-block; font-size: 0.65rem; font-weight: 600; padding: 0.2rem 0.65rem; border-radius: 20px; }}
    .tag-positivo {{ background: {CORES["positivo"]}22; color: {CORES["positivo"]}; }}
    .tag-negativo {{ background: {CORES["negativo"]}22; color: {CORES["negativo"]}; }}
    .tag-neutro {{ background: {CORES["neutro"]}22; color: {CORES["neutro"]}; }}

    section[data-testid="stSidebar"] > div:first-child {{ background: {CORES["fundo"]}; border-right: 1px solid {CORES["borda"]}; }}
    .sidebar-header {{ font-size: 0.85rem; font-weight: 700; color: {CORES["accent"]}; letter-spacing: 0.5px; margin-bottom: 0.25rem; }}
    .sidebar-portal {{ font-size: 0.75rem; color: {CORES["texto_muted"]}; padding: 0.15rem 0; }}
    .sidebar-tema {{ font-size: 0.78rem; color: {CORES["accent"]}; cursor: pointer; padding: 0.15rem 0; transition: opacity 0.15s; }}
    .sidebar-tema:hover {{ opacity: 0.7; }}

    .welcome {{ text-align: center; padding: 5rem 1rem; }}
    .welcome-icon {{ font-size: 4rem; margin-bottom: 1rem; }}
    .welcome-title {{ font-size: 1.5rem; font-weight: 600; color: {CORES["texto"]}; margin-bottom: 0.5rem; }}
    .welcome-sub {{ font-size: 0.9rem; color: {CORES["texto_muted"]}; max-width: 480px; margin: 0 auto 0.5rem; }}
    .welcome-portais {{ font-size: 0.75rem; color: {CORES["texto_muted"]}; opacity: 0.5; }}

    .info-box {{
        background: {CORES["card"]}; backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid {CORES["borda"]};
        border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        padding: 1.25rem;
        border-left: 4px solid {CORES["accent"]};
        color: {CORES["texto"]}; line-height: 1.6; margin: 0.5rem 0;
    }}

    .footer {{
        text-align: center; color: {CORES["texto_muted"]}; font-size: 0.7rem;
        margin-top: 3rem; padding: 1.5rem 0 1rem;
        border-top: 1px solid {CORES["borda"]}; opacity: 0.5;
    }}

    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {CORES["accent"]}, {CORES["accent2"]}) !important;
        border: none !important; color: #0A1628 !important;
        font-weight: 600 !important; border-radius: 10px !important;
        padding: 0.4rem 1.2rem !important;
        transition: transform 0.15s, box-shadow 0.15s !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 20px {CORES["accent"]}44 !important;
    }}
    div[data-testid="stTextInput"] input {{
        background: {CORES["card"]} !important;
        border: 1px solid {CORES["borda"]} !important;
        border-radius: 10px !important;
        color: {CORES["texto"]} !important;
    }}
    div[data-testid="stTextInput"] input:focus {{
        border-color: {CORES["accent"]} !important;
        box-shadow: 0 0 0 2px {CORES["accent"]}22 !important;
    }}
    hr {{ border-color: {CORES["borda"]} !important; }}
    .chart-grid {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;
    }}
    .chart-full {{
        grid-column: 1 / -1;
    }}
    div[data-testid="stVerticalBlock"] > div > div[data-testid="column"] {{
        gap: 1rem;
    }}
    .stPlotlyChart, .stImage, .stPyplot {{
        outline: none;
    }}
    .st-emotion-cache-1y4p8pa {{
        gap: 1rem;
    }}
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] {{ padding-top: 0; }}

    .hist-row {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.75rem 1rem; border-bottom: 1px solid {CORES["borda"]};
        transition: background 0.15s;
    }}
    .hist-row:hover {{ background: rgba(255,255,255,0.03); }}
    .hist-tema {{ font-weight: 600; color: {CORES["texto"]}; }}
    .hist-meta {{ font-size: 0.72rem; color: {CORES["texto_muted"]}; }}
    .hist-toms {{ display: flex; gap: 0.5rem; font-size: 0.75rem; }}
    .hist-actions {{ display: flex; gap: 0.4rem; }}
    .btn-small {{
        font-size: 0.7rem; padding: 0.25rem 0.7rem; border-radius: 8px;
        border: 1px solid {CORES["borda"]}; cursor: pointer;
        background: transparent; color: {CORES["texto_muted"]};
        transition: all 0.15s; font-family: inherit;
    }}
    .btn-small:hover {{ border-color: {CORES["accent"]}; color: {CORES["accent"]}; }}
    .btn-small.danger:hover {{ border-color: {CORES["negativo"]}; color: {CORES["negativo"]}; }}
</style>
""",
    unsafe_allow_html=True,
)

# ── SESSION STATE ──
for key in ["analise_feita", "df_resultado", "manchetes_raw", "tema_atual"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "analise_feita" else (pd.DataFrame() if "df" in key else [] if "raw" in key else "")

for key in ["comp_resultado", "resumo_texto", "resumo_comp_texto",
            "status_gemini", "status_gemini_comp"]:
    if key not in st.session_state:
        st.session_state[key] = False if "resultado" in key else True if "status" in key else ""

if "comp_dados" not in st.session_state:
    st.session_state.comp_dados = {}

# ── NAVBAR ──
st.markdown(
    f'<div class="navbar">'
    f'<span class="navbar-icon">📰</span>'
    f'<span class="navbar-title">Analisador de Manchetes</span>'
    f'<span class="navbar-sub">Enquadramento Midiático · Projeto Acadêmico</span>'
    f"</div>"
    f'<div class="navbar-spacer"></div>',
    unsafe_allow_html=True,
)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(
        f'<div style="text-align:center;margin:.5rem 0 1rem;">'
        f'<div style="font-size:2rem;margin-bottom:.25rem;">📊</div>'
        f'<div class="sidebar-header">Analisador de Manchetes</div>'
        f'<div style="font-size:.65rem;color:{CORES["texto_muted"]};">Coleta · Análise · Visualização</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    tema_input = st.text_input(
        "Tema", placeholder="Ex: Flamengo, Lula, IA...",
        value=st.session_state.tema_atual, label_visibility="collapsed",
    )
    analisar_btn = st.button("Analisar Manchetes", type="primary", use_container_width=True)

    st.markdown(
        f'<div style="font-size:.7rem;font-weight:600;color:{CORES["texto_muted"]};'
        f'text-transform:uppercase;letter-spacing:1px;margin:1.25rem 0 .5rem;">Portais</div>',
        unsafe_allow_html=True,
    )
    for p in ["G1", "CNN Brasil", "UOL", "Folha de S.Paulo", "Estadão"]:
        st.markdown(f'<div class="sidebar-portal">◦ {p}</div>', unsafe_allow_html=True)

    try:
        ts = ultimos_temas(5)
        if ts:
            st.markdown(
                f'<div style="font-size:.7rem;font-weight:600;color:{CORES["texto_muted"]};'
                f'text-transform:uppercase;letter-spacing:1px;margin:1.25rem 0 .5rem;">Últimos temas</div>',
                unsafe_allow_html=True,
            )
            for t in ts:
                st.markdown(f'<div class="sidebar-tema">→ {t}</div>', unsafe_allow_html=True)
    except Exception as e:
        logger.warning(f"Erro ao carregar ultimos temas: {e}")

# ── SEARCH TRIGGER (aba 1) ──
if analisar_btn and tema_input.strip():
    with st.spinner("📡 Coletando manchetes..."):
        logger.info(f"Analise: {tema_input}")
        manchetes = coletar_manchetes(tema_input.strip())
        if not manchetes:
            st.warning("Nenhuma manchete encontrada. Tente outro termo.")
            st.session_state.analise_feita = False
        else:
            for m in manchetes:
                m["tom"] = analisar_sentimento(m["manchete"])
            df = pd.DataFrame(manchetes)[["portal", "manchete", "tom", "data", "link", "horario_coleta"]]
            df.columns = ["Portal", "Manchete", "Tom", "Data", "Link", "Coleta"]
            st.session_state.df_resultado = df
            st.session_state.manchetes_raw = manchetes
            st.session_state.tema_atual = tema_input
            st.session_state.analise_feita = True
            try:
                salvar_analise(tema_input, df)
            except Exception as e:
                logger.warning(f"Erro ao salvar: {e}")
            st.rerun()

# ── TABS ──
tab1, tab2, tab3, tab4 = st.tabs(["📊 Análise Única", "🔍 Comparar Temas", "🏛️ Comparar Portais", "📁 Histórico"])

# ============================================================
# TAB 1 — ANÁLISE ÚNICA
# ============================================================
with tab1:
    if st.session_state.analise_feita:
        df = st.session_state.df_resultado
        manchetes = st.session_state.manchetes_raw
        tema = st.session_state.tema_atual

        total = len(df)
        positivas = len(df[df["Tom"] == "Positivo"])
        negativas = len(df[df["Tom"] == "Negativo"])
        neutras = len(df[df["Tom"] == "Neutro"])
        perc_pos = round(positivas / total * 100) if total else 0
        perc_neg = round(negativas / total * 100) if total else 0

        st.markdown('<div class="metric-row">', unsafe_allow_html=True)
        cols = st.columns(4)
        for i, (label, valor, sub, cor) in enumerate([
            ("Total Manchetes", str(total), f'"{tema}"', CORES["accent"]),
            ("Positivas", str(positivas), f"{perc_pos}%", CORES["positivo"]),
            ("Negativas", str(negativas), f"{perc_neg}%", CORES["negativo"]),
            ("Neutras", str(neutras), "Sem vies claro", CORES["neutro"]),
        ]):
            with cols[i]:
                st.markdown(
                    f'<div class="glass metric-card">'
                    f'<div class="metric-label">{label}</div>'
                    f'<div class="metric-value" style="color:{cor};">{valor}</div>'
                    f'<div class="metric-sub">{sub}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f'<div class="section-title"><span>📋</span> Manchetes Coletadas</div>', unsafe_allow_html=True)
        for _, row in df.iterrows():
            tom = row["Tom"]
            tc = tom.lower()
            link_h = (
                f'<a class="news-link" href="{row["Link"]}" target="_blank">Abrir ↗</a>'
                if row["Link"] and str(row["Link"]).startswith("http") else ""
            )
            st.markdown(
                f'<div class="news-card border-{tc}">'
                f'<div class="news-content">'
                f'<div class="news-title">{row["Manchete"]}</div>'
                f'<div class="news-meta">'
                f'<span class="news-badge">{row["Portal"]}</span>'
                f'<span class="news-tag tag-{tc}">{tom}</span>'
                f'<span>{row["Data"]}</span>{link_h}'
                f"</div></div></div>",
                unsafe_allow_html=True,
            )

        # ── ROW 1: Sentiment + Portal Quantity ──
        st.markdown(
            f'<div class="section-title"><span>📊</span> Análise de Sentimento</div>',
            unsafe_allow_html=True,
        )
        r1a, r1b = st.columns(2)
        with r1a:
            fig1 = grafico_sentimentos(df)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True, key="tab1_sentiment")
        with r1b:
            fig2 = grafico_quantidade_portais(df)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True, key="tab1_portal_qt")

        # ── ROW 2: Portal Comparison + Timeline ──
        st.markdown(
            f'<div class="section-title"><span>🔍📅</span> Comparação entre Portais e Frequência</div>',
            unsafe_allow_html=True,
        )
        r2a, r2b = st.columns(2)
        with r2a:
            fig3 = grafico_comparativo_portais(df)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True, key="tab1_compare")
            else:
                st.info("Poucos dados para comparacao entre portais.")
        with r2b:
            fig5 = timeline_noticias(df)
            if fig5:
                st.plotly_chart(fig5, use_container_width=True, key="tab1_timeline")
            else:
                st.info("Poucos dados para linha do tempo.")

        # ── ROW 3: WordCloud (full width, centered) ──
        st.markdown(
            f'<div class="section-title"><span>☁️</span> Nuvem de Palavras</div>',
            unsafe_allow_html=True,
        )
        fig4 = nuvem_palavras(df)
        if fig4:
            st.pyplot(fig4)
        else:
            st.info("Nao foi possivel gerar a nuvem (poucos dados).")

        st.markdown(f'<div class="section-title"><span>🤖</span> Resumo das Manchetes</div>', unsafe_allow_html=True)
        if st.button("✨ Gerar Resumo", type="primary", key="resumo_tab1"):
            with st.spinner("Analisando manchetes..."):
                resumo, ok = gerar_resumo(manchetes)
                st.session_state.resumo_texto = resumo
                st.session_state.status_gemini = ok
            st.rerun()
        if st.session_state.get("resumo_texto"):
            if not st.session_state.get("status_gemini", True):
                st.info("⚠️ Cota da API Gemini excedida — resumo gerado localmente.")
            st.markdown(f'<div class="info-box">{st.session_state.resumo_texto}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="welcome">'
            f'<div class="welcome-icon">📰</div>'
            f'<div class="welcome-title">Bem-vindo ao Analisador de Manchetes</div>'
            f'<div class="welcome-sub">'
            f'Digite um tema na barra lateral e clique em '
            f'<strong style="color:{CORES["accent"]};">Analisar Manchetes</strong>.'
            f"</div>"
            f'<div class="welcome-portais">G1 · CNN Brasil · UOL · Folha de S.Paulo · Estadão</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

# ============================================================
# TAB 2 — COMPARAR TEMAS
# ============================================================
with tab2:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;">'
        f'<span style="display:flex;align-items:center;gap:0.4rem;">'
        f'<span style="color:{CORES["accent"]};font-weight:700;">Tema A</span>'
        f'<span style="color:{CORES["accent"]};font-size:0.7rem;">●</span>'
        f"</span>"
        f'<div style="flex:1;min-width:180px;">',
        unsafe_allow_html=True,
    )
    tema_a = st.text_input("Tema A", placeholder="Ex: Lula", key="comp_a", label_visibility="collapsed")
    st.markdown(
        f"</div>"
        f'<span style="color:{CORES["texto_muted"]};">vs</span>'
        f'<span style="display:flex;align-items:center;gap:0.4rem;">'
        f'<span style="color:{CORES["tema_b"]};font-weight:700;">Tema B</span>'
        f'<span style="color:{CORES["tema_b"]};font-size:0.7rem;">●</span>'
        f"</span>"
        f'<div style="flex:1;min-width:180px;">',
        unsafe_allow_html=True,
    )
    tema_b = st.text_input("Tema B", placeholder="Ex: Bolsonaro", key="comp_b", label_visibility="collapsed")
    st.markdown(
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    comp_btn = st.button("🔍 Comparar Temas", type="primary", use_container_width=True)

    if comp_btn and tema_a.strip() and tema_b.strip():
        try:
            with st.status("Coletando dados..."):
                st.write(f"Buscando **{tema_a}**...")
                m_a = coletar_manchetes(tema_a.strip())
                if m_a:
                    for m in m_a: m["tom"] = analisar_sentimento(m["manchete"])
                    df_a = pd.DataFrame(m_a)[["portal", "manchete", "tom", "data", "link", "horario_coleta"]]
                    df_a.columns = ["Portal", "Manchete", "Tom", "Data", "Link", "Coleta"]
                else:
                    st.warning(f"Nenhum resultado para '{tema_a}'")
                    df_a = pd.DataFrame()

                st.write(f"Buscando **{tema_b}**...")
                m_b = coletar_manchetes(tema_b.strip())
                if m_b:
                    for m in m_b: m["tom"] = analisar_sentimento(m["manchete"])
                    df_b = pd.DataFrame(m_b)[["portal", "manchete", "tom", "data", "link", "horario_coleta"]]
                    df_b.columns = ["Portal", "Manchete", "Tom", "Data", "Link", "Coleta"]
                else:
                    st.warning(f"Nenhum resultado para '{tema_b}'")
                    df_b = pd.DataFrame()

            st.session_state.comp_dados = {"a": df_a, "b": df_b, "nome_a": tema_a.strip(), "nome_b": tema_b.strip()}
            st.session_state.comp_resultado = True
        except Exception as e:
            st.error(f"Erro ao coletar dados: {e}")
        st.rerun()

    if st.session_state.comp_resultado:
        d = st.session_state.comp_dados
        df_a = d["a"]
        df_b = d["b"]
        nome_a = d["nome_a"]
        nome_b = d["nome_b"]

        if df_a.empty and df_b.empty:
            st.warning("Nenhum resultado para ambos os temas.")
        else:
            # — metrics —
            def _metricas(df):
                t = len(df)
                p = len(df[df["Tom"] == "Positivo"]) if "Tom" in df.columns else 0
                n = len(df[df["Tom"] == "Negativo"]) if "Tom" in df.columns else 0
                neu = len(df[df["Tom"] == "Neutro"]) if "Tom" in df.columns else 0
                return t, p, n, neu

            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin:1rem 0;">',
                unsafe_allow_html=True,
            )
            for df_x, nome_x, cor_x in [(df_a, nome_a, CORES["accent"]), (df_b, nome_b, CORES["tema_b"])]:
                t, p, n, neu = _metricas(df_x)
                st.markdown(
                    f'<div class="glass" style="padding:1rem;">'
                    f'<div style="font-size:1rem;font-weight:700;color:{cor_x};margin-bottom:0.75rem;'
                    f'display:flex;align-items:center;gap:0.5rem;">'
                    f'<span style="font-size:0.6rem;">●</span>{nome_x}</div>'
                    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">'
                    f'<div><div class="metric-label">Total</div><div class="metric-value" style="font-size:1.5rem;color:{cor_x};">{t}</div></div>'
                    f'<div><div class="metric-label">Pos</div><div class="metric-value" style="font-size:1.5rem;color:{CORES["positivo"]};">{p}</div></div>'
                    f'<div><div class="metric-label">Neg</div><div class="metric-value" style="font-size:1.5rem;color:{CORES["negativo"]};">{n}</div></div>'
                    f'<div><div class="metric-label">Neu</div><div class="metric-value" style="font-size:1.5rem;color:{CORES["neutro"]};">{neu}</div></div>'
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

            # ── ROW 1: Comparison chart + Dual timeline ──
            st.markdown(
                f'<div class="section-title"><span>📊📅</span> Sentimento e Frequência</div>',
                unsafe_allow_html=True,
            )
            comp_row_a, comp_row_b = st.columns(2)
            with comp_row_a:
                fig_comp = grafico_comparacao_temas(df_a, df_b, nome_a, nome_b)
                if fig_comp:
                    st.plotly_chart(fig_comp, use_container_width=True, key="comp_chart")
            with comp_row_b:
                fig_tl = timeline_dupla(df_a, df_b, nome_a, nome_b)
                if fig_tl:
                    st.plotly_chart(fig_tl, use_container_width=True, key="timeline_chart")

            # ── ROW 2: Portal charts side by side ──
            st.markdown(
                f'<div class="section-title"><span>🏛️</span> Manchetes por Portal</div>',
                unsafe_allow_html=True,
            )
            cp_a, cp_b = st.columns(2)
            with cp_a:
                st.markdown(
                    f'<div style="font-size:0.85rem;font-weight:600;color:{CORES["accent"]};'
                    f'margin-bottom:0.5rem;">{nome_a}</div>',
                    unsafe_allow_html=True,
                )
                if not df_a.empty:
                    fig_pa = grafico_quantidade_portais(df_a)
                    if fig_pa:
                        st.plotly_chart(fig_pa, use_container_width=True, key="portal_a_chart")
                else:
                    st.info("Sem dados")
            with cp_b:
                st.markdown(
                    f'<div style="font-size:0.85rem;font-weight:600;color:{CORES["tema_b"]};'
                    f'margin-bottom:0.5rem;">{nome_b}</div>',
                    unsafe_allow_html=True,
                )
                if not df_b.empty:
                    fig_pb = grafico_quantidade_portais(df_b)
                    if fig_pb:
                        st.plotly_chart(fig_pb, use_container_width=True, key="portal_b_chart")
                else:
                    st.info("Sem dados")

            # ── ROW 3: Wordclouds side by side ──
            st.markdown(
                f'<div class="section-title"><span>☁️</span> Nuvens de Palavras</div>',
                unsafe_allow_html=True,
            )
            wc_a, wc_b = st.columns(2)
            with wc_a:
                st.markdown(
                    f'<div style="font-size:0.85rem;font-weight:600;color:{CORES["accent"]};'
                    f'margin-bottom:0.5rem;text-align:center;">{nome_a}</div>',
                    unsafe_allow_html=True,
                )
                if not df_a.empty:
                    fig_wc_a = nuvem_palavras(df_a)
                    if fig_wc_a:
                        st.pyplot(fig_wc_a)
            with wc_b:
                st.markdown(
                    f'<div style="font-size:0.85rem;font-weight:600;color:{CORES["tema_b"]};'
                    f'margin-bottom:0.5rem;text-align:center;">{nome_b}</div>',
                    unsafe_allow_html=True,
                )
                if not df_b.empty:
                    fig_wc_b = nuvem_palavras(df_b)
                    if fig_wc_b:
                        st.pyplot(fig_wc_b)
            # — summary —
            st.markdown(f'<div class="section-title"><span>🤖</span> Resumo Comparativo</div>', unsafe_allow_html=True)
            stub_a = []
            for _, r in (df_a if not df_a.empty else pd.DataFrame()).iterrows():
                stub_a.append({"portal": r["Portal"], "manchete": r["Manchete"], "tom": r["Tom"]})
            stub_b = []
            for _, r in (df_b if not df_b.empty else pd.DataFrame()).iterrows():
                stub_b.append({"portal": r["Portal"], "manchete": r["Manchete"], "tom": r["Tom"]})

            if stub_a or stub_b:
                if st.button("✨ Gerar Resumo Comparativo", type="primary", key="resumo_tab2"):
                    with st.spinner("Analisando..."):
                        resumo_texto, ok = gerar_resumo(stub_a + stub_b)
                        ta, pa, na, neua = _metricas(df_a)
                        tb, pb, nb, neub = _metricas(df_b)
                        extra = (
                            f"\n\n**Resumo da comparação:** O tema **{nome_a}** gerou {ta} manchetes "
                            f"({pa} positivas, {na} negativas), enquanto **{nome_b}** gerou {tb} "
                            f"({pb} positivas, {nb} negativas)."
                        )
                        st.session_state.resumo_comp_texto = resumo_texto + extra
                        st.session_state.status_gemini_comp = ok
                    st.rerun()
                if st.session_state.get("resumo_comp_texto"):
                    if not st.session_state.get("status_gemini_comp", True):
                        st.info("⚠️ Cota da API Gemini excedida — resumo gerado localmente.")
                    st.markdown(f'<div class="info-box">{st.session_state.resumo_comp_texto}</div>', unsafe_allow_html=True)

# ============================================================
# TAB 3 — COMPARAR PORTAIS
# ============================================================
with tab3:
    if not st.session_state.analise_feita:
        st.markdown(
            f'<div class="welcome">'
            f'<div class="welcome-icon">🏛️</div>'
            f'<div class="welcome-title">Compare os Portais</div>'
            f'<div class="welcome-sub">'
            f"Faça uma análise na aba "
            f'<strong style="color:{CORES["accent"]};">Análise Única</strong> '
            f"primeiro para ver a comparação detalhada entre portais."
            f"</div></div>",
            unsafe_allow_html=True,
        )
    else:
        df = st.session_state.df_resultado
        manchetes = st.session_state.manchetes_raw
        tema = st.session_state.tema_atual

        portais_disponiveis = sorted(df["Portal"].unique().tolist())
        padrao = portais_disponiveis[:]

        st.markdown(
            f'<div class="section-title"><span>🏛️</span> Comparação entre Portais: "{tema}"</div>',
            unsafe_allow_html=True,
        )

        selecionados = st.multiselect(
            "Selecione os portais para comparar",
            options=portais_disponiveis,
            default=padrao,
            label_visibility="collapsed",
        )

        if not selecionados:
            st.info("Selecione ao menos um portal.")
        else:
            df_filtrado = df[df["Portal"].isin(selecionados)]

            # ── Tabela de métricas ──
            st.markdown(
                f'<div style="font-size:0.9rem;font-weight:600;color:{CORES["texto"]};'
                f'margin:1rem 0 0.5rem;">📊 Métricas por Portal</div>',
                unsafe_allow_html=True,
            )

            linhas_metricas = []
            for portal in selecionados:
                dp = df_filtrado[df_filtrado["Portal"] == portal]
                t = len(dp)
                p = len(dp[dp["Tom"] == "Positivo"])
                n = len(dp[dp["Tom"] == "Negativo"])
                neu = len(dp[dp["Tom"] == "Neutro"])
                perc_p = round(p / t * 100) if t else 0
                perc_n = round(n / t * 100) if t else 0
                linhas_metricas.append(
                    f"<tr style='border-bottom:1px solid {CORES['borda']};'>"
                    f"<td style='padding:0.6rem 0.8rem;font-weight:600;color:{CORES['texto']};'>{portal}</td>"
                    f"<td style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['accent']};'>{t}</td>"
                    f"<td style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['positivo']};'>{p}</td>"
                    f"<td style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['negativo']};'>{n}</td>"
                    f"<td style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['neutro']};'>{neu}</td>"
                    f"<td style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['positivo']};'>{perc_p}%</td>"
                    f"<td style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['negativo']};'>{perc_n}%</td>"
                    f"</tr>"
                )

            st.markdown(
                f'<div class="glass" style="overflow-x:auto;padding:0.5rem;">'
                f'<table style="width:100%;border-collapse:collapse;font-size:0.85rem;">'
                f"<thead>"
                f"<tr style='border-bottom:2px solid {CORES['accent']}44;'>"
                f"<th style='padding:0.6rem 0.8rem;text-align:left;color:{CORES['texto_muted']};font-weight:600;'>Portal</th>"
                f"<th style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['texto_muted']};font-weight:600;'>Total</th>"
                f"<th style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['texto_muted']};font-weight:600;'>Pos</th>"
                f"<th style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['texto_muted']};font-weight:600;'>Neg</th>"
                f"<th style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['texto_muted']};font-weight:600;'>Neu</th>"
                f"<th style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['texto_muted']};font-weight:600;'>% Pos</th>"
                f"<th style='padding:0.6rem 0.8rem;text-align:center;color:{CORES['texto_muted']};font-weight:600;'>% Neg</th>"
                f"</tr>"
                f"</thead>"
                f"<tbody>{''.join(linhas_metricas)}</tbody>"
                f"</table></div>",
                unsafe_allow_html=True,
            )

            # ── Heatmap ──
            st.markdown(
                f'<div class="section-title"><span>🔥</span> Mapa de Calor (Portal × Sentimento)</div>',
                unsafe_allow_html=True,
            )
            fig_heat = heatmap_portais(df_filtrado)
            if fig_heat:
                st.plotly_chart(fig_heat, use_container_width=True, key="tab4_heatmap")

            # ── Timeline por portal + Palavras lado a lado ──
            st.markdown(
                f'<div class="section-title"><span>📅🔤</span> Frequência e Palavras-chave</div>',
                unsafe_allow_html=True,
            )
            tl_col, pa_col = st.columns(2)
            with tl_col:
                fig_tl_p = timeline_por_portal(df_filtrado)
                if fig_tl_p:
                    st.plotly_chart(fig_tl_p, use_container_width=True, key="tab4_timeline")
                else:
                    st.info("Poucos dados para timeline.")
            with pa_col:
                fig_pal = tabela_palavras_por_portal(df_filtrado)
                if fig_pal:
                    st.plotly_chart(fig_pal, use_container_width=True, key="tab4_keywords")
                else:
                    st.info("Poucos dados para palavras-chave.")

# ============================================================
# TAB 4 — HISTÓRICO
# ============================================================
with tab4:
    st.markdown(f'<div class="section-title"><span>📁</span> Histórico de Análises</div>', unsafe_allow_html=True)

    try:
        hist = carregar_historico()
    except Exception as e:
        logger.warning(f"Erro ao carregar historico: {e}")
        hist = pd.DataFrame()

    if hist.empty:
        st.markdown(
            f'<div style="text-align:center;padding:3rem 1rem;color:{CORES["texto_muted"]};">'
            f'<div style="font-size:3rem;margin-bottom:0.5rem;">📭</div>'
            f"<div>Nenhuma análise encontrada. Faça sua primeira análise na aba "
            f'<strong style="color:{CORES["accent"]};">Análise Única</strong>.'
            f"</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="glass" style="padding:0.75rem 1rem;margin-bottom:1rem;display:flex;'
            f'align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">'
            f'<span style="font-size:0.9rem;color:{CORES["texto"]};">'
            f'Total de <strong>{len(hist)}</strong> análise(s) registrada(s).</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

        for _, row in hist.iterrows():
            aid = row["id"]
            st.markdown(
                f'<div class="hist-row glass" style="margin-bottom:0.5rem;">'
                f'<div style="flex:1;min-width:0;">'
                f'<div class="hist-tema">{row["tema"]}</div>'
                f'<div class="hist-meta">{row["data_analise"]} · {row["total_manchetes"]} manchetes</div>'
                f"</div>"
                f'<div class="hist-toms">'
                f'<span style="color:{CORES["positivo"]};">+{row["positivas"]}</span>'
                f'<span style="color:{CORES["negativo"]};">-{row["negativas"]}</span>'
                f'<span style="color:{CORES["neutro"]};">~{row["neutras"]}</span>'
                f"</div>"
                f'<div class="hist-actions">',
                unsafe_allow_html=True,
            )

            col_a1, col_a2 = st.columns([1, 1])
            with col_a1:
                if st.button("📂 Carregar", key=f"load_{aid}"):
                    df_hist = carregar_manchetes_por_analise(aid)
                    if not df_hist.empty:
                        df_hist.columns = ["id", "analise_id", "Portal", "Manchete", "Tom", "Data", "Link", "Coleta"]
                        raw = df_hist.to_dict("records")
                        st.session_state.df_resultado = df_hist
                        st.session_state.manchetes_raw = raw
                        st.session_state.tema_atual = row["tema"]
                        st.session_state.analise_feita = True
                        st.rerun()
            with col_a2:
                if st.button("🗑️ Excluir", key=f"del_{aid}"):
                    deletar_analise(aid)
                    st.rerun()

            st.markdown(f"</div></div>", unsafe_allow_html=True)

import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
from utils import CORES, extrair_palavras, logger

_CORES_GRAFICO = [
    "#00D4FF", "#0088FF", "#00E676", "#FFD740", "#FF5252",
]

_CORES_PORTAIS = [
    "#00D4FF", "#7C4DFF", "#00E676", "#FFD740", "#FF6D00",
]


def _config_layout(fig, titulo):
    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(size=16, color=CORES["texto"], family="Inter, sans-serif"),
            x=0.5,
            y=0.95,
        ),
        plot_bgcolor=CORES["fundo"],
        paper_bgcolor=CORES["card_solid"],
        font=dict(color=CORES["texto"], family="Inter, sans-serif"),
        xaxis=dict(
            showgrid=False,
            title=dict(font=dict(size=13, color=CORES["texto_muted"])),
            tickfont=dict(size=12, color=CORES["texto_muted"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            title=dict(font=dict(size=13, color=CORES["texto_muted"])),
            tickfont=dict(size=12, color=CORES["texto_muted"]),
        ),
        hoverlabel=dict(
            bgcolor=CORES["card_solid"],
            font=dict(color=CORES["texto"], size=13),
            bordercolor=CORES["accent"],
        ),
        margin=dict(l=50, r=50, t=60, b=50),
        legend=dict(
            font=dict(color=CORES["texto"], size=12),
            bgcolor="rgba(0,0,0,0.2)",
        ),
    )
    return fig


def grafico_sentimentos(df):
    if df.empty:
        return None

    contagem = df["Tom"].value_counts().reindex(
        ["Positivo", "Negativo", "Neutro"], fill_value=0
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=contagem.index,
        y=contagem.values,
        marker_color=[CORES["positivo"], CORES["negativo"], CORES["neutro"]],
        text=contagem.values,
        textposition="outside",
        textfont=dict(size=15, color=CORES["texto"]),
        hovertemplate="<b>%{x}</b>: %{y}<extra></extra>",
    ))
    fig.update_yaxes(range=[0, max(contagem.values) * 1.25 or 5])
    fig = _config_layout(fig, "Distribuição de Sentimento")
    return fig


def grafico_comparativo_portais(df):
    if df.empty:
        return None

    pivot = pd.crosstab(df["Portal"], df["Tom"])
    for col in ["Positivo", "Negativo", "Neutro"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot[["Positivo", "Negativo", "Neutro"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Positivo",
        x=pivot.index,
        y=pivot["Positivo"],
        marker_color=CORES["positivo"],
        text=pivot["Positivo"],
        textposition="inside",
        hovertemplate="<b>%{x}</b><br>Positivo: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Negativo",
        x=pivot.index,
        y=pivot["Negativo"],
        marker_color=CORES["negativo"],
        text=pivot["Negativo"],
        textposition="inside",
        hovertemplate="<b>%{x}</b><br>Negativo: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Neutro",
        x=pivot.index,
        y=pivot["Neutro"],
        marker_color=CORES["neutro"],
        text=pivot["Neutro"],
        textposition="inside",
        hovertemplate="<b>%{x}</b><br>Neutro: %{y}<extra></extra>",
    ))
    fig.update_layout(barmode="group", bargap=0.2)
    fig = _config_layout(fig, "Tom por Portal")
    return fig


def nuvem_palavras(df):
    if df.empty:
        return None

    todas_palavras = []
    for manchete in df["Manchete"]:
        todas_palavras.extend(extrair_palavras(manchete))

    if not todas_palavras:
        return None

    freq = Counter(todas_palavras)

    wc = WordCloud(
        width=800,
        height=400,
        background_color="#0A1628",
        colormap="Blues",
        max_words=70,
        max_font_size=110,
        min_font_size=12,
        relative_scaling=0.4,
        prefer_horizontal=0.7,
        collocations=False,
        color_func=lambda word, **_: (
            "#00D4FF" if word and word[0] < "m"
            else "#0088FF" if word and word[0] < "s"
            else "#00E676"
        ),
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_facecolor("#0A1628")
    plt.tight_layout(pad=0)
    return fig


def timeline_noticias(df):
    if df.empty:
        return None

    df_temp = df.copy()
    df_temp["contagem"] = 1
    df_temp["Data"] = pd.to_datetime(df_temp["Data"], dayfirst=True, errors="coerce")
    df_temp = df_temp.dropna(subset=["Data"])

    if df_temp.empty:
        return None

    timeline = df_temp.set_index("Data").resample("D").count()["contagem"].reset_index()
    timeline.columns = ["Data", "quantidade"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline["Data"],
        y=timeline["quantidade"],
        mode="lines+markers",
        line=dict(color=CORES["accent"], width=2.5),
        marker=dict(
            size=10,
            color=CORES["accent"],
            line=dict(color=CORES["fundo"], width=2),
        ),
        fill="tozeroy",
        fillcolor=f"rgba(0, 212, 255, 0.12)",
        hovertemplate="<b>%{x|%d/%m}</b>: %{y} manchetes<extra></extra>",
    ))
    fig = _config_layout(fig, "Frequência de Publicações")
    return fig


def grafico_quantidade_portais(df):
    if df.empty:
        return None

    contagem = df["Portal"].value_counts().reset_index()
    contagem.columns = ["Portal", "quantidade"]

    cores = _CORES_PORTAIS[: len(contagem)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=contagem["Portal"],
        y=contagem["quantidade"],
        marker_color=cores,
        text=contagem["quantidade"],
        textposition="outside",
        textfont=dict(size=14, color=CORES["texto"]),
        hovertemplate="<b>%{x}</b>: %{y} manchetes<extra></extra>",
    ))
    fig.update_yaxes(range=[0, max(contagem["quantidade"]) * 1.3 or 5])
    fig = _config_layout(fig, "Manchetes por Portal")
    return fig


def grafico_comparacao_temas(df_a, df_b, nome_a, nome_b):
    if df_a.empty and df_b.empty:
        return None

    cor_a = CORES["accent"]
    cor_b = CORES["tema_b"]

    fig = go.Figure()

    for tom in ["Positivo", "Negativo", "Neutro"]:
        val_a = len(df_a[df_a["Tom"] == tom]) if not df_a.empty else 0
        val_b = len(df_b[df_b["Tom"] == tom]) if not df_b.empty else 0
        fig.add_trace(go.Bar(
            name=tom,
            x=[nome_a, nome_b],
            y=[val_a, val_b],
            marker_color=(
                CORES["positivo"] if tom == "Positivo"
                else CORES["negativo"] if tom == "Negativo"
                else CORES["neutro"]
            ),
            text=[val_a, val_b],
            textposition="inside",
            legendgroup=tom,
            hovertemplate="<b>%{x}</b><br>%{legendgroup}: %{y}<extra></extra>",
        ))

    fig.update_layout(barmode="group", bargap=0.15)
    fig = _config_layout(fig, "Comparação de Sentimento entre Temas")
    fig.update_xaxes(title="")
    return fig


def timeline_dupla(df_a, df_b, nome_a, nome_b):
    if df_a.empty and df_b.empty:
        return None

    cor_a = CORES["accent"]
    cor_b = CORES["tema_b"]

    fig = go.Figure()

    def _add_timeline(df, nome, cor):
        if df.empty:
            return
        df_temp = df.copy()
        df_temp["c"] = 1
        data_col = "Data" if "Data" in df_temp.columns else "data"
        df_temp[data_col] = pd.to_datetime(df_temp[data_col], dayfirst=True, errors="coerce")
        df_temp = df_temp.dropna(subset=[data_col])
        if df_temp.empty:
            return
        tl = df_temp.set_index(data_col).resample("D").count()["c"].reset_index()
        tl.columns = [data_col, "qtd"]
        fig.add_trace(go.Scatter(
            x=tl[data_col],
            y=tl["qtd"],
            mode="lines+markers",
            name=nome,
            line=dict(color=cor, width=2.5),
            marker=dict(size=9, color=cor, line=dict(color=CORES["fundo"], width=2)),
            hovertemplate=f"<b>%{{x|%d/%m}}</b><br>{nome}: %{{y}}<extra></extra>",
        ))

    _add_timeline(df_a, nome_a, cor_a)
    _add_timeline(df_b, nome_b, cor_b)
    fig = _config_layout(fig, "Linha do Tempo Comparativa")
    return fig


def heatmap_portais(df):
    if df.empty or "Portal" not in df.columns or "Tom" not in df.columns:
        return None

    pivot = pd.crosstab(df["Portal"], df["Tom"])
    for col in ["Positivo", "Negativo", "Neutro"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot[["Positivo", "Negativo", "Neutro"]]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[
            [0, CORES["negativo"]],
            [0.5, "#2A2A4A"],
            [1, CORES["positivo"]],
        ],
        text=pivot.values,
        texttemplate="%{text}",
        textfont=dict(size=14, color=CORES["texto"]),
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> · %{x}: %{z}<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(title="", side="bottom"),
        yaxis=dict(title="", autorange="reversed"),
    )
    fig = _config_layout(fig, "Intensidade de Sentimento por Portal")
    fig.update_yaxes(autorange="reversed")
    return fig


def timeline_por_portal(df):
    if df.empty:
        return None

    fig = go.Figure()
    portais = df["Portal"].unique()
    cores_portais = ["#00D4FF", "#FF6D00", "#00E676", "#FFD740", "#FF5252"]

    for i, portal in enumerate(portais):
        df_p = df[df["Portal"] == portal].copy()
        df_p["c"] = 1
        data_col = "Data" if "Data" in df_p.columns else "data"
        df_p[data_col] = pd.to_datetime(df_p[data_col], dayfirst=True, errors="coerce")
        df_p = df_p.dropna(subset=[data_col])
        if df_p.empty:
            continue
        tl = df_p.set_index(data_col).resample("D").count()["c"].reset_index()
        tl.columns = [data_col, "qtd"]
        cor = cores_portais[i % len(cores_portais)]
        fig.add_trace(go.Scatter(
            x=tl[data_col],
            y=tl["qtd"],
            mode="lines+markers",
            name=portal,
            line=dict(color=cor, width=2),
            marker=dict(size=7, color=cor, line=dict(color=CORES["fundo"], width=1.5)),
            hovertemplate=f"<b>%{{x|%d/%m}}</b><br>{portal}: %{{y}}<extra></extra>",
        ))

    if not fig.data:
        return None
    fig = _config_layout(fig, "Frequência por Portal ao Longo do Tempo")
    return fig


def tabela_palavras_por_portal(df, top_n=5):
    if df.empty:
        return None

    portais = df["Portal"].unique()
    resultado = {}
    for portal in portais:
        textos = df[df["Portal"] == portal]["Manchete"].tolist()
        palavras = []
        for t in textos:
            palavras.extend(extrair_palavras(t))
        freq = Counter(palavras)
        tops = [w for w, _ in freq.most_common(top_n)]
        resultado[portal] = tops

    fig = go.Figure()
    fig.update_layout(
        title=dict(
            text="Palavras mais Frequentes por Portal",
            font=dict(size=16, color=CORES["texto"], family="Inter, sans-serif"),
            x=0.5,
        ),
        plot_bgcolor=CORES["fundo"],
        paper_bgcolor=CORES["card_solid"],
        font=dict(color=CORES["texto"], family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=60, b=20),
    )

    muted = CORES["texto_muted"]
    for i, (portal, palavras) in enumerate(resultado.items()):
        texto = " · ".join(palavras) if palavras else "(sem dados)"
        cor = ["#00D4FF", "#FF6D00", "#00E676", "#FFD740", "#FF5252"][i % 5]
        fig.add_annotation(
            x=0.5,
            y=1.0 - (i * 0.18) - 0.1,
            xref="paper",
            yref="paper",
            text=(f"<b style='color:{cor};font-size:14px;'>{portal}</b><br>"
                  f"<span style='color:{muted};font-size:13px;'>{texto}</span>"),
            showarrow=False,
            align="center",
            xanchor="center",
            yanchor="middle",
        )

    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=False, visible=False)
    fig.update_layout(height=60 + len(resultado) * 100)
    return fig

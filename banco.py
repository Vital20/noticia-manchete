import sqlite3
from pathlib import Path
import pandas as pd
from datetime import datetime
from utils import log

DB_PATH = str(Path(__file__).parent / "noticias.db")


def _conectar():
    return sqlite3.connect(DB_PATH)


def criar_tabelas():
    conn = _conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema TEXT NOT NULL,
            total_manchetes INTEGER,
            positivas INTEGER,
            negativas INTEGER,
            neutras INTEGER,
            data_analise TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manchetes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analise_id INTEGER,
            portal TEXT NOT NULL,
            manchete TEXT NOT NULL,
            tom TEXT,
            data TEXT,
            link TEXT,
            horario_coleta TEXT,
            FOREIGN KEY (analise_id) REFERENCES analises (id)
        )
    """)
    conn.commit()
    conn.close()


def _val(row, *keys, default=""):
    for k in keys:
        v = row.get(k)
        if v is not None and not (isinstance(v, float) and pd.isna(v)):
            return v
    return default


def salvar_analise(tema, df):
    criar_tabelas()
    conn = _conectar()
    cursor = conn.cursor()

    if df.empty:
        return None

    tom_col = "Tom" if "Tom" in df.columns else "tom"
    portal_col = "Portal" if "Portal" in df.columns else "portal"
    manchete_col = "Manchete" if "Manchete" in df.columns else "manchete"
    data_col = "Data" if "Data" in df.columns else "data"
    link_col = "Link" if "Link" in df.columns else "link"
    coleta_col = "Coleta" if "Coleta" in df.columns else "horario_coleta"

    positivas = len(df[df[tom_col] == "Positivo"])
    negativas = len(df[df[tom_col] == "Negativo"])
    neutras = len(df[df[tom_col] == "Neutro"])

    data_analise = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO analises (tema, total_manchetes, positivas, negativas, neutras, data_analise)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tema, len(df), positivas, negativas, neutras, data_analise))
    analise_id = cursor.lastrowid

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO manchetes (analise_id, portal, manchete, tom, data, link, horario_coleta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            analise_id,
            _val(row, portal_col, "portal"),
            _val(row, manchete_col, "manchete"),
            _val(row, tom_col, "tom", default="Neutro"),
            _val(row, data_col, "data"),
            _val(row, link_col, "link"),
            _val(row, coleta_col, "horario_coleta"),
        ))

    conn.commit()
    conn.close()
    log(f"Analise salva no banco (ID: {analise_id})")
    return analise_id


def carregar_historico():
    conn = _conectar()
    df = pd.read_sql_query(
        "SELECT * FROM analises ORDER BY data_analise DESC LIMIT 50", conn
    )
    conn.close()
    return df


def carregar_manchetes_por_analise(analise_id):
    conn = _conectar()
    df = pd.read_sql_query(
        "SELECT * FROM manchetes WHERE analise_id = ? ORDER BY data DESC",
        conn,
        params=(analise_id,),
    )
    conn.close()
    return df


def deletar_analise(analise_id):
    conn = _conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM manchetes WHERE analise_id = ?", (analise_id,))
    cursor.execute("DELETE FROM analises WHERE id = ?", (analise_id,))
    conn.commit()
    conn.close()
    log(f"Analise {analise_id} deletada")


def ultimos_temas(limite=5):
    conn = _conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT tema FROM analises ORDER BY id DESC LIMIT ?",
        (limite,)
    )
    temas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return temas


# Garantir que as tabelas existam ao importar o modulo
criar_tabelas()

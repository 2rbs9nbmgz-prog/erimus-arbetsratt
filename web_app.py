#!/usr/bin/env python3
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

ERIMUS_LOGO_B64 = "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"

# ============================================================================
# OPTIMERINGAR FÖR SNABBARE WAKE-UP
# ============================================================================

st.set_page_config(
    page_title="Erimus AB – Rättsfallsdatabas i arbetsrätt",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar öppen direkt
)

# Minimal CSS - laddar snabbare
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500&family=Montserrat:wght@300;400&display=swap');
.stApp { background-color: #deeaf4; }
.erimus-header {
    background-color: #deeaf4; padding: 18px 32px 12px 32px;
    border-bottom: 1px solid #a8c4dc;
    display: flex; align-items: center; justify-content: space-between;
}
.erimus-logo img { height: 50px; width: auto; }
.erimus-title-block { flex: 1; text-align: right; }
.erimus-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.55rem; font-weight: 500; color: #1a4a72;
    letter-spacing: 0.04em; margin: 0;
}
.erimus-subtitle {
    font-family: 'Montserrat', sans-serif; font-size: 0.7rem;
    color: #3a6a92; letter-spacing: 0.14em; text-transform: uppercase;
}
section[data-testid="stSidebar"] { background-color: #c8daea !important; }
.stButton > button {
    background-color: #1a4a72 !important; color: #deeaf4 !important;
    font-family: 'Montserrat', sans-serif !important;
}
.stButton > button:hover { background-color: #3a6a92 !important; }
</style>
"""

# Cachad databaskoppling - snabbare wake-up
@st.cache_resource
def get_connection():
    conn = sqlite3.connect('arbetsratt_rattsfall.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Cachad statistik - färre queries
@st.cache_data(ttl=3600)  # Cache i 1 timme
def hamta_statistik(conn):
    totalt = conn.execute("SELECT COUNT(*) as n FROM rattsfall").fetchone()['n']
    per_lagomrade = conn.execute(
        "SELECT lagomrade, COUNT(*) as antal FROM rattsfall GROUP BY lagomrade"
    ).fetchall()
    per_ar = conn.execute(
        "SELECT strftime('%Y', avgorande_datum) as ar, COUNT(*) as antal "
        "FROM rattsfall GROUP BY ar ORDER BY ar DESC"
    ).fetchall()
    return {
        'totalt': totalt,
        'per_lagomrade': per_lagomrade,
        'per_ar': per_ar
    }

# Cachade filter-alternativ
@st.cache_data(ttl=3600)
def hamta_filter_alternativ(_conn):
    lagomraden = _conn.execute(
        "SELECT DISTINCT lagomrade FROM rattsfall ORDER BY lagomrade"
    ).fetchall()
    teman = _conn.execute(
        "SELECT DISTINCT tema FROM teman ORDER BY tema"
    ).fetchall()
    ar = _conn.execute(
        "SELECT DISTINCT strftime('%Y', avgorande_datum) as ar FROM rattsfall ORDER BY ar DESC"
    ).fetchall()
    return {
        'lagomraden': [r['lagomrade'] for r in lagomraden],
        'teman': [r['tema'] for r in teman],
        'ar': [int(r['ar']) for r in ar if r['ar']]
    }

def senaste_datum(conn):
    row = conn.execute("SELECT MAX(avgorande_datum) as s FROM rattsfall").fetchone()
    if row and row['s']:
        try:
            d = datetime.strptime(row['s'], '%Y-%m-%d')
            sv = {
                'January':'januari','February':'februari','March':'mars',
                'April':'april','May':'maj','June':'juni','July':'juli',
                'August':'augusti','September':'september',
                'October':'oktober','November':'november','December':'december'
            }
            txt = d.strftime('%-d %B %Y')
            for en, se in sv.items():
                txt = txt.replace(en, se)
            return txt
        except:
            return row['s']
    return "–"

def visa_header(conn):
    uppdaterad = senaste_datum(conn)
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f"""
<div class="erimus-header">
  <div class="erimus-logo">
    <img src="data:image/jpeg;base64,{ERIMUS_LOGO_B64}" alt="Erimus">
  </div>
  <div class="erimus-title-block">
    <p class="erimus-title">Erimus Aktiebolags rättsfallsdatabas i arbetsrätt</p>
    <p class="erimus-subtitle">Arbetsdomstolen · LAS · Diskrimineringslagen · Arbetstidslagen</p>
    <p style="font-size:0.66rem;color:#5a8ab2;font-style:italic;margin-top:4px;">Uppdaterad: {uppdaterad}</p>
  </div>
</div>
<hr style="border:none;border-top:1px solid #a8c4dc;margin:0 0 22px 0;">
""", unsafe_allow_html=True)

def hamta_rattsfall(conn, sokord=None, lagomrade=None, tema=None, ar=None):
    q = """SELECT DISTINCT r.* FROM rattsfall r
           LEFT JOIN rattsfall_teman rt ON r.id = rt.rattsfall_id
           LEFT JOIN teman t ON rt.tema_id = t.id WHERE 1=1"""
    p = []
    if sokord:
        s = f'%{sokord}%'
        q += " AND (r.rubrik LIKE ? OR r.sammanfattning LIKE ? OR r.nyckelord LIKE ?)"
        p.extend([s, s, s])
    if lagomrade and lagomrade != "Alla":
        q += " AND r.lagomrade = ?"
        p.append(lagomrade)
    if tema and tema != "Alla":
        q += " AND t.tema = ?"
        p.append(tema)
    if ar:
        q += " AND strftime('%Y', r.avgorande_datum) = ?"
        p.append(str(ar))
    q += " ORDER BY r.avgorande_datum DESC"
    return conn.execute(q, p).fetchall()

def hamta_detaljer(conn, rid):
    lagrum = conn.execute(
        "SELECT lag, paragraf, stycke FROM lagrum WHERE rattsfall_id=?", (rid,)
    ).fetchall()
    teman = conn.execute(
        "SELECT t.tema FROM teman t JOIN rattsfall_teman rt ON t.id=rt.tema_id WHERE rt.rattsfall_id=?", (rid,)
    ).fetchall()
    return lagrum, teman

def main():
    conn = get_connection()
    visa_header(conn)
    
    # Sidebar med filter
    st.sidebar.title("Navigation")
    sida = st.sidebar.radio("Välj sida:", ["🔍 Sök rättsfall", "📊 Statistik", "ℹ️ Om databasen"])
    
    if sida == "🔍 Sök rättsfall":
        visa_sok_sida(conn)
    elif sida == "📊 Statistik":
        visa_statistik_sida(conn)
    else:
        visa_om_sida(conn)

def visa_sok_sida(conn):
    st.header("Sök rättsfall")
    
    # Hämta filter-alternativ (cachat)
    alternativ = hamta_filter_alternativ(conn)
    
    with st.expander("🔎 Filtrera sök", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            sokord = st.text_input("Sökord (rubrik/sammanfattning/nyckelord)", "")
            lagomrade = st.selectbox("Lagområde", ["Alla"] + alternativ['lagomraden'])
        with col2:
            tema = st.selectbox("Tema", ["Alla"] + alternativ['teman'])
            ar = st.selectbox("År", [None] + alternativ['ar'])
        sok_knapp = st.button("🔍 Sök", type="primary")
    
    if sok_knapp or sokord:
        res = hamta_rattsfall(
            conn,
            sokord if sokord else None,
            lagomrade if lagomrade != "Alla" else None,
            tema if tema != "Alla" else None,
            ar
        )
        st.markdown(f"### Hittade {len(res)} rättsfall")
        for fall in res:
            visa_kort(conn, fall)
        if not res:
            st.info("Inga träffar.")
    else:
        res = hamta_rattsfall(conn)
        st.markdown(f"### Alla rättsfall ({len(res)} st)")
        for fall in res:
            visa_kort(conn, fall)

def visa_kort(conn, fall):
    with st.expander(
        f"**{fall['malnummer']}** – {fall['rubrik']} ({fall['avgorande_datum']})"
    ):
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"**Domstol:** {fall['domstol']}  \n**Lagområde:** {fall['lagomrade']}")
            if fall['huvudsaklig_lag']:
                st.markdown(f"**Lag:** {fall['huvudsaklig_lag']}")
            st.markdown("---\n**Sammanfattning:**")
            st.markdown(fall['sammanfattning'])
            st.markdown(f"---\n**Utfall:** {fall['utfall']}")
            if fall['nyckelord']:
                st.markdown(f"**🏷️ Nyckelord:** {fall['nyckelord']}")
        with c2:
            lagrum, teman = hamta_detaljer(conn, fall['id'])
            if lagrum:
                st.markdown("**📖 Lagrum:**")
                for l in lagrum:
                    par = f"§ {l['paragraf']}"
                    if l['stycke']:
                        par += f" st. {l['stycke']}"
                    st.markdown(f"- {l['lag']} {par}")
            if teman:
                st.markdown("**🏷️ Teman:**")
                for t in teman:
                    st.markdown(f"- {t['tema']}")
            if fall['fulltext_url']:
                st.markdown(f"---\n[📄 Läs fullständig dom]({fall['fulltext_url']})")

def visa_statistik_sida(conn):
    st.header("Statistik")
    s = hamta_statistik(conn)
    ld = {r['lagomrade']: r['antal'] for r in s['per_lagomrade']}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Totalt", s['totalt'])
    c2.metric("LAS-fall", ld.get('LAS', 0))
    c3.metric("Diskriminering", ld.get('Diskrimineringslagen', 0))
    c4.metric("Arbetstid", ld.get('Arbetstidslagen', 0))
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Per lagområde")
        df = pd.DataFrame(s['per_lagomrade'])
        if not df.empty:
            st.bar_chart(df.set_index('lagomrade'))
    with col2:
        st.subheader("Per år")
        df = pd.DataFrame(s['per_ar'])
        if not df.empty:
            st.bar_chart(df.set_index('ar'))

def visa_om_sida(conn):
    uppdaterad = senaste_datum(conn)
    st.header("Om databasen")
    st.markdown(f"""
Erimus Aktiebolags rättsfallsdatabas samlar avgöranden från Arbetsdomstolen.

**Lagområden:**
- Lag om anställningsskydd (LAS)
- Diskrimineringslagen
- Arbetstidslagen och EU:s arbetstidsdirektiv

**Senast uppdaterad:** {uppdaterad}

[Arbetsdomstolen](https://www.arbetsdomstolen.se/) · 
[Lagen.nu](https://lagen.nu/dom/ad/) · 
[DO](https://www.do.se/)

*Databasen är avsedd för information och utgör inte juridisk rådgivning.*
    """)

if __name__ == '__main__':
    main()

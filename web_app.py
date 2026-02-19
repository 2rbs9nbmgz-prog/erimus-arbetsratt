#!/usr/bin/env python3
"""
Webbaserat gränssnitt för arbetsrättsdatabasen
Kör med: streamlit run web_app.py
"""
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Konfiguration
st.set_page_config(
    page_title="Arbetsrättslig Rättsfallsdatabas",
    page_icon="⚖️",
    layout="wide"
)

# Databasanslutning
@st.cache_resource
def get_connection():
    conn = sqlite3.connect('arbetsratt_rattsfall.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hamta_rattsfall(conn, sokord=None, lagomrade=None, tema=None, ar=None):
    """Sök rättsfall baserat på kriterier"""
    query = """
        SELECT DISTINCT r.* 
        FROM rattsfall r
        LEFT JOIN rattsfall_teman rt ON r.id = rt.rattsfall_id
        LEFT JOIN teman t ON rt.tema_id = t.id
        WHERE 1=1
    """
    params = []
    
    if sokord:
        query += """ AND (r.rubrik LIKE ? OR r.sammanfattning LIKE ? 
                        OR r.nyckelord LIKE ?)"""
        sokterm = f'%{sokord}%'
        params.extend([sokterm, sokterm, sokterm])
    
    if lagomrade and lagomrade != "Alla":
        query += " AND r.lagomrade = ?"
        params.append(lagomrade)
    
    if tema and tema != "Alla":
        query += " AND t.tema = ?"
        params.append(tema)
    
    if ar:
        query += " AND strftime('%Y', r.avgorande_datum) = ?"
        params.append(str(ar))
    
    query += " ORDER BY r.avgorande_datum DESC"
    
    cursor = conn.execute(query, params)
    return cursor.fetchall()

def hamta_detaljer(conn, rattsfall_id):
    """Hämta fullständiga detaljer för ett rättsfall"""
    # Hämta lagrum
    cursor = conn.execute("""
        SELECT lag, paragraf, stycke FROM lagrum 
        WHERE rattsfall_id = ?
    """, (rattsfall_id,))
    lagrum = cursor.fetchall()
    
    # Hämta teman
    cursor = conn.execute("""
        SELECT t.tema, t.beskrivning FROM teman t
        JOIN rattsfall_teman rt ON t.id = rt.tema_id
        WHERE rt.rattsfall_id = ?
    """, (rattsfall_id,))
    teman = cursor.fetchall()
    
    return lagrum, teman

def hamta_teman(conn):
    """Hämta alla teman"""
    cursor = conn.execute("SELECT DISTINCT tema FROM teman ORDER BY tema")
    return [row['tema'] for row in cursor.fetchall()]

def hamta_statistik(conn):
    """Hämta databasstatistik"""
    stats = {}
    
    cursor = conn.execute("SELECT COUNT(*) as antal FROM rattsfall")
    stats['totalt'] = cursor.fetchone()['antal']
    
    cursor = conn.execute("""
        SELECT lagomrade, COUNT(*) as antal 
        FROM rattsfall 
        GROUP BY lagomrade
    """)
    stats['per_lagomrade'] = cursor.fetchall()
    
    cursor = conn.execute("""
        SELECT strftime('%Y', avgorande_datum) as ar, COUNT(*) as antal
        FROM rattsfall
        GROUP BY ar
        ORDER BY ar DESC
    """)
    stats['per_ar'] = cursor.fetchall()
    
    return stats

# Huvudapp
def main():
    conn = get_connection()
    
    # Sidhuvud
    st.title("⚖️ Arbetsrättslig Rättsfallsdatabas")
    st.markdown("*Sök och utforska rättsfall från Arbetsdomstolen inom LAS och Diskrimineringslagen*")
    
    # Sidebar för navigation
    st.sidebar.title("Navigation")
    sida = st.sidebar.radio(
        "Välj sida:",
        ["🔍 Sök rättsfall", "📊 Statistik", "📚 Om databasen"]
    )
    
    if sida == "🔍 Sök rättsfall":
        visa_sok_sida(conn)
    elif sida == "📊 Statistik":
        visa_statistik_sida(conn)
    else:
        visa_om_sida()

def visa_sok_sida(conn):
    """Sök och visa rättsfall"""
    st.header("🔍 Sök rättsfall")
    
    # Sökfilter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sokord = st.text_input("🔎 Sökord", placeholder="t.ex. diskriminering, uppsägning...")
    
    with col2:
        lagomraden = ["Alla", "LAS", "Diskrimineringslagen"]
        lagomrade = st.selectbox("📋 Lagområde", lagomraden)
    
    with col3:
        teman = ["Alla"] + hamta_teman(conn)
        tema = st.selectbox("🏷️ Tema", teman)
    
    # Extra filter
    with st.expander("Fler filter"):
        col1, col2 = st.columns(2)
        with col1:
            cursor = conn.execute("""
                SELECT DISTINCT strftime('%Y', avgorande_datum) as ar 
                FROM rattsfall 
                ORDER BY ar DESC
            """)
            ar_lista = [None] + [row['ar'] for row in cursor.fetchall()]
            ar = st.selectbox("📅 År", ar_lista, format_func=lambda x: "Alla" if x is None else x)
    
    # Sök-knapp
    if st.button("🔍 Sök", type="primary"):
        resultat = hamta_rattsfall(
            conn, 
            sokord=sokord if sokord else None,
            lagomrade=lagomrade if lagomrade != "Alla" else None,
            tema=tema if tema != "Alla" else None,
            ar=ar
        )
        
        st.markdown(f"### Hittade {len(resultat)} rättsfall")
        
        if resultat:
            for fall in resultat:
                visa_rattsfall_kort(conn, fall)
        else:
            st.info("Inga rättsfall matchade dina sökkriterier.")
    else:
        # Visa alla rättsfall som standard
        resultat = hamta_rattsfall(conn)
        st.markdown(f"### Visar alla rättsfall ({len(resultat)} st)")
        
        for fall in resultat:
            visa_rattsfall_kort(conn, fall)

def visa_rattsfall_kort(conn, fall):
    """Visa ett rättsfall i kortformat med expanderbar detalj"""
    with st.expander(f"**{fall['malnummer']}** - {fall['rubrik']} ({fall['avgorande_datum']})"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Domstol:** {fall['domstol']}")
            st.markdown(f"**Lagområde:** {fall['lagomrade']}")
            if fall['huvudsaklig_lag']:
                st.markdown(f"**Lag:** {fall['huvudsaklig_lag']}")
            
            st.markdown("---")
            st.markdown("**Sammanfattning:**")
            st.markdown(fall['sammanfattning'])
            
            st.markdown("---")
            st.markdown(f"**Utfall:** {fall['utfall']}")
            
            if fall['nyckelord']:
                st.markdown(f"**🏷️ Nyckelord:** {fall['nyckelord']}")
        
        with col2:
            # Hämta lagrum och teman
            lagrum, teman = hamta_detaljer(conn, fall['id'])
            
            if lagrum:
                st.markdown("**📖 Lagrum:**")
                for l in lagrum:
                    paragraf_text = f"§ {l['paragraf']}"
                    if l['stycke']:
                        paragraf_text += f" st. {l['stycke']}"
                    st.markdown(f"- {l['lag']} {paragraf_text}")
            
            if teman:
                st.markdown("**🏷️ Teman:**")
                for t in teman:
                    st.markdown(f"- {t['tema']}")
            
            if fall['fulltext_url']:
                st.markdown("---")
                st.markdown(f"[📄 Läs fullständig dom]({fall['fulltext_url']})")

def visa_statistik_sida(conn):
    """Visa statistik om databasen"""
    st.header("📊 Statistik")
    
    stats = hamta_statistik(conn)
    
    # Översikt
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Totalt antal rättsfall", stats['totalt'])
    
    with col2:
        if stats['per_lagomrade']:
            las_antal = next((r['antal'] for r in stats['per_lagomrade'] if r['lagomrade'] == 'LAS'), 0)
            st.metric("LAS-fall", las_antal)
    
    with col3:
        if stats['per_lagomrade']:
            disk_antal = next((r['antal'] for r in stats['per_lagomrade'] if r['lagomrade'] == 'Diskrimineringslagen'), 0)
            st.metric("Diskrimineringsfall", disk_antal)
    
    st.markdown("---")
    
    # Diagram
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Fördelning per lagområde")
        if stats['per_lagomrade']:
            df = pd.DataFrame(stats['per_lagomrade'])
            st.bar_chart(df.set_index('lagomrade'))
    
    with col2:
        st.subheader("Rättsfall per år")
        if stats['per_ar']:
            df = pd.DataFrame(stats['per_ar'])
            st.bar_chart(df.set_index('ar'))
    
    st.markdown("---")
    
    # Teman
    st.subheader("Teman med rättsfall")
    cursor = conn.execute("""
        SELECT t.tema, t.beskrivning, COUNT(rt.rattsfall_id) as antal
        FROM teman t
        LEFT JOIN rattsfall_teman rt ON t.id = rt.tema_id
        GROUP BY t.id
        HAVING antal > 0
        ORDER BY antal DESC, t.tema
    """)
    
    tema_data = []
    for row in cursor.fetchall():
        tema_data.append({
            'Tema': row['tema'],
            'Beskrivning': row['beskrivning'],
            'Antal rättsfall': row['antal']
        })
    
    if tema_data:
        st.dataframe(tema_data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Senaste rättsfallen
    st.subheader("Senaste rättsfallen")
    cursor = conn.execute("""
        SELECT malnummer, rubrik, avgorande_datum, lagomrade
        FROM rattsfall
        ORDER BY avgorande_datum DESC
        LIMIT 10
    """)
    
    senaste = []
    for row in cursor.fetchall():
        senaste.append({
            'Målnummer': row['malnummer'],
            'Rubrik': row['rubrik'],
            'Datum': row['avgorande_datum'],
            'Lagområde': row['lagomrade']
        })
    
    st.dataframe(senaste, use_container_width=True, hide_index=True)

def visa_om_sida():
    """Visa information om databasen"""
    st.header("📚 Om databasen")
    
    st.markdown("""
    ## Arbetsrättslig Rättsfallsdatabas
    
    Denna databas innehåller rättsfall från Arbetsdomstolen med fokus på:
    
    ### 📋 Lagområden
    - **Lag om anställningskydd (LAS)** - Rättsfall om uppsägningar, turordning, arbetsbrist m.m.
    - **Diskrimineringslagen** - Rättsfall om olika former av diskriminering i arbetslivet
    
    ### 🏷️ Teman
    Rättsfallen är kategoriserade enligt följande teman:
    
    **LAS-relaterade:**
    - Uppsägning saklig grund
    - Turordning vid uppsägning
    - Arbetsbrist
    - Personliga skäl
    - Omplacering
    - Visstidsanställning
    - Provanställning
    
    **Diskrimineringsrelaterade:**
    - Åldersdiskriminering
    - Könsdiskriminering
    - Etnisk diskriminering
    - Diskriminering p.g.a. funktionsnedsättning
    - Trakasserier
    - Sexuella trakasserier
    - Repressalier
    
    **Allmänt:**
    - Bevisning och bevisbörda
    - Skadestånd
    
    ### 🔍 Hur man använder databasen
    
    1. **Sök rättsfall** - Använd söksidan för att hitta relevanta rättsfall
    2. **Filtrera** - Använd filter för lagområde, tema och år
    3. **Utforska** - Klicka på rättsfall för att se detaljer, lagrum och teman
    4. **Statistik** - Se översikt och trender i rättspraxis
    
    ### 💾 Teknisk information
    
    - **Databastyp:** SQLite 3
    - **Antal rättsfall:** Se statistiksidan
    - **Uppdaterad:** Februari 2026
    
    ### 📖 Resurser
    
    - [Arbetsdomstolen](https://www.arbetsdomstolen.se/)
    - [Lagen.nu - Rättsfallsregister](https://lagen.nu/dom/ad/)
    - [Diskrimineringsombudsmannen](https://www.do.se/)
    
    ### ⚠️ Ansvarsfriskrivning
    
    Denna databas är avsedd för informationsändamål och utgör inte juridisk rådgivning. 
    För juridisk rådgivning, kontakta en jurist eller advokat.
    """)

if __name__ == '__main__':
    main()

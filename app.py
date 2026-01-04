# app.py

import streamlit as st
import pandas as pd
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import ssl
import httpx

# --- Globale Umgehung für SSL-Zertifikatsprobleme (Methode 1) ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# --- 1. Verbindung zu Supabase herstellen ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    
    # --- Spezifische Umgehung für SSL-Zertifikatsprobleme (Methode 2) ---
    httpx_client = httpx.Client(verify=False)
    opts = ClientOptions(httpx_client=httpx_client)
    
    return create_client(url, key, options=opts)

supabase = init_connection()

# --- 2. Funktion zum Abfragen der Daten ---
@st.cache_data
def run_query(query):
    response = supabase.rpc('execute_sql', {'sql_query': query}).execute()
    data = response.data
    return pd.DataFrame(data)

# --- 3. Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Gewächshaus-Dashboard")

st.header("Klima-Analyse")

# --- 4. Beispiel-Abfrage und Plot: Durchschnittstemperatur pro Woche ---
st.subheader("Durchschnittliche Aussentemperatur pro Woche")

query_temp_per_week = """
    SELECT
        woche,
        AVG(aussen_durchschnittstemp_c) as avg_temp
    FROM
        klima_messungen
    WHERE
        woche IS NOT NULL AND aussen_durchschnittstemp_c IS NOT NULL
    GROUP BY
        woche
    ORDER BY
        woche;
"""

try:
    df_temp = run_query(query_temp_per_week)
    if not df_temp.empty:
        st.line_chart(df_temp.set_index('woche'))
    else:
        st.warning("Keine Klimadaten für diesen Zeitraum gefunden.")
except Exception as e:
    st.error(f"Ein Fehler ist aufgetreten: {e}")


# --- 5. Weiteres Beispiel: Wachstum einer bestimmten Pflanze ---
st.header("Pflanzenwachstum-Analyse")
st.subheader("Stängeldicke einer Beispielpflanze über die Zeit")

query_growth = """
    SELECT
        datum,
        staengeldicke_mm
    FROM
        wachstum_messungen
    WHERE
        pflanze_nr = 5 AND staengeldicke_mm IS NOT NULL
    ORDER BY
        datum;
"""

try:
    df_growth = run_query(query_growth)
    if not df_growth.empty:
        st.bar_chart(df_growth.set_index('datum'))
    else:
        st.info("Keine Wachstumsdaten für Pflanze Nr. 5 gefunden.")
except Exception as e:
    st.error(f"Ein Fehler ist aufgetreten: {e}")
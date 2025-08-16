# app_local_csv.py

import streamlit as st
import pandas as pd

# --- 1. Funktion zum Laden der Daten aus CSV-Dateien ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'datum' in df.columns:
            df['datum'] = pd.to_datetime(df['datum'])
        return df
    except FileNotFoundError:
        st.error(f"FEHLER: Die Datei '{file_path}' wurde nicht im Projektordner gefunden.")
        return None

# --- 2. Daten laden ---
df_pflanzen = load_data('pflanzen.csv')
df_klima = load_data('klima_messungen.csv')
df_wachstum = load_data('wachstum_messungen.csv')
df_produktion = load_data('produktion_messungen.csv')


# --- 3. Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Gewächshaus Dashboard: Wichtige Analysen")

# --- PLOT 1: INNEN- VS. AUSSENTEMPERATUR ---
st.header("🌡️ Klima im Griff: Innen- vs. Aussentemperatur")
import plotly.graph_objects as go

if df_klima is not None:
    temp_vergleich = df_klima.set_index('datum')[['gh_gem_tagesdurchschnitt_c', 'aussen_durchschnittstemp_c']]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=temp_vergleich.index,
        y=temp_vergleich['gh_gem_tagesdurchschnitt_c'],
        mode='lines',
        name='Innen'
    ))
    fig.add_trace(go.Scatter(
        x=temp_vergleich.index,
        y=temp_vergleich['aussen_durchschnittstemp_c'],
        mode='lines',
        name='Aussen'
    ))
    fig.update_layout(
        xaxis_title="Datum",
        yaxis_title="Temperatur in Grad Celsius"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("Dieser Plot zeigt, wie gut Ihr Gewächshaus die Innentemperatur im Vergleich zur Aussentemperatur reguliert.")

# --- Durchschnittliche Innen- vs. Aussentemperatur pro Haus ---
if df_klima is not None and 'haus' in df_klima.columns:
    st.subheader("Durchschnittliche Innen vs. Aussentemperatur pro Haus")
    haus_options = df_klima['haus'].unique()
    selected_haus = st.selectbox("Haus auswählen", haus_options)
    df_haus = df_klima[df_klima['haus'] == selected_haus]
    temp_vergleich_haus = df_haus.set_index('datum')[['gh_gem_tagesdurchschnitt_c', 'aussen_durchschnittstemp_c']]
    fig_haus = go.Figure()
    fig_haus.add_trace(go.Scatter(
        x=temp_vergleich_haus.index,
        y=temp_vergleich_haus['gh_gem_tagesdurchschnitt_c'],
        mode='lines',
        name='Innen'
    ))
    fig_haus.add_trace(go.Scatter(
        x=temp_vergleich_haus.index,
        y=temp_vergleich_haus['aussen_durchschnittstemp_c'],
        mode='lines',
        name='Aussen'
    ))
    fig_haus.update_layout(
        xaxis_title="Datum",
        yaxis_title="Temperatur in Grad Celsius"
    )
    st.plotly_chart(fig_haus, use_container_width=True)
    st.info(f"Vergleich der Temperaturen für Haus '{selected_haus}' über die Zeit.")

# --- PLOT 2: STRAHLUNG VS. WACHSTUM ---
st.header("☀️🌱 Wachstumsmotor: Strahlung vs. Längenzuwachs pro Haus")
if df_pflanzen is not None and df_klima is not None and df_wachstum is not None:
    # Kultur-Auswahl
    kultur_options = df_pflanzen['kultur'].unique()
    selected_kultur = st.selectbox("Kultur auswählen", kultur_options)

    # Finde zugehörige Häuser für die gewählte Kultur
    pflanzen_kultur = df_pflanzen[df_pflanzen['kultur'] == selected_kultur]
    haus_options = pflanzen_kultur['haus'].unique()
    selected_haus = haus_options[0] if len(haus_options) == 1 else st.selectbox("Haus auswählen", haus_options)

    # Filtere Klima- und Wachstumsdaten für die gewählte Kultur und das zugehörige Haus
    df_klima_kultur_haus = df_klima[(df_klima['haus'] == selected_haus)]
    df_wachstum_kultur_haus = df_wachstum[(df_wachstum['haus'] == selected_haus)]

    # Berechne die durchschnittliche wöchentliche Strahlungssumme
    strahlung_pro_woche = df_klima_kultur_haus.groupby('woche')['aussen_strahlungssumme_j_cm2'].mean().reset_index()

    # Berechne den durchschnittlichen Längenzuwachs pro Woche
    wachstum_pro_woche = df_wachstum_kultur_haus.groupby('woche')['laengenzuwachs_cm_woche'].mean().reset_index()

    # Führe die beiden Datensätze zusammen
    merged_df = pd.merge(strahlung_pro_woche, wachstum_pro_woche, on='woche')

    # Sortiere nach Woche, damit die Punkte chronologisch sind
    merged_df = merged_df.sort_values('woche')

    # Plotly Scatterplot: Woche auf x-Achse, Strahlung und Längenzuwachs als Linien
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=merged_df['woche'],
        y=merged_df['aussen_strahlungssumme_j_cm2'],
        mode='lines+markers',
        name='Strahlungssumme (J/cm²)'
    ))
    fig.add_trace(go.Scatter(
        x=merged_df['woche'],
        y=merged_df['laengenzuwachs_cm_woche'],
        mode='lines+markers',
        name='Längenzuwachs (cm/Woche)',
        yaxis='y2'
    ))
    fig.update_layout(
        title=f"Strahlung und Längenzuwachs pro Woche ({selected_kultur}, Haus {selected_haus})",
        xaxis_title="Woche",
        yaxis=dict(
            title="Strahlungssumme (J/cm²)",
            side="left"
        ),
        yaxis2=dict(
            title="Längenzuwachs (cm/Woche)",
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("Die x-Achse zeigt die Wochen in chronologischer Reihenfolge. So siehst du, wie sich Strahlung und Wachstum gemeinsam über die Zeit entwickeln.")

# --- PLOT 3: PRODUKTIONS-PIPELINE ---
st.header("🍅 LAI vs. Fruchtansatz: Zusammenhang analysieren")
if df_produktion is not None and df_pflanzen is not None:
    # Kultur-Auswahl
    kultur_options = df_pflanzen['kultur'].unique()
    selected_kultur = st.selectbox("Kultur auswählen (LAI vs. Fruchtansatz)", kultur_options)

    # Finde zugehörige Pflanzen-IDs für die gewählte Kultur
    pflanzen_kultur = df_pflanzen[df_pflanzen['kultur'] == selected_kultur]
    pflanzen_ids = pflanzen_kultur['pflanze_id'].unique()

    # Filtere Produktionsdaten für die gewählte Kultur
    produktion_kultur = df_produktion[df_produktion['pflanze_id'].isin(pflanzen_ids)]

    # Berechne durchschnittlichen LAI pro Woche aus df_wachstum und Fruchtansatz pro Woche aus produktion_kultur
    if df_wachstum is not None:
        # Filtere Wachstumsdaten für die gewählte Kultur
        wachstum_kultur = df_wachstum[df_wachstum['pflanze_id'].isin(pflanzen_ids)]
        lai_pro_woche = wachstum_kultur.groupby('woche')['lai_m2_m2'].mean().reset_index()
        fruchtansatz_pro_woche = produktion_kultur.groupby('woche')['fruchtansatz_x_m2'].mean().reset_index()
        # Führe die beiden Datensätze zusammen
        lai_fruchtansatz = pd.merge(lai_pro_woche, fruchtansatz_pro_woche, on='woche')
    else:
        lai_fruchtansatz = pd.DataFrame()

    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=lai_fruchtansatz['woche'],
        y=lai_fruchtansatz['lai_m2_m2'],
        mode='lines+markers',
        name='LAI (m²/m²)',
    ))
    fig.add_trace(go.Scatter(
        x=lai_fruchtansatz['woche'],
        y=lai_fruchtansatz['fruchtansatz_x_m2'],
        mode='lines+markers',
        name='Fruchtansatz',
        yaxis='y2'
    ))
    fig.update_layout(
        title=f"LAI und Fruchtansatz pro Woche ({selected_kultur})",
        xaxis_title="Woche",
        yaxis=dict(
            title="LAI",
            side="left"
        ),
        yaxis2=dict(
            title="Fruchtansatz_pro_m2",
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("Dieser Plot zeigt den Zusammenhang zwischen Blattflächenindex (LAI) und Fruchtansatz pro Woche für die gewählte Kultur.")

# --- PLOT 4: SORTENVERGLEICH ---
st.header("🏆 Sortenvergleich: Welche Sorte liefert am meisten?")
if df_produktion is not None and df_pflanzen is not None:
    # Kultur-Auswahl
    kultur_options = df_pflanzen['kultur'].unique()
    selected_kultur = st.selectbox("Kultur auswählen (Sortenvergleich)", kultur_options)

    # Filtere Pflanzen-Stammdaten und Produktionsdaten für die gewählte Kultur
    pflanzen_kultur = df_pflanzen[df_pflanzen['kultur'] == selected_kultur]
    pflanzen_ids = pflanzen_kultur['pflanze_id'].unique()
    produktion_kultur = df_produktion[df_produktion['pflanze_id'].isin(pflanzen_ids)]

    # Führe Produktionsdaten und Pflanzen-Stammdaten zusammen
    sorten_df = pd.merge(produktion_kultur, pflanzen_kultur, on='pflanze_id')

    # Berechne die durchschnittliche Produktion pro Sorte
    produktion_pro_sorte = sorten_df.groupby('sorte')['produktion_x_m2'].mean().sort_values(ascending=False)

    import plotly.express as px
    fig = px.bar(
        produktion_pro_sorte,
        x=produktion_pro_sorte.index,
        y=produktion_pro_sorte.values,
        labels={'x': 'Sorte', 'y': 'Produktion pro m²'},
        title="Durchschnittliche Produktion pro Sorte"
    )
    fig.update_yaxes(title_text="Produktion pro m²")
    st.plotly_chart(fig, use_container_width=True)

    beste_sorte = produktion_pro_sorte.idxmax() if not produktion_pro_sorte.empty else None
    if beste_sorte:
        st.success(f"Die Sorte mit der höchsten durchschnittlichen Produktion für '{selected_kultur}' ist: **{beste_sorte}**")
    st.info("Dieser Plot vergleicht die durchschnittliche Produktion (in kg oder Anzahl pro m²) für jede Sorte innerhalb der gewählten Kultur.")

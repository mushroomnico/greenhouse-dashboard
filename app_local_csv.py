import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# --- 1. SETUP & PFADE ---
st.set_page_config(layout="wide", page_title="Greenhouse Data Analyzer")

# Findet den Ordner, in dem dieses Skript liegt
BASE_DIR = Path(__file__).parent 

# --- 2. DATEN-LADE-FUNKTION ---
@st.cache_data
def load_data(file_name):
    full_path = BASE_DIR / file_name
    try:
        df = pd.read_csv(full_path)
        if 'datum' in df.columns:
            df['datum'] = pd.to_datetime(df['datum'])
        return df
    except FileNotFoundError:
        st.error(f"Datei nicht gefunden: {full_path}")
        return None

# Daten laden
df_pflanzen = load_data('pflanzen.csv')
df_klima = load_data('klima_messungen.csv')
df_wachstum = load_data('wachstum_messungen.csv')
df_produktion = load_data('produktion_messungen.csv')

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



# --- 3. MASTER DATAFRAME ERSTELLEN (Alles zusammenführen) ---
def create_master_df():
    # Wir starten mit Klima
    if df_klima is None: return None, []
    
    master = df_klima.copy()
    
    # Mergen mit Wachstum (über Datum und Haus)
    if df_wachstum is not None:
        master = pd.merge(master, df_wachstum, on=['datum', 'haus'], how='outer')
    
    # Mergen mit Produktion (über Datum und Haus/Pflanze falls vorhanden)
    if df_produktion is not None:
        # Falls produktion_messungen keine 'haus' Spalte hat, müssen wir sie über df_pflanzen holen
        prod_tmp = df_produktion.copy()
        if 'haus' not in prod_tmp.columns and df_pflanzen is not None:
            prod_tmp = pd.merge(prod_tmp, df_pflanzen[['pflanze_id', 'haus', 'kultur']], on='pflanze_id', how='left')
        
        master = pd.merge(master, prod_tmp, on=['datum', 'haus'], how='outer', suffixes=('', '_prod'))

    # Kultur-Informationen sicherstellen
    if 'kultur' not in master.columns and df_pflanzen is not None:
        # Wenn kultur fehlt, versuchen wir sie über das Haus zu mappen
        haus_kultur_map = df_pflanzen.groupby('haus')['kultur'].first().to_dict()
        master['kultur'] = master['haus'].map(haus_kultur_map)

    # Numerische Spalten für die Auswahl identifizieren
    numeric_cols = master.select_dtypes(include=['number']).columns.tolist()
    # Woche/ID/Jahr oft nicht sinnvoll für Korrelation, optional entfernen:
    blacklist = ['woche', 'jahr', 'pflanze_id', 'pflanze_nr']
    numeric_cols = [c for c in numeric_cols if c not in blacklist]
    
    return master, numeric_cols

df_master, numeric_cols = create_master_df()

# --- 4. SIDEBAR FILTER ---
st.sidebar.header("Filter-Optionen")
if df_master is not None:
    all_cultures = sorted([str(x) for x in df_master['kultur'].unique() if pd.notna(x)])
    selected_cultures = st.sidebar.multiselect("Kulturen", options=all_cultures, default=all_cultures)

    all_houses = sorted([str(x) for x in df_master['haus'].unique() if pd.notna(x)])
    selected_houses = st.sidebar.multiselect("Häuser", options=all_houses, default=all_houses)

    # Filter anwenden
    mask = df_master['kultur'].astype(str).isin(selected_cultures) & df_master['haus'].astype(str).isin(selected_houses)
    df_filtered = df_master[mask]
else:
    st.stop()

# --- 5. HAUPTSEITE ---
st.title("🌿 Greenhouse Data: Erweiterte Analyse")

# --- PLOT 1: KORRELATION ---
st.header("🔍 Analyse 1: Korrelations-Konfigurator")

with st.expander("Einstellungen für Korrelationsplot", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        x_param = st.selectbox("X-Achse auswählen", options=numeric_cols, index=0)
        color_opt = st.selectbox("Farbe nach:", ["Keine", "kultur", "haus"])
    with col2:
        y_param = st.selectbox("Y-Achse auswählen", options=numeric_cols, index=1)
        facet_opt = st.selectbox("Separate Diagramme (Faceting):", ["Keine", "kultur", "haus"])
    with col3:
        show_trend = st.checkbox("Trendlinien (Lineare Regression)", value=True)
        show_y2 = st.checkbox("Zweite Y-Achse (Rechts) nutzen")
        y_param_right = None
        if show_y2:
            y_param_right = st.selectbox("Y-Achse Rechts", options=numeric_cols, index=2)

# Plot erstellen
fig1 = px.scatter(
    df_filtered,
    x=x_param,
    y=y_param,
    color=None if color_opt == "Keine" else color_opt,
    facet_col=None if facet_opt == "Keine" else facet_opt,
    trendline="ols" if show_trend else None,
    hover_data=['datum', 'haus', 'kultur'],
    template="plotly_white",
    title=f"Korrelation: {x_param} vs. {y_param}",
    height=600
)

# Optionale zweite Y-Achse hinzufügen (manuell über graph_objects)
if show_y2 and y_param_right:
    # Plotly Express macht es schwer, eine 2. Achse in ein Facet-Grid zu drücken.
    # Wir fügen sie hier vereinfacht für den Hauptplot hinzu:
    fig1.add_trace(go.Scatter(x=df_filtered[x_param], y=df_filtered[y_param_right], 
                             mode='markers', name=y_param_right, yaxis="y2", marker=dict(symbol='x', opacity=0.5)))
    fig1.update_layout(yaxis2=dict(title=y_param_right, overlaying='y', side='right'))

st.plotly_chart(fig1, use_container_width=True)

# --- STATISTIK BOX ---
st.subheader("📊 Statistische Auswertung")
if len(df_filtered) > 1:
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        corr_val = df_filtered[x_param].corr(df_filtered[y_param])
        r2 = corr_val**2
        st.metric("Gesamt-Zusammenhang (R²)", f"{r2:.2f}")
    with col_s2:
        if color_opt != "Keine":
            st.write(f"**Details nach {color_opt}:**")
            for grp, grp_df in df_filtered.groupby(color_opt):
                if len(grp_df) > 1:
                    r_grp = grp_df[x_param].corr(grp_df[y_param])**2
                    st.write(f"- {grp}: R² = {r_grp:.2f}")
else:
    st.warning("Zu wenige Daten für Statistik.")

st.divider()

# --- PLOT 2: ZEITVERLAUF ---
st.header("📈 Analyse 2: Zeitverlauf-Vergleich")

with st.expander("Einstellungen für Zeitachse", expanded=True):
    y_multi = st.multiselect("Parameter wählen (Y-Achse)", options=numeric_cols, default=[numeric_cols[0]])
    
    if len(y_multi) >= 1:
        fig2 = go.Figure()
        for p in y_multi:
            # Durchschnitt pro Datum (falls mehrere Messungen pro Tag)
            daily_avg = df_filtered.groupby('datum')[p].mean().reset_index()
            fig2.add_trace(go.Scatter(x=daily_avg['datum'], y=daily_avg[p], name=p, mode='lines+markers'))
        
        # Zweite Achse Logik
        if len(y_multi) >= 2:
            y_to_right = st.selectbox("Einen Parameter auf die rechte Achse legen:", ["Keiner"] + y_multi)
            if y_to_right != "Keiner":
                for trace in fig2.data:
                    if trace.name == y_to_right:
                        trace.yaxis = "y2"
                fig2.update_layout(yaxis2=dict(title=y_to_right, overlaying='y', side='right'))
        
        fig2.update_layout(title="Entwicklung über die Zeit", xaxis_title="Datum", template="plotly_white", height=500, hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)
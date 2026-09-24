import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Config de la page
# ----------------------------
st.set_page_config(page_title="TikTok Songs 2020", page_icon="🎵", layout="wide")

# ----------------------------
# Chargement des données
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("TikTok_songs_2020.csv")
    return df

df = load_data()

st.title("🎵 Dashboard — TikTok Songs 2020")
st.markdown("Exploration des morceaux les plus populaires sur TikTok en 2020 (données audio Spotify).")

# ----------------------------
# Sidebar : filtres
# ----------------------------
st.sidebar.header("Filtres")

artists = sorted(df["artist_name"].unique())
selected_artists = st.sidebar.multiselect("Artiste(s)", artists)

pop_min, pop_max = int(df["track_pop"].min()), int(df["track_pop"].max())
pop_range = st.sidebar.slider("Popularité du morceau (track_pop)", pop_min, pop_max, (pop_min, pop_max))

dance_range = st.sidebar.slider("Danceability", 0.0, 1.0, (0.0, 1.0))

# Application des filtres
filtered = df.copy()
if selected_artists:
    filtered = filtered[filtered["artist_name"].isin(selected_artists)]
filtered = filtered[
    (filtered["track_pop"].between(*pop_range)) &
    (filtered["danceability"].between(*dance_range))
]

st.sidebar.markdown(f"**{len(filtered)}** morceaux sélectionnés")

# ----------------------------
# KPIs principaux
# ----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Nombre de morceaux", len(filtered))
col2.metric("Popularité moyenne", f"{filtered['track_pop'].mean():.1f}" if len(filtered) else "—")
col3.metric("Tempo moyen (BPM)", f"{filtered['tempo'].mean():.0f}" if len(filtered) else "—")
col4.metric("Durée moyenne", f"{filtered['duration_ms'].mean()/60000:.1f} min" if len(filtered) else "—")

st.divider()

# ----------------------------
# Graphiques
# ----------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Top 10 morceaux les plus populaires")
    top10 = filtered.sort_values("track_pop", ascending=False).head(10)
    fig_top = px.bar(
        top10, x="track_pop", y="track_name", color="artist_name",
        orientation="h", labels={"track_pop": "Popularité", "track_name": "Morceau"}
    )
    fig_top.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
    st.plotly_chart(fig_top, use_container_width=True)

with c2:
    st.subheader("Danceability vs Energy")
    fig_scatter = px.scatter(
        filtered, x="danceability", y="energy", size="track_pop", color="valence",
        hover_name="track_name", hover_data=["artist_name"],
        color_continuous_scale="viridis"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Distribution du tempo (BPM)")
    fig_tempo = px.histogram(filtered, x="tempo", nbins=30)
    st.plotly_chart(fig_tempo, use_container_width=True)

with c4:
    st.subheader("Répartition des tonalités (key)")
    key_labels = {0:"C",1:"C#",2:"D",3:"D#",4:"E",5:"F",6:"F#",7:"G",8:"G#",9:"A",10:"A#",11:"B"}
    key_counts = filtered["key"].map(key_labels).value_counts().reset_index()
    key_counts.columns = ["Tonalité", "Nombre"]
    fig_key = px.pie(key_counts, names="Tonalité", values="Nombre", hole=0.4)
    st.plotly_chart(fig_key, use_container_width=True)

st.divider()

# ----------------------------
# Table des données
# ----------------------------
st.subheader("Données détaillées")
st.dataframe(
    filtered[["track_name", "artist_name", "album", "track_pop", "artist_pop",
              "danceability", "energy", "tempo", "valence"]].sort_values("track_pop", ascending=False),
    use_container_width=True,
    hide_index=True
)

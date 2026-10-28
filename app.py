import json
import random
from datetime import datetime
import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="UrbanGreen | Canopy & Carbon Tracker",
    page_icon="🌿",
    layout="wide",
)

# ==============================================================================
# 🎨 DEEP FOREST CANOPY THEME (CSS)
# ==============================================================================
custom_css = """
<style>
/* Rich Deep Forest Canopy Gradient Background */
.stApp {
    background: radial-gradient(circle at top right, #163824 0%, #0D2217 60%, #07130E 100%);
    color: #ECFDF5 !important;
}

/* Crisp Mint & Emerald Typography */
html, body, [class*="css"], .stMarkdown, p, span, label, h1, h2, h3, h4, h5, h6 {
    color: #ECFDF5 !important;
    font-family: 'Inter', -apple-system, sans-serif;
}

/* Header Styling */
h1 {
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #34D399, #10B981, #ECFDF5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    border-bottom: 2px solid rgba(16, 185, 129, 0.3);
    padding-bottom: 10px;
}
h2, h3 {
    color: #34D399 !important;
    font-weight: 700;
}

/* Glassmorphism Canopy Cards */
div[data-testid="stBlock"] {
    background: rgba(18, 38, 27, 0.8) !important;
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(16, 185, 129, 0.25);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    padding: 1.4rem;
}

/* Emerald Green Glowing Buttons */
div.stButton > button, div.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
    color: #07130E !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
    transition: all 0.3s ease;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(16, 185, 129, 0.45);
}

/* Metric Cards */
[data-testid="stMetricValue"] {
    color: #34D399 !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
}
[data-testid="stMetricLabel"] {
    color: #A7F3D0 !important;
    font-weight: 600;
}

/* Custom Styled Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"] {
    background-color: rgba(18, 38, 27, 0.7) !important;
    border-radius: 8px 8px 0px 0px;
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #A7F3D0 !important;
    padding: 10px 18px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background-color: #10B981 !important;
    color: #07130E !important;
    font-weight: 700 !important;
}

/* Input Fields styling */
input, select, textarea {
    background-color: #0D2217 !important;
    color: #ECFDF5 !important;
    border: 1px solid rgba(16, 185, 129, 0.3) !important;
    border-radius: 6px !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# 📍 INITIALIZE DEFAULT TREE CANOPY DATA
# ==============================================================================
if "tree_data" not in st.session_state:
  st.session_state.tree_data = [
      {
          "id": 1,
          "species": "Oak (Quercus robur)",
          "location": "Central Park East, NY",
          "lat": 40.7812,
          "lon": -73.9665,
          "age_years": 15,
          "est_co2_kg_yr": 22.0,
          "health": "Healthy",
          "notes": "Mature canopy providing significant summer shade cover.",
      },
      {
          "id": 2,
          "species": "Maple (Acer saccharum)",
          "location": "Prospect Park, Brooklyn",
          "lat": 40.6602,
          "lon": -73.9690,
          "age_years": 8,
          "est_co2_kg_yr": 12.5,
          "health": "Healthy",
          "notes": "Planted during community reforestation initiative.",
      },
      {
          "id": 3,
          "species": "Pine (Pinus strobus)",
          "location": "Tiergarten, Berlin",
          "lat": 52.5145,
          "lon": 13.3501,
          "age_years": 20,
          "est_co2_kg_yr": 28.0,
          "health": "Monitored",
          "notes": "Evergreen shelter belt tree; active growth monitoring.",
      },
      {
          "id": 4,
          "species": "Jacaranda (Jacaranda mimosifolia)",
          "location": "Karura Forest Border, Nairobi",
          "lat": -1.2400,
          "lon": 36.8300,
          "age_years": 5,
          "est_co2_kg_yr": 8.0,
          "health": "Healthy",
          "notes": (
              "Flowering urban street tree contributing to local pollinator"
              " habitat."
          ),
      },
  ]

if "clicked_lat" not in st.session_state:
  st.session_state.clicked_lat = 0.0
if "clicked_lon" not in st.session_state:
  st.session_state.clicked_lon = 0.0

# ==============================================================================
# 🖥️ APP HEADER & METRICS
# ==============================================================================
st.title("🌿 UrbanGreen")
st.markdown(
    "##### *A spatial neighborhood canopy registry & carbon offset estimator.*"
)

df = pd.DataFrame(st.session_state.tree_data)
total_trees = len(df)
total_co2 = round(df["est_co2_kg_yr"].sum(), 1) if not df.empty else 0
avg_age = round(df["age_years"].mean(), 1) if not df.empty else 0

col1, col2, col3 = st.columns(3)
col1.metric(label="Registered Canopy Trees", value=total_trees)
col2.metric(label="Est. Annual CO₂ Offset", value=f"{total_co2} kg/yr")
col3.metric(label="Avg Stand Age", value=f"{avg_age} yrs")

st.divider()

# ==============================================================================
# 📑 TABS: MAP vs REGISTRY vs ADD TREE vs ANALYTICS
# ==============================================================================
tab_map, tab_list, tab_add, tab_analytics = st.tabs([
    "🗺️ Canopy Map",
    "🌳 Tree Registry",
    "✨ Log Planting",
    "📊 Impact Analytics",
])

with tab_map:
  st.markdown("### Interactive Canopy Atlas")
  st.caption(
      "Click anywhere on the map to capture coordinates for logging a new tree!"
  )

  m = folium.Map(
      location=[20.0, 0.0],
      zoom_start=2,
      tiles="CartoDB dark_matter",
      name="Dark Mode Map",
  )
  folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
  folium.TileLayer(
      tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
      attr="Google Satellite",
      name="Google Satellite",
      max_zoom=20,
  ).add_to(m)

  for tree in st.session_state.tree_data:
    popup_html = f"""
        <div style="font-family: sans-serif; width: 210px; color: #07130E;">
            <h4 style="margin:0; color:#059669;">{tree['species']}</h4>
            <p style="margin:4px 0; font-size:12px;">📍 <b>{tree['location']}</b></p>
            <p style="margin:4px 0; font-size:12px;">🌳 Age: {tree['age_years']} years</p>
            <p style="margin:4px 0; font-size:12px;">🍃 Est CO₂: {tree['est_co2_kg_yr']} kg/yr</p>
            <p style="margin:4px 0; font-size:12px;">🏷️ Status: {tree['health']}</p>
            <hr style="margin:4px 0;">
            <p style="font-size:11px; color:#444;">{tree['notes']}</p>
        </div>
        """
    folium.Marker(
        location=[tree["lat"], tree["lon"]],
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=tree["species"],
        icon=folium.Icon(color="green", icon="tree", prefix="fa"),
    ).add_to(m)

  folium.LayerControl().add_to(m)
  map_data = st_folium(m, width=1200, height=500, key="canopy_map")

  if map_data and map_data.get("last_clicked"):
    clat = map_data["last_clicked"]["lat"]
    clon = map_data["last_clicked"]["lng"]
    if (
        clat != st.session_state.clicked_lat
        or clon != st.session_state.clicked_lon
    ):
      st.session_state.clicked_lat = clat
      st.session_state.clicked_lon = clon
      st.success(
          f"📍 Coordinates Captured: Lat `{clat:.4f}`, Lon `{clon:.4f}`. Head"
          " to **'Log Planting'** to complete entry!"
      )

with tab_list:
  st.markdown("### Registered Community Trees")

  s1, s2 = st.columns(2)
  with s1:
    search_q = st.text_input(
        "🔍 Search Species or Location", placeholder="e.g. Oak or Brooklyn"
    )
  with s2:
    health_f = st.selectbox(
        "Filter by Health Status",
        ["All"] + list(df["health"].unique()) if not df.empty else ["All"],
    )

  filtered_df = df.copy()
  if search_q:
    filtered_df = filtered_df[
        filtered_df["species"].str.contains(search_q, case=False, na=False)
        | filtered_df["location"].str.contains(search_q, case=False, na=False)
    ]
  if health_f != "All":
    filtered_df = filtered_df[filtered_df["health"] == health_f]

  for _, row in filtered_df.iterrows():
    with st.container():
      col_a, col_b = st.columns([4, 1])
      with col_a:
        st.markdown(f"#### 🌳 {row['species']} — *{row['location']}*")
        st.markdown(
            f"**Age:** `{row['age_years']} yrs` &nbsp;|&nbsp; **Est."
            f" Sequestration:** `{row['est_co2_kg_yr']} kg CO₂/yr`"
            f" &nbsp;|&nbsp; **Health:** `{row['health']}`"
        )
        st.info(row["notes"])
      with col_b:
        if st.button("Delete Tree", key=f"del_tree_{row['id']}"):
          st.session_state.tree_data = [
              x for x in st.session_state.tree_data if x["id"] != row["id"]
          ]
          st.rerun()
      st.divider()

with tab_add:
  st.markdown("### Log a New Planting Entry")
  st.markdown("Record a newly planted tree or community park specimen.")

  with st.form("add_tree_form"):
    t_species = st.text_input(
        "Species Name", placeholder="e.g. Red Maple (Acer rubrum)"
    )
    t_location = st.text_input(
        "Location Name", placeholder="e.g. Riverside Park Zone B"
    )

    c1, c2 = st.columns(2)
    with c1:
      def_lat = (
          st.session_state.clicked_lat
          if st.session_state.clicked_lat != 0.0
          else 40.7128
      )
      t_lat = st.number_input("Latitude", value=float(def_lat), format="%.4f")
    with c2:
      def_lon = (
          st.session_state.clicked_lon
          if st.session_state.clicked_lon != 0.0
          else -74.0060
      )
      t_lon = st.number_input("Longitude", value=float(def_lon), format="%.4f")

    c3, c4 = st.columns(2)
    with c3:
      t_age = st.number_input(
          "Tree Age (Years)", min_value=1, max_value=200, value=5
      )
    with c4:
      t_health = st.selectbox(
          "Health Condition", ["Healthy", "Monitored", "Needs Care"]
      )

    t_notes = st.text_area(
        "Field Observations",
        placeholder="Soil condition, stake support, watering schedule...",
    )

    submitted = st.form_submit_button("Record Tree in Registry")
    if submitted:
      if t_species and t_location:
        est_co2 = round(min(t_age * 1.3, 30.0), 1)
        new_id = (
            max([x["id"] for x in st.session_state.tree_data]) + 1
            if st.session_state.tree_data
            else 1
        )
        st.session_state.tree_data.append({
            "id": new_id,
            "species": t_species,
            "location": t_location,
            "lat": t_lat,
            "lon": t_lon,
            "age_years": t_age,
            "est_co2_kg_yr": est_co2,
            "health": t_health,
            "notes": t_notes,
        })
        st.success(f"Recorded '{t_species}' in UrbanGreen!")
        st.rerun()
      else:
        st.error("Please enter a species name and location.")

with tab_analytics:
  st.markdown("### 📊 Urban Forestry Analytics")
  ca1, ca2 = st.columns(2)

  with ca1:
    fig_species = px.pie(
        df,
        names="species",
        title="Canopy Distribution by Species",
        hole=0.4,
        color_discrete_sequence=["#059669", "#10B981", "#34D399", "#6EE7B7"],
    )
    fig_species.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#ECFDF5"),
    )
    st.plotly_chart(fig_species, use_container_width=True)

  with ca2:
    fig_co2 = px.bar(
        df,
        x="species",
        y="est_co2_kg_yr",
        title="Est. Annual CO₂ Offset (kg/year) per Species",
        color="health",
        color_discrete_sequence=["#10B981", "#34D399", "#A7F3D0"],
    )
    fig_co2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#ECFDF5"),
    )
    st.plotly_chart(fig_co2, use_container_width=True)
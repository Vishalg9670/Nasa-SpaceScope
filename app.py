import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ─────────────────────────────────────────
# PAGE SETTINGS
# ─────────────────────────────────────────
st.set_page_config(
    page_title="NASA Space Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS — Dark Space Theme
# ─────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #0a0a2a; color: white; }
    .stApp { background-color: #0a0a2a; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a4e, #0d0d30);
        border: 1px solid #00ffcc;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
    }
    .big-title {
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #7b2fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=150)
    st.markdown("## ⚙️ Settings")

    API_KEY = st.text_input(
        "🔑 NASA API Key",
        value="USjBuJsrY795MUVsvFTVUQoKNeXObqO8cHVCf5eF",
        type="password",
        help="api.nasa.gov se free key "
    )

    st.markdown("---")
    st.markdown("### 📅 Date Range (Asteroids)")
    days = st.slider("How many days of data do you need?", 1, 7, 7)

    st.markdown("---")
    st.markdown("### 🔍 Filter")
    show_dangerous = st.checkbox("Only Dangerous Asteroids", False)

    st.markdown("---")
    st.info("💡 Go to api.nasa.gov to get a free API key!")


    # ─────────────────────────────────────────
# MAIN TITLE
# ─────────────────────────────────────────
st.markdown('<p class="big-title">🚀 NASA Space Dashboard</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Real-time Space Data powered by NASA APIs</p>", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🌌 Space Image (APOD)", "☄️ Asteroid Tracker", "📊 Analytics"])

# ══════════════════════════════════════════
# TAB 1 — APOD (Daily Space Image)
# ══════════════════════════════════════════
with tab1:
    st.markdown("## 🌌 Astronomy Picture of the Day")

    col1, col2 = st.columns([1, 3])

    with col1:
        selected_date = st.date_input(
            "📅 choose the Date",
            value=datetime.now()
        )
        fetch_btn = st.button("🔭 Fetch Your Image ", use_container_width=True)

    if fetch_btn:  # ✅ sirf yahi rakho
        with st.spinner("🚀 Processing The NASA Image"):
            try:
                url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={selected_date}"
                response = requests.get(url)
                apod = response.json()

                if 'error' in apod:
                    st.error(f"❌ Error: {apod['error']['message']}")
                else:
                    col_img, col_info = st.columns([2, 1])

                    with col_img:
                        if apod.get('media_type') == 'image':
                            st.image(apod['url'], use_container_width=True, caption=apod['title'])  # ✅ fixed
                        else:
                            st.video(apod['url'])

                    with col_info:
                        st.markdown(f"### 🌟 {apod['title']}")
                        st.markdown(f"📅 **Date:** {apod['date']}")
                        if 'copyright' in apod:
                            st.markdown(f"📸 **Credit:** {apod['copyright']}")
                        st.markdown("---")
                        st.markdown("#### 📖 About")
                        st.markdown(f"<p style='color:#ccc; font-size:14px;'>{apod['explanation'][:500]}...</p>",
                                   unsafe_allow_html=True)
                        st.link_button("🔗 See The Full Image", apod['url'])

            except Exception as e:
                st.error(f"❌ No Image Available On the NASA Site On this Day: Please select Other Day ")



# ══════════════════════════════════════════
# TAB 2 — ASTEROID TRACKER
# ══════════════════════════════════════════
with tab2:
    st.markdown("## ☄️ Near Earth Asteroid Tracker")

    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

    with st.spinner(f"☄️ {days} din ke asteroids dhundh raha hoon..."):
        try:
            neo_url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={API_KEY}"
            neo_response = requests.get(neo_url)
            neo_data = neo_response.json()

            # Data extract karo
            asteroids = []
            for date, objects in neo_data['near_earth_objects'].items():
                for obj in objects:
                    asteroids.append({
                        'Name': obj['name'],
                        'Date': date,
                        'Min Diameter (km)': round(obj['estimated_diameter']['kilometers']['estimated_diameter_min'], 4),
                        'Max Diameter (km)': round(obj['estimated_diameter']['kilometers']['estimated_diameter_max'], 4),
                        'Speed (km/h)': round(float(obj['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']), 2),
                        'Miss Distance (km)': round(float(obj['close_approach_data'][0]['miss_distance']['kilometers']), 2),
                        'Dangerous': obj['is_potentially_hazardous_asteroid']
                    })

            df = pd.DataFrame(asteroids)

            if show_dangerous:
                df = df[df['Dangerous'] == True]

            # ── KPI Cards ──
            st.markdown("### 📊 Key Stats")
            k1, k2, k3, k4 = st.columns(4)

            k1.metric("☄️ Total Asteroids", len(df))
            k2.metric("⚠️ Dangerous", df['Dangerous'].sum())
            k3.metric("✅ Safe", len(df) - df['Dangerous'].sum())
            k4.metric("💨 Avg Speed (km/h)", f"{df['Speed (km/h)'].mean():,.0f}")

            st.markdown("---")

            # ── Table ──
            st.markdown("### 📋 Asteroid List")
            st.dataframe(
                df.style.applymap(
                    lambda x: 'background-color: #ff000033' if x == True else '',
                    subset=['Dangerous']
                ),
                use_container_width=True,
                height=300
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
            df = pd.DataFrame()



# ══════════════════════════════════════════
# TAB 3 — ANALYTICS & CHARTS
# ══════════════════════════════════════════
with tab3:
    st.markdown("## 📊 Asteroid Analytics")

    if 'df' in dir() and len(df) > 0:

        col1, col2 = st.columns(2)

        # Chart 1 — Speed vs Distance Scatter
        with col1:
            st.markdown("#### 🚀 Speed vs Distance")
            fig1 = px.scatter(
                df,
                x='Miss Distance (km)',
                y='Speed (km/h)',
                size='Max Diameter (km)',
                color='Dangerous',
                hover_name='Name',
                color_discrete_map={True: 'red', False: 'cyan'},
                template='plotly_dark',
                title='Speed vs Earth Distance'
            )
            fig1.update_layout(
                paper_bgcolor='#0a0a2a',
                plot_bgcolor='#0d0d30'
            )
            st.plotly_chart(fig1, use_container_width=True)

        # Chart 2 — Pie Chart
        with col2:
            st.markdown("#### ⚠️ Danger Analysis")
            danger_counts = df['Dangerous'].value_counts()
            fig2 = px.pie(
                values=danger_counts.values,
                names=['Safe ✅', 'Dangerous ⚠️'],
                color_discrete_sequence=['#00ffcc', '#ff4444'],
                template='plotly_dark',
                title='Safe vs Dangerous',
                hole=0.4
            )
            fig2.update_layout(paper_bgcolor='#0a0a2a')
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        # Chart 3 — Daily Count
        with col3:
            st.markdown("#### 📅 Daily Asteroid Count")
            daily = df.groupby('Date').size().reset_index(name='Count')
            fig3 = px.bar(
                daily, x='Date', y='Count',
                color='Count',
                color_continuous_scale='Viridis',
                template='plotly_dark',
                title='Asteroids Per Day'
            )
            fig3.update_layout(paper_bgcolor='#0a0a2a', plot_bgcolor='#0d0d30')
            st.plotly_chart(fig3, use_container_width=True)

        # Chart 4 — Size Distribution
        with col4:
            st.markdown("#### 📏 Size Distribution")
            fig4 = px.histogram(
                df, x='Max Diameter (km)',
                nbins=20,
                color='Dangerous',
                color_discrete_map={True: 'red', False: 'cyan'},
                template='plotly_dark',
                title='Asteroid Size Distribution'
            )
            fig4.update_layout(paper_bgcolor='#0a0a2a', plot_bgcolor='#0d0d30')
            st.plotly_chart(fig4, use_container_width=True)

        # Download Button
        st.markdown("---")
        st.markdown("### 💾 Data Download ")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 CSV Download ",
            data=csv,
            file_name=f"asteroids_{start_date}.csv",
            mime='text/csv',
            use_container_width=True
        )
    else:
        st.warning("⚠️ First, go to the Asteroid Tracker tab — load the data!")
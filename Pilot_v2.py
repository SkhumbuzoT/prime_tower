import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu

# BRAND COLORS
PRIMARY_BG = "#000000"  # Jet Black
ACCENT_TEAL = "#008080"  # Teal
ACCENT_GOLD = "#D4AF37"  # Gold
SECONDARY_NAVY = "#0A1F44"  # Navy Blue
WHITE = "#FFFFFF"  # White
LIGHT_GRAY = "#F8F9FA"  # Light Gray for backgrounds

# COLOR MAP FOR CHARTS
COLOR_MAP = {
    "Revenue": ACCENT_GOLD,
    "Cost": "#d32f2f",  # Red for costs
    "Profit": ACCENT_TEAL,
    "Fuel": "#ffa726",  # Orange
    "Efficiency": "#26a69a",  # Teal
    "Fixed Cost": "#9c27b0",  # Purple
    "Variable Cost": "#d32f2f",  # Red
    True: "#d32f2f",  # For flags like Service Due = True (Red)
    False: "#2e7d32"  # OK = Green
}

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

# PAGE CONFIG
st.set_page_config(
    page_title="PrimeTower Fleet Dashboard",
    page_icon=":truck:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM STYLES
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: {PRIMARY_BG};
        color: {WHITE};
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', sans-serif;
        color: {WHITE};
    }}

    .container {{
        padding: 1.5rem;
        background-color: {SECONDARY_NAVY};
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }}

    .metric-card {{
        background-color: {SECONDARY_NAVY};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid {ACCENT_TEAL};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6);
    }}
    .metric-card h3 {{
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: {LIGHT_GRAY};
        margin-bottom: 0.5rem;
    }}
    .metric-card p {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.8rem;
        color: {ACCENT_GOLD};
        margin: 0;
    }}

    .stTabs [role="tab"] {{
        font-family: 'Poppins', sans-serif;
        font-size: 1rem;
        color: {ACCENT_TEAL};
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {ACCENT_TEAL};
        color: {WHITE};
    }}

    [data-testid="stSidebar"] {{
        background-color: {SECONDARY_NAVY} !important;
        border-right: 2px solid {ACCENT_TEAL};
    }}

    .stButton>button {{
        background-color: {ACCENT_TEAL};
        color: {WHITE};
        border: none;
        border-radius: 8px;
        font-family: 'Poppins', sans-serif;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #006666;
        color: {WHITE};
    }}

    .dataframe {{
        background-color: {SECONDARY_NAVY} !important;
        border-radius: 8px;
    }}
    .dataframe td, .dataframe th {{
        background-color: {SECONDARY_NAVY} !important;
        color: {WHITE} !important;
        border: 1px solid {ACCENT_TEAL};
    }}

    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {PRIMARY_BG};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {ACCENT_TEAL};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #006666;
    }}

    .login-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80vh;
    }}
    .login-box {{
        background-color: {WHITE};
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        width: 400px;
        text-align: center;
    }}
    .login-box h2 {{
        color: {ACCENT_TEAL};
        font-family: 'Poppins', sans-serif;
        margin-bottom: 1.5rem;
    }}
    </style>
""", unsafe_allow_html=True)

# CHART THEME
pio.templates["prime_theme"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter", size=12, color=WHITE),
        title=dict(font=dict(size=16, color=ACCENT_TEAL)),
        paper_bgcolor=PRIMARY_BG,
        plot_bgcolor=SECONDARY_NAVY,
        margin=dict(l=30, r=20, t=50, b=30),
        xaxis=dict(
            showgrid=True,
            gridcolor="#333333",
            title_font=dict(size=12, family="Inter"),
            tickfont=dict(size=10, family="Inter"),
            automargin=True
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#333333",
            title_font=dict(size=12, family="Inter"),
            tickfont=dict(size=10, family="Inter"),
            automargin=True
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10, family="Inter")
        ),
        colorway=[ACCENT_TEAL, "#d32f2f", ACCENT_GOLD, "#ffa726", "#26a69a"]
    )
)
pio.templates.default = "prime_theme"

def apply_chart_style(fig, title, height=400):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Poppins", size=16, color=WHITE)),
        height=height,
        margin=dict(l=30, r=20, t=50, b=30),
        xaxis_title_font=dict(family="Inter", size=12),
        yaxis_title_font=dict(family="Inter", size=12),
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter", size=10)
        )
    )
    return fig

def kpi_card(title, value, emoji=None, delta=None):
    emoji_html = f'<span style="font-size: 1.2rem; margin-right: 8px; color: {ACCENT_TEAL};">{emoji}</span>' if emoji else ""
    delta_html = f"""
        <div style='font-size: 0.9rem; color: {"#2e7d32" if delta >= 0 else "#d32f2f"}; margin-top: 5px;'>
            {"↑" if delta >= 0 else "↓"} {abs(delta):.1f}% vs last period
        </div>
    """ if delta is not None else ""
    
    return f"""
        <div class="metric-card">
            <h3>{emoji_html}{title}</h3>
            <p>{value}</p>
            {delta_html}
        </div>
    """

# SAMPLE DATA
@st.cache_data
def load_sample_data():
    # Operations Data
    operations_data = {
        "Doc Type": ["Offloading", "Fuel", "Offloading", "Fuel"],
        "Ton Reg": [20, 100, 25, 80],
        "TruckID": ["TRK001", "TRK001", "TRK002", "TRK002"],
        "Date": ["2025-06-01", "2025-06-02", "2025-06-01", "2025-06-02"],
        "Route Code": ["RT001", "RT001", "RT002", "RT002"],
        "Slip Number": [1001, 1002, 1003, 1004]
    }
    operations = pd.DataFrame(operations_data)
    operations["Date"] = pd.to_datetime(operations["Date"])
    
    # Tracker Data
    tracker_data = {
        "Distance (km)": [500, 450, 600, 550],
        "TruckID": ["TRK001", "TRK001", "TRK002", "TRK002"],
        "Date": ["2025-06-01", "2025-06-02", "2025-06-01", "2025-06-02"],
        "TripID": [1, 2, 3, 4]
    }
    tracker = pd.DataFrame(tracker_data)
    tracker["Date"] = pd.to_datetime(tracker["Date"])
    
    # LOI Data
    loi_data = {
        "Route Code": ["RT001", "RT002"],
        "Loading Point": ["Cape Town", "Johannesburg"],
        "Offloading Point": ["Durban", "Pretoria"],
        "Distance": [1200, 300],
        "Rate per ton": [1500.0, 1000.0],
        "Fuel per litre": [25.0, 25.0],
        "Estimated loads per day": [2, 3]
    }
    loi = pd.DataFrame(loi_data)
    
    # Truck Pack Data
    truck_pak_data = {
        "Registration": ["CA123", "GP456"],
        "Driver Name": ["John Doe", "Jane Smith"],
        "Prime Mover": ["Volvo", "Mercedes"],
        "Series": ["FH16", "Actros"],
        "Year": [2019, 2020],
        "Trailer 1": ["TRL001", "TRL003"],
        "Trailer 2": ["TRL002", "TRL004"],
        "TruckID": ["TRK001", "TRK002"],
        "Vehicle License Expiry": ["2025-12-31", "2025-11-30"],
        "Driver License Expiry": ["2026-06-30", "2026-03-31"],
        "Last Service": [150000, 120000],
        "GIT Insurance Expiry": ["2025-10-31", "2025-09-30"],
        "Last Service Date": ["2025-03-01", "2025-02-15"],
        "Current Mileage": [160000, 130000]
    }
    truck_pak = pd.DataFrame(truck_pak_data)
    truck_pak["Vehicle License Expiry"] = pd.to_datetime(truck_pak["Vehicle License Expiry"])
    truck_pak["Driver License Expiry"] = pd.to_datetime(truck_pak["Driver License Expiry"])
    truck_pak["Last Service Date"] = pd.to_datetime(truck_pak["Last Service Date"])
    truck_pak["GIT Insurance Expiry"] = pd.to_datetime(truck_pak["GIT Insurance Expiry"])
    
    # Vehicle Cost Schedule Data
    vcs_data = {
        "TruckID": ["TRK001", "TRK002"],
        "Vehicle Type": ["34T Side-T", "34T Flatbed"],
        "Finance Cost (R/month)": [20000, 18000],
        "Insurance (R/month)": [5000, 4500],
        "License (R/month)": [1000, 1000],
        "Driver Salary (R/month)": [15000, 14000],
        "Fuel Cost (R/km)": [10.0, 9.5],
        "Maintenance Cost (R/km)": [2.0, 1.8],
        "Tyres (R/km)": [1.5, 1.4],
        "Daily Fixed Cost (R/day)": [1000, 900]
    }
    vcs = pd.DataFrame(vcs_data)
    
    return operations, tracker, loi, truck_pak, vcs

# Load sample data
try:
    operations, tracker, loi, truck_pak, vcs = load_sample_data()
except Exception as e:
    st.error(f"Error loading sample data: {str(e)}")
    st.stop()

# AUTHENTICATION
def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div class="login-box">
                <h2>🔐 PrimeTower Login</h2>
            </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", use_container_width=True):
            authenticate(username, password)
        
        st.markdown("</div>", unsafe_allow_html=True)

def authenticate(username, password):
    users = {"admin": "1234", "user1": "pass123"}  # In production, use secure auth
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.first_visit = True
        st.rerun()
    else:
        st.error("Invalid credentials")

if not st.session_state.logged_in:
    show_login()
    st.stop()

# DATA PREP
operations["Date_only"] = operations["Date"].dt.date
operations["Year-Month"] = operations["Date"].dt.to_period("M").astype(str)
operations["Month_Display"] = operations["Date"].dt.strftime("%B %Y")
month_mapping = operations[["Year-Month", "Month_Display"]].drop_duplicates()
month_dict = dict(zip(month_mapping["Month_Display"], month_mapping["Year-Month"]))
available_months_display = sorted(month_dict.keys(), key=lambda m: month_dict[m])

# SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <h4 style='color: {ACCENT_TEAL};'>Welcome, {st.session_state.username}</h4>
        </div>
    """, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Home", "Financials", "Operations", "Fuel", "Maintenance", "Alerts"],
        icons=["house", "cash-stack", "speedometer", "fuel-pump", "tools", "bell"],
        menu_icon="cast",
        default_index=0 if st.session_state.first_visit else 1,
        styles={
            "container": {"padding": "5px", "background-color": SECONDARY_NAVY},
            "icon": {"color": ACCENT_GOLD, "font-size": "18px"},
            "nav-link": {
                "color": WHITE,
                "font-size": "15px",
                "text-align": "left",
                "margin": "5px",
                "--hover-color": ACCENT_TEAL,
            },
            "nav-link-selected": {"background-color": ACCENT_TEAL},
        }
    )
    
    with st.form("filters_form"):
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            selected_month_display = st.selectbox(
                "Month", 
                available_months_display, 
                index=len(available_months_display)-1
            )
        with col2:
            selected_truck = st.selectbox(
                "Truck", 
                ["All"] + sorted(truck_pak["TruckID"].unique()), 
                index=0
            )
        with col3:
            selected_route = st.selectbox(
                "Route", 
                ["All"] + sorted(loi["Route Code"].unique()), 
                index=0
            )
        submitted = st.form_submit_button("Apply Filters")
        
        if submitted:
            st.session_state.month_filter = selected_month_display
            st.session_state.truck_filter = selected_truck
            st.session_state.route_filter = selected_route
    
    selected_month_display = st.session_state.get("month_filter", available_months_display[-1])
    selected_truck = st.session_state.get("truck_filter", "All")
    selected_route = st.session_state.get("route_filter", "All")
    
    if st.button("Logout", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

selected_month = month_dict[selected_month_display]

# APPLY FILTERS
filtered_ops = operations.copy()
if selected_truck != "All":
    filtered_ops = filtered_ops[filtered_ops["TruckID"] == selected_truck]
if selected_route != "All":
    filtered_ops = filtered_ops[filtered_ops["Route Code"] == selected_route]
filtered_ops = filtered_ops[filtered_ops["Year-Month"] == selected_month]

# Calculate previous period for delta comparisons
prev_month = (pd.to_datetime(selected_month) - pd.DateOffset(months=1)).strftime("%Y-%m")
prev_month_filtered = operations[operations["Year-Month"] == prev_month]

# HOME TAB
if selected == "Home":
    st.session_state.first_visit = False
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: {ACCENT_TEAL};'>🚀 PrimeTower Fleet Dashboard</h1>
            <p style='font-size: 1.2rem; color: {LIGHT_GRAY};'>
                Real-time insights for smarter trucking operations
            </p>
        </div>
    """.format(ACCENT_TEAL=ACCENT_TEAL, LIGHT_GRAY=LIGHT_GRAY), unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            **PrimeTower** empowers fleet owners to manage trucks like a business, not guesswork. 
            Track trips, fuel, maintenance, and profitability in real-time with a clean, intuitive interface.
        """)
    with col2:
        st.markdown(f"""
            <div style='text-align: center;'>
                <span style='font-size: 3rem;'>🚛</span>
                <p style='color: {ACCENT_GOLD};'>Your Fleet, Your Control</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## 👤 Who is PrimeTower for?")
    st.markdown("""
    - 🛻 **Truck Owners** (1–50 trucks)  
    - 🤝 **Subcontracted Transporters**  
    - 🧾 **SME Logistics Coordinators**  
    - 🔍 **Fleet Managers** needing better data  
    """)
    
    st.markdown("## 🔑 Key Features")
    st.markdown("""
    | 🛠 Feature | 💬 Description |
    |------------|----------------|
    | 📍 **Trip Tracking** | Real-time visibility into trips, distances, loads |
    | 💰 **Profit Analysis** | Know your margin per truck, trip, and route |
    | ⛽ **Fuel Usage Insights** | Spot fuel anomalies and consumption patterns |
    | 🔧 **Maintenance Reminders** | Get alerts before services and renewals are missed |
    | 🧮 **Fleet Cost Dashboard** | Compare truck performance and total cost/km |
    """)
    
    st.markdown(f"""
        <div style='text-align: center; margin-top: 2rem;'>
            <a href='#' style='background-color: {ACCENT_TEAL}; color: {WHITE}; padding: 0.8rem 1.5rem; 
                border-radius: 8px; text-decoration: none; font-family: Poppins, sans-serif;'>
                Explore Dashboard
            </a>
        </div>
    """, unsafe_allow_html=True)

# FINANCIALS TAB
elif selected == "Financials":
    st.markdown("## 📊 Financials Overview")
    
    try:
        cost_df = filtered_ops.copy()
        cost_df = cost_df.merge(loi[["Route Code", "Rate per ton"]], on="Route Code", how="left")
        cost_df = cost_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        cost_df = cost_df.merge(tracker[["TruckID", "Distance (km)"]], on="TruckID", how="left")
        cost_df = cost_df.merge(vcs[["TruckID", "Fuel Cost (R/km)", "Maintenance Cost (R/km)", 
                                     "Tyres (R/km)", "Daily Fixed Cost (R/day)"]], on="TruckID", how="left")
        
        cost_df["Revenue (R)"] = cost_df["Ton Reg"] * cost_df["Rate per ton"]
        cost_df["Variable Cost (R)"] = cost_df["Distance (km)"] * (
            cost_df["Fuel Cost (R/km)"] + cost_df["Maintenance Cost (R/km)"] + cost_df["Tyres (R/km)"]
        )
        cost_df["Total Cost (R)"] = cost_df["Variable Cost (R)"] + cost_df["Daily Fixed Cost (R/day)"]
        cost_df["Profit (R)"] = cost_df["Revenue (R)"] - cost_df["Total Cost (R)"]
        
        total_revenue = cost_df["Revenue (R)"].sum()
        prev_revenue = prev_month_filtered["Ton Reg"].sum() * loi["Rate per ton"].mean() if not prev_month_filtered.empty else 0
        revenue_delta = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue != 0 else 0
        
        total_cost = cost_df["Total Cost (R)"].sum()
        fixed_cost_mean = vcs["Daily Fixed Cost (R/day)"].mean()
        prev_cost = len(prev_month_filtered) * fixed_cost_mean if not prev_month_filtered.empty else 0
        cost_delta = ((total_cost - prev_cost) / prev_cost * 100) if prev_cost != 0 else 0
        
        avg_cost_per_km = (cost_df["Total Cost (R)"] / cost_df["Distance (km)"]).mean()
        profitable_trucks = cost_df[cost_df["Profit (R)"] > 0]["TruckID"].nunique()
        total_trucks = cost_df["TruckID"].nunique()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(kpi_card("Total Revenue", f"R{total_revenue:,.2f}", emoji="💰", delta=revenue_delta), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Total Cost", f"R{total_cost:,.2f}", emoji="📉", delta=cost_delta), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Avg Cost per KM", f"R{avg_cost_per_km:,.2f}", emoji="🛣️"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("Profitable Trucks", f"{profitable_trucks}/{total_trucks}", emoji="📈"), unsafe_allow_html=True)
        
        st.caption(f"Data from {cost_df['Date'].min().date()} to {cost_df['Date'].max().date()}")
        
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                grouped_cost = cost_df.groupby("TruckID").agg({
                    "Revenue (R)": "sum",
                    "Variable Cost (R)": "sum",
                    "Daily Fixed Cost (R/day)": "sum",
                    "Total Cost (R)": "sum",
                    "Profit (R)": "sum"
                }).reset_index()
                df_plot = grouped_cost[["TruckID", "Variable Cost (R)", "Daily Fixed Cost (R/day)"]].melt(
                    id_vars="TruckID",
                    var_name="Cost Type",
                    value_name="Cost (R)"
                )
                fig = px.bar(
                    df_plot,
                    x="TruckID",
                    y="Cost (R)",
                    color="Cost Type",
                    barmode="stack",
                    title="Cost Structure by Truck",
                    color_discrete_map=COLOR_MAP
                )
                fig = apply_chart_style(fig, "Cost Structure by Truck")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig2 = px.bar(
                    grouped_cost,
                    x="TruckID",
                    y="Profit (R)",
                    color="Profit (R)",
                    color_continuous_scale=[(0, "#d32f2f"), (1, ACCENT_TEAL)],
                    title="Profit by Truck"
                )
                fig2 = apply_chart_style(fig2, "Profit by Truck")
                st.plotly_chart(fig2, use_container_width=True)
        
        with st.container():
            route_profit = cost_df.groupby("Route Code").agg({
                "Revenue (R)": "mean",
                "Total Cost (R)": "mean",
                "Profit (R)": "mean",
                "Ton Reg": "sum"
            }).reset_index()
            fig3 = px.scatter(
                route_profit,
                x="Revenue (R)",
                y="Total Cost (R)",
                size="Ton Reg",
                color="Profit (R)",
                hover_name="Route Code",
                title="Route Profitability (Bubble Size = Total Tons)",
                color_continuous_scale=[(0, "#d32f2f"), (1, ACCENT_TEAL)],
                size_max=40
            )
            fig3.add_shape(
                type="line", line=dict(dash="dash", color=WHITE),
                x0=0, y0=0, x1=route_profit["Revenue (R)".max()*1.1,
                y1=route_profit["Revenue (R)".max()*1.1
            ]
            fig3 = apply_chart_style(fig3, "Route Profitability")
            st.plotly_chart(fig3, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error in Financials tab: {str(e)}")

# OPERATIONS TAB
elif selected == "Operations":
    st.markdown("## 🚛 Operations Dashboard")
    
    try:
        ops_df = filtered_ops.copy()
        if "Distance" in loi.columns:
            ops_df = ops_df.merge(loi[["Route Code", "Distance"]], on="Route Code", how="left")
        else:
            st.warning("Column 'Distance' not found in LOI data. Using default distance.")
            ops_df["Distance"] = 0
        
        ops_df = ops_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        
        active_trucks = ops_df["TruckID"].nunique()
        total_tons = ops_df[ops_df["Doc Type"] == "Offloading"]["Ton Reg"].sum()
        total_km = ops_df["Distance"].sum() if "Distance" in ops_df.columns else 0
        route_count = ops_df["Route Code"].nunique()
        
        prev_active_trucks = prev_month_filtered["TruckID"].nunique() if not prev_month_filtered.empty else 0
        active_trucks_delta = ((active_trucks - prev_active_trucks) / prev_active_trucks * 100) if prev_active_trucks != 0 else 0
        prev_tons = prev_month_filtered[prev_month_filtered["Doc Type"] == "Offloading"]["Ton Reg"].sum() if not prev_month_filtered.empty else 0
        tons_delta = ((total_tons - prev_tons) / prev_tons * 100) if prev_tons != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(kpi_card("Active Trucks", active_trucks, emoji="🚚", delta=active_trucks_delta), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Total Tons Moved", f"{total_tons:,.1f}", emoji="📦", delta=tons_delta), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Distance Covered", f"{total_km:,.0f} km", emoji="🛣️"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("Routes Used", route_count, emoji="🗺️"), unsafe_allow_html=True)
        
        st.caption(f"Data from {ops_df['Date'].min().date()} to {ops_df['Date'].max().date()}")
        
        with st.container():
            daily_tons = ops_df[ops_df["Doc Type"] == "Offloading"].groupby("Date_only")["Ton Reg"].sum().reset_index()
            fig1 = px.line(
                daily_tons,
                x="Date_only",
                y="Ton Reg",
                title="Daily Tons Moved",
                markers=True,
                line_shape="spline"
            )
            fig1.update_traces(line_color=ACCENT_TEAL)
            fig1 = apply_chart_style(fig1, "Daily Tons Moved")
            st.plotly_chart(fig1, use_container_width=True)
        
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                tons_per_truck = ops_df.groupby(["TruckID", "Driver Name"])["Ton Reg"].sum().reset_index()
                fig2 = px.bar(
                    tons_per_truck,
                    x="TruckID",
                    y="Ton Reg",
                    color="Ton Reg",
                    hover_name="Driver Name",
                    title="Total Tons by Truck",
                    color_continuous_scale=[(0, SECONDARY_NAVY), (1, ACCENT_TEAL)]
                )
                fig2 = apply_chart_style(fig2, "Total Tons by Truck")
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                trips_per_truck = ops_df[ops_df["Doc Type"] == "Offloading"].groupby(["TruckID", "Driver Name"]).size().reset_index(name="Trips")
                fig3 = px.bar(
                    trips_per_truck,
                    x="TruckID",
                    y="Trips",
                    color="Trips",
                    hover_name="Driver Name",
                    title="Total Trips by Truck",
                    color_continuous_scale=[(0, SECONDARY_NAVY), (1, ACCENT_GOLD)]
                )
                fig3 = apply_chart_style(fig3, "Total Trips by Truck")
                st.plotly_chart(fig3, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error in Operations tab: {str(e)}")

# FUEL TAB
elif selected == "Fuel":
    st.markdown("## ⛽ Fuel Efficiency Dashboard")
    
    try:
        fuel_df = filtered_ops[filtered_ops["Doc Type"] == "Fuel"].copy()
        fuel_df = fuel_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        if "Distance" in loi.columns:
            fuel_df = fuel_df.merge(loi[["Route Code", "Distance"]], on="Route Code", how="left")
        else:
            st.warning("Column 'Distance' not found in LOI data. Using default distance.")
            fuel_df["Distance"] = 0
        
        fuel_df["Fuel Efficiency (km/L)"] = fuel_df["Distance"] / fuel_df["Ton Reg"]
        fuel_df["Fuel Cost per km (R/km)"] = fuel_df["Ton Reg"] / fuel_df["Distance"]
        
        avg_efficiency = fuel_df["Fuel Efficiency (km/L)"].mean()
        total_fuel_used = fuel_df["Ton Reg"].sum()
        fuel_cost_per_km = fuel_df["Fuel Cost per km (R/km)"].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(kpi_card("Avg Fuel Efficiency", f"{avg_efficiency:.2f} km/L", emoji="🚀"), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Total Fuel Used", f"{total_fuel_used:,.1f} L", emoji="⛽"), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Avg Fuel Cost per km", f"R{fuel_cost_per_km:.2f}", emoji="💸"), unsafe_allow_html=True)
        
        st.caption(f"Data from {fuel_df['Date'].min().date()} to {fuel_df['Date'].max().date()}")
        
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                daily_eff = fuel_df.groupby("Date_only")["Fuel Efficiency (km/L)"].mean().reset_index()
                fig1 = px.line(
                    daily_eff,
                    x="Date_only",
                    y="Fuel Efficiency (km/L)",
                    title="Daily Fuel Efficiency",
                    markers=True,
                    line_shape="spline"
                )
                fig1.update_traces(line_color=ACCENT_TEAL)
                fig1.add_hline(y=avg_efficiency, line_dash="dash", line_color=ACCENT_GOLD, 
                              annotation_text=f"Avg: {avg_efficiency:.2f} km/L")
                fig1 = apply_chart_style(fig1, "Daily Fuel Efficiency")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                truck_eff = fuel_df.groupby(["TruckID", "Driver Name"])["Fuel Efficiency (km/L)"].mean().reset_index()
                fig2 = px.bar(
                    truck_eff,
                    x="TruckID",
                    y="Fuel Efficiency (km/L)",
                    color="Fuel Efficiency (km/L)",
                    hover_name="Driver Name",
                    title="Fuel Efficiency by Truck",
                    color_continuous_scale=[(0, "#d32f2f"), (0.5, "#ffa726"), (1, ACCENT_TEAL)]
                )
                fig2 = apply_chart_style(fig2, "Fuel Efficiency by Truck")
                st.plotly_chart(fig2, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error in Fuel tab: {str(e)}")

# MAINTENANCE TAB
elif selected == "Maintenance":
    st.markdown("## 🔧 Maintenance Dashboard")
    
    try:
        maint_df = truck_pak.copy()
        maint_df["KM Since Service"] = maint_df["Current Mileage"] - maint_df["Last Service"]
        maint_df["Service Due"] = maint_df["KM Since Service"] > 10000
        
        today = pd.to_datetime("today").normalize()
        expiry_fields = {
            "Vehicle License Expiry": "License Expiry",
            "Driver License Expiry": "Driver License",
            "GIT Insurance Expiry": "GIT Insurance"
        }
        
        for col, label in expiry_fields.items():
            maint_df[f"{label} Days Left"] = (maint_df[col] - today).dt.days
            maint_df[f"{label} Expiring"] = maint_df[f"{label} Days Left"].le(30)
        
        overdue_services = maint_df["Service Due"].sum()
        license_expiring = maint_df["License Expiry Expiring"].sum()
        driver_expiring = maint_df["Driver License Expiring"].sum()
        git_expiring = maint_df["GIT Insurance Expiring"].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(kpi_card("Overdue Services", int(overdue_services), emoji="🔧"), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Vehicle Licenses Expiring", license_expiring, emoji="🚗"), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Driver Licenses Expiring", driver_expiring, emoji="🧑‍✈️"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("GIT Insurance Expiring", git_expiring, emoji="🛡️"), unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.bar(
                    maint_df.sort_values("KM Since Service", ascending=False),
                    x="TruckID",
                    y="KM Since Service",
                    color="Service Due",
                    color_discrete_map=COLOR_MAP,
                    title="KM Since Last Service",
                    hover_data=["Current Mileage", "Last Service"]
                )
                fig1.add_hline(y=10000, line_dash="dash", line_color=ACCENT_GOLD, 
                              annotation_text="Service Threshold")
                fig1 = apply_chart_style(fig1, "KM Since Last Service")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                expiring_df = maint_df[
                    maint_df["License Expiry Expiring"] |
                    maint_df["Driver License Expiring"] |
                    maint_df["GIT Insurance Expiring"]
                ]
                if not expiring_df.empty:
                    date_cols = ["Vehicle License Expiry", "Driver License Expiry", "GIT Insurance Expiry"]
                    days_matrix = expiring_df[date_cols].apply(lambda col: (col - today).dt.days)
                    days_matrix = days_matrix.clip(lower=0, upper=30)
                    fig2 = go.Figure(data=go.Heatmap(
                        z=days_matrix.values,
                        x=days_matrix.columns,
                        y=expiring_df["TruckID"],
                        colorscale=[[0, "darkred"], [0.2, "orangered"], [0.5, "orange"], [0.8, "yellow"], [1, "lightyellow"]],
                        colorbar=dict(title="Days to Expiry", tickvals=[0, 10, 20, 30], ticktext=["0 (Expired)", "10", "20", "30+"]),
                        hoverongaps=False,
                        hovertemplate="TruckID %{y}<br>%{x}: %{z} days"
                    ))
                    fig2 = apply_chart_style(fig2, "Expiring Licenses & Insurance")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.success("✅ No licenses or insurance expiring soon.")
    
    except Exception as e:
        st.error(f"Error in Maintenance tab: {str(e)}")

# ALERTS TAB
elif selected == "Alerts":
    st.markdown("## 🔔 Actionable Alerts")
    
    try:
        cost_df = filtered_ops.copy()
        cost_df = cost_df.merge(loi[["Route Code", "Rate per ton"]], on="Route Code", how="left")
        cost_df = cost_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        cost_df = cost_df.merge(tracker[["TruckID", "Distance (km)"]], on="TruckID", how="left")
        cost_df = cost_df.merge(vcs[["TruckID", "Fuel Cost (R/km)", "Maintenance Cost (R/km)", 
                                     "Tyres (R/km)", "Daily Fixed Cost (R/day)"]], on="TruckID", how="left")
        
        cost_df["Revenue (R)"] = cost_df["Ton Reg"] * cost_df["Rate per ton"]
        cost_df["Variable Cost (R)"] = cost_df["Distance (km)"] * (
            cost_df["Fuel Cost (R/km)"] + cost_df["Maintenance Cost (R/km)"] + cost_df["Tyres (R/km)"]
        )
        cost_df["Total Cost (R)"] = cost_df["Variable Cost (R)"] + cost_df["Daily Fixed Cost (R/day)"]
        cost_df["Profit (R)"] = cost_df["Revenue (R)"] - cost_df["Total Cost (R)"]
        
        st.markdown("### 🌟 Top Performers")
        col1, col2 = st.columns(2)
        with col1:
            profitable_truck = cost_df.groupby(["TruckID", "Driver Name"])["Profit (R)"].sum().nlargest(1).reset_index()
            if not profitable_truck.empty:
                truck = profitable_truck.iloc[0]
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>🚛 Most Profitable Truck</h3>
                        <p>{truck['TruckID']} ({truck['Driver Name']})</p>
                        <p style='font-size: 1.5rem; color: {ACCENT_TEAL};'>R{truck['Profit (R)']:,.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            efficient_route = cost_df.groupby("Route Code")["Profit (R)"].mean().nlargest(1).reset_index()
            if not efficient_route.empty:
                route = efficient_route.iloc[0]
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>🛣️ Most Profitable Route</h3>
                        <p>{route['Route Code']}</p>
                        <p style='font-size: 1.5rem; color: {ACCENT_TEAL};'>R{route['Profit (R)']:,.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("### ⚡ Optimization Opportunities")
        fuel_df = filtered_ops[filtered_ops["Doc Type"] == "Fuel"].copy()
        if "Distance" in loi.columns:
            fuel_df = fuel_df.merge(loi[["Route Code", "Distance"]], on="Route Code", how="left")
        else:
            fuel_df["Distance"] = 0
        fuel_df["Fuel Efficiency (km/L)"] = fuel_df["Distance"] / fuel_df["Ton Reg"]
        inefficient_trucks = fuel_df.groupby(["TruckID", "Driver Name"])["Fuel Efficiency (km/L)"].mean().nsmallest(3).reset_index()
        
        if not inefficient_trucks.empty:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>⛽ Least Fuel-Efficient Trucks</h3>
                    <table style='width: 100%; border-collapse: collapse;'>
                        <tr style='border-bottom: 1px solid {ACCENT_TEAL};'>
                            <th style='text-align: left; padding: 8px;'>Truck</th>
                            <th style='text-align: left; padding: 8px;'>Driver</th>
                            <th style='text-align: right; padding: 8px;'>Efficiency</th>
                        </tr>
                        {"".join([f"<tr><td style='padding: 8px;'>{row['TruckID']}</td><td style='padding: 8px;'>{row['Driver Name']}</td><td style='padding: 8px; text-align: right;'>{row['Fuel Efficiency (km/L)']:.2f} km/L</td></tr>" for _, row in inefficient_trucks.iterrows()])}
                    </table>
                </div>
            """, unsafe_allow_html=True)
        
        loss_routes = cost_df.groupby("Route Code")["Profit (R)"].sum().nsmallest(3).reset_index()
        if not loss_routes.empty:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>🔴 Top Loss-Making Routes</h3>
                    <table style='width: 100%; border-collapse: collapse;'>
                        <tr style='border-bottom: 1px solid {ACCENT_TEAL};'>
                            <th style='text-align: left; padding: 8px;'>Route</th>
                            <th style='text-align: right; padding: 8px;'>Loss</th>
                        </tr>
                        {"".join([f"<tr><td style='padding: 8px;'>{row['Route Code']}</td><td style='padding: 8px; text-align: right;'>R{abs(row['Profit (R)']):,.2f}</td></tr>" for _, row in loss_routes.iterrows()])}
                    </table>
                </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error in Alerts tab: {str(e)}")

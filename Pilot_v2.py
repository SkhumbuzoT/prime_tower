# DEPENDENCIES
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from datetime import datetime, timedelta
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
import openai
import requests
from streamlit_option_menu import option_menu
import os
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
import google.generativeai as genai

# BRAND COLORS
PRIMARY_BG = "#000000"  # Jet Black
ACCENT_TEAL = "#008080"  # Teal
ACCENT_GOLD = "#D4AF37"  # Gold
SECONDARY_NAVY = "#0A1F44"  # Navy Blue
WHITE = "#FFFFFF"  # White
LIGHT_GRAY = "#F8F9FA"  # Light Gray for backgrounds

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True
if "use_demo" not in st.session_state:
    st.session_state.use_demo = False

# PAGE CONFIG - Should only be called once per session
st.set_page_config(
    page_title="PrimeTower Fleet Dashboard",
    page_icon="prime_tower/prime_logo.png",
    layout="wide"
)

# CUSTOM STYLES
st.markdown(f"""
    <style>
    .login-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80vh;
    }}
    .login-box {{
        background-color: {SECONDARY_NAVY};
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid {ACCENT_TEAL};
        width: 400px;
        text-align: center;
    }}
    </style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
def show_login():
    """Display centered login form"""
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container():
            st.markdown(f"""
                <div class="login-box">
                    <h2 style='color:{ACCENT_TEAL}; margin-bottom: 1.5rem;'>🔐 Prime Tower Login</h2>
            """, unsafe_allow_html=True)
            
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary", use_container_width=True):
                authenticate(username, password)
            
            st.markdown("</div>", unsafe_allow_html=True)

def authenticate(username, password):
    """Authenticate user"""
    users = {"admin": "1234", "user1": "pass123"}  # In production, use proper auth
    
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.first_visit = True
        st.session_state.use_demo = False
        st.rerun()
    else:
        st.error("Invalid credentials")

# Only show the rest if logged in
if not st.session_state.logged_in:
    show_login()
    st.stop()  # Stop execution if not logged in

# --- MAIN APP CONTENT ---

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

@st.cache_resource
def get_gsheet_client():
    creds_dict = {
        "type": st.secrets["gcp_service_account"]["type"],
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": st.secrets["gcp_service_account"]["private_key"],
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
    }
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    return gspread.authorize(creds)

@st.cache_data
def load_sheet_data():
    client = get_gsheet_client()
    sheet = client.open_by_key("1QYHK9DoiBjJPLrQlovHxDkRuv4xImwtzbokul_rOdjI").worksheet("Sheet1")
    return pd.DataFrame(sheet.get_all_records())

@st.cache_data
def get_resized_image(image_path):
    buffered = BytesIO()
    Image.open(image_path).resize((100, 100)).save(buffered, format="PNG")
    return buffered.getvalue()

# Additional custom styles
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');

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
        padding: 5px;
        background-color: {SECONDARY_NAVY};
    }}
    .metric-card {{
        background-color: {SECONDARY_NAVY};
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid {ACCENT_TEAL};
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.75);
    }}
    .metric-card h3 {{
        font-weight: 600;
        font-size: 1rem;
        color: #94A3B8;
        margin-bottom: 0.3rem;
    }}
    .metric-card p {{
        font-size: 2.1rem;
        font-weight: 700;
        color: {ACCENT_GOLD};
        margin: 0;
    }}
    .stTabs [role="tab"] {{
        font-family: 'Poppins', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: {ACCENT_TEAL};
        padding: 10px 15px;
        border-radius: 5px;
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
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #006666;
        color: {WHITE};
    }}
    .dataframe {{
        background-color: {SECONDARY_NAVY} !important;
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
    </style>
""", unsafe_allow_html=True)

# Apply chart theme
pio.templates["prime_theme"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter", size=13, color=WHITE),
        title=dict(font=dict(size=16, color=ACCENT_TEAL)),
        paper_bgcolor=PRIMARY_BG,
        plot_bgcolor=SECONDARY_NAVY,
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor="#333333",
            title_font=dict(size=13),
            automargin=True
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#333333",
            title_font=dict(size=13),
            automargin=True
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        colorway=[ACCENT_TEAL, "#d32f2f", ACCENT_GOLD, "#ffa726", "#26a69a"]
    )
)
pio.templates.default = "prime_theme"

def apply_chart_style(fig, title, height=400):
    fig.update_layout(
        title=dict(text=title, font=dict(color=WHITE)),
        height=height,
        title_font_size=16,
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis_title=None,
        yaxis_title=None,
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        )
    )
    return fig

def kpi_card(title, value, icon=None, emoji=None, delta=None):
    icon_html = f'<i class="bi bi-{icon}" style="font-size: 1.2rem; margin-right: 6px; color: {ACCENT_TEAL};"></i>' if icon else ""
    emoji_html = f'{emoji} ' if emoji else ""
    
    delta_html = ""
    if delta is not None:
        delta_color = "#2e7d32" if delta >= 0 else "#d32f2f"
        delta_icon = "↑" if delta >= 0 else "↓"
        delta_html = f"""<div style='font-size:12px; color:{delta_color}; margin-top:5px;'>
                            {delta_icon} {abs(delta):.1f}% vs last period
                         </div>"""
    
    return f"""
        <div class="metric-card">
            <h5 style='margin:0; font-size:15px; color:#f1f1f1;'>{icon_html}{emoji_html}{title}</h5>
            <p style='margin:5px 0 0; font-size:20px; font-weight:bold;'>{value}</p>
            {delta_html}
        </div>
    """

# LOAD DATA
@st.cache_data
def load_data_from_gsheet():
    if st.session_state.get("use_demo", False):
        @st.cache_data
        def load_demo_data():
            operations = pd.read_csv("data/demo_operations.csv")
            tracker = pd.read_csv("data/demo_tracker.csv")
            loi = pd.read_csv("data/demo_loi.csv")
            truck_pak = pd.read_csv("data/demo_truck_pak.csv")
            vcs = pd.read_csv("data/demo_vcs.csv")
            return operations, tracker, loi, truck_pak, vcs
        return load_demo_data()
    else:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds_dict = {
            "type": st.secrets["gcp_service_account"]["type"],
            "project_id": st.secrets["gcp_service_account"]["project_id"],
            "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
            "private_key": st.secrets["gcp_service_account"]["private_key"],
            "client_email": st.secrets["gcp_service_account"]["client_email"],
            "client_id": st.secrets["gcp_service_account"]["client_id"],
            "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
            "token_uri": st.secrets["gcp_service_account"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
        }
        
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        def get_worksheet_df(sheet_name):
            return pd.DataFrame(client.open_by_key("1QYHK9DoiBjJPLrQlovHxDkRuv4xImwtzbokul_rOdjI")
                              .worksheet(sheet_name).get_all_records())
        
        return (
            get_worksheet_df("operations"),
            get_worksheet_df("tracker"),
            get_worksheet_df("loi"),
            get_worksheet_df("truck_pak"),
            get_worksheet_df("vehicle_cost_schedule")
        )

# Load the data
operations, tracker, loi, truck_pak, vcs = load_data_from_gsheet()

# --- DATA PREP ---
operations["Date"] = pd.to_datetime(operations["Date"])
operations["Date_only"] = operations["Date"].dt.date
operations["Year-Month"] = operations["Date"].dt.to_period("M").astype(str)
operations["Month_Display"] = operations["Date"].dt.strftime("%B %Y")
month_mapping = operations[["Year-Month", "Month_Display"]].drop_duplicates()
month_dict = dict(zip(month_mapping["Month_Display"], month_mapping["Year-Month"]))
available_months_display = sorted(month_dict.keys(), key=lambda m: month_dict[m])

# Navigation menu - in sidebar
with st.sidebar:
    try:
        st.image("prime_tower/prime_logo.png", width=100)
    except:
        st.warning("Logo image not found")
    
    st.markdown(f"""
        <div style='text-align:center; margin-bottom:1rem;'>
            <h4 style='color:{ACCENT_TEAL};'>Welcome, {st.session_state.username}</h4>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Home", "Financials", "Operations", 
                "Fuel", "Maintenance", "Alerts"],
        icons=["house", "cash-stack", "speedometer", 
              "fuel-pump", "tools", "notification"],
        menu_icon="cast",
        default_index=0 if st.session_state.first_visit else 1,
        styles={
            "container": {"padding": "5px", "background-color": SECONDARY_NAVY},
            "icon": {"color": ACCENT_GOLD, "font-size": "20px"},
            "nav-link": {
                "color": WHITE,
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "--hover-color": ACCENT_TEAL,
            },
            "nav-link-selected": {"background-color": ACCENT_TEAL},
        }
    )
    
    with st.sidebar:
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
        # Only update filters on submit
        if submitted:
            st.session_state.month_filter = selected_month_display
            st.session_state.truck_filter = selected_truck
            st.session_state.route_filter = selected_route
        # Set defaults if not submitted
        selected_month_display = st.session_state.get("month_filter", available_months_display[-1])
        selected_truck = st.session_state.get("truck_filter", "All")
        selected_route = st.session_state.get("route_filter", "All")
    
    
    # Logout button
    if st.button("Logout", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()



# Set defaults if not submitted
#selected_month_display = st.session_state.get("month_filter", available_months_display[-1])
#selected_truck = st.session_state.get("truck_filter", "All")
#selected_route = st.session_state.get("route_filter", "All")
selected_month = month_dict[selected_month_display]  # <-- Add this line!

# --- Apply filters ---
filtered_ops = operations.copy()
if selected_truck != "All":
    filtered_ops = filtered_ops[filtered_ops["TruckID"] == selected_truck]
if selected_route != "All":
    filtered_ops = filtered_ops[filtered_ops["Route Code"] == selected_route]
filtered_ops = filtered_ops[filtered_ops["Year-Month"] == selected_month]


# Calculate previous period for delta comparisons
prev_month = (pd.to_datetime(selected_month) - pd.DateOffset(months=1)).strftime("%Y-%m")
prev_month_filtered = operations[operations["Year-Month"] == prev_month]

# --- MERGE WITH LOI ---
merged_ops = pd.merge(filtered_ops, loi, on="Route Code", how="left")

# --- HOME TAB ---
if selected == "Home":
    st.session_state.first_visit = False

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🚀 Welcome to Prime Tower")
        st.markdown("""
        **Prime Tower** is your real-time dashboard to track trips, fuel, costs, and profitability —  
        designed for logistics operators who want visibility without complexity.
        """)
    with col2:
        try:
            st.image("prime_tower/prime_logo.png", width=160)
        except:
            st.warning("🔺 Logo not found")

    # Audience
    st.markdown("## 👤 Who is Prime Tower for?")
    st.markdown("""
    - 🛻 **Truck Owners** (1–50 trucks)  
    - 🤝 **Subcontracted Transporters**  
    - 🧾 **SME Logistics Coordinators**  
    - 🔍 **Fleet Managers** needing better data  
    """)

    # Get Started Options
    st.markdown("## 🛠️ How to Get Started")
    st.markdown("Pick one of the quick-start options below:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🧪 Try Demo Data")
        st.markdown("Explore the full dashboard with ready-made sample data.")
        if st.button("Try Demo Data", use_container_width=True, key="demo_data_button"):
            st.session_state.use_demo = True
            st.rerun()

    with col2:
        st.markdown("### 📊 Connect Your Google Sheet")
        st.markdown("Use your real data with our plug-and-play template.")
        if st.button("Connect Sheet (Coming Soon)", use_container_width=True, key="connect_sheet_button"):
            st.info("🔧 This feature is under development.")

    with col3:
        st.markdown("### 📄 View Sheet Template")
        st.markdown("See how to format your data for best results.")
        if st.button("Open Template", use_container_width=True, key="view_template_button"):
            st.markdown("[👉 Download Sheet Template](https://your-template-link.com)")

    # Features Table
    st.markdown("## 🔑 Key Features at a Glance")

    st.markdown("""
    | 🛠 Feature | 💬 Description |
    |------------|----------------|
    | 📍 **Trip Tracking** | Real-time visibility into trips, distances, loads |
    | 💰 **Profit Analysis** | Know your margin per truck, trip, and route |
    | ⛽ **Fuel Usage Insights** | Spot fuel anomalies and consumption patterns |
    | 🔧 **Maintenance Reminders** | Get alerts before services and renewals are missed |
    | 🧮 **Fleet Cost Dashboard** | Compare truck performance and total cost/km |
    """)

    # Footer CTA
    st.markdown("""
    ---
    ### ✅ Ready to take control?
    Use the left menu to explore live dashboards or start with demo data above.
    Need help? [Chat with us on WhatsApp](https://wa.me/YOURNUMBER) or [book a walkthrough](https://calendly.com/YOUR-LINK).
    """)

elif selected == "Financials":
        st.markdown("Analyze cost structures and profitability by truck and route")
        
        # Prepare cost data
        cost_df = filtered_ops.copy()
        cost_df = cost_df.merge(loi[["Route Code", "Rate per ton"]], on="Route Code", how="left")
        cost_df = cost_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        cost_df = cost_df.merge(tracker[["TruckID", "Distance (km)"]], on="TruckID", how="left")
        cost_df = cost_df.merge(vcs[["TruckID", "Fuel Cost (R/km)", "Maintenance Cost (R/km)", 
                                     "Tyres (R/km)", "Daily Fixed Cost (R/day)"]],
                        on="TruckID", how="left")
    
        # Calculations
        cost_df["Revenue (R)"] = cost_df["Ton Reg"] * cost_df["Rate per ton"]
        cost_df["Variable Cost (R)"] = cost_df["Distance (km)"] * (
            cost_df["Fuel Cost (R/km)"] + cost_df["Maintenance Cost (R/km)"] + cost_df["Tyres (R/km)"]
        )
        cost_df["Total Cost (R)"] = cost_df["Variable Cost (R)"] + cost_df["Daily Fixed Cost (R/day)"]
        cost_df["Profit (R)"] = cost_df["Revenue (R)"] - cost_df["Total Cost (R)"]
        cost_df["Profit per Ton (R)"] = cost_df["Profit (R)"] / cost_df["Ton Reg"]
        cost_df["Cost per Ton (R)"] = cost_df["Total Cost (R)"] / cost_df["Ton Reg"]
        
        # KPIs with delta calculations - with improved error handling
        total_revenue = cost_df["Revenue (R)"].sum()
        
        # Handle cases where previous month data might be empty or invalid
        try:
            prev_revenue = prev_month_filtered["Ton Reg"].sum() * loi["Rate per ton"].mean() if not prev_month_filtered.empty else 0
            revenue_delta = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue != 0 else 0
        except:
            prev_revenue = 0
            revenue_delta = 0
        
        total_cost = cost_df["Total Cost (R)"].sum()
        
        # Improved fixed cost calculation with error handling
        try:
            fixed_cost_mean = pd.to_numeric(vcs["Daily Fixed Cost (R/day)"], errors='coerce').mean()
            prev_cost = len(prev_month_filtered) * fixed_cost_mean if not prev_month_filtered.empty else 0
            cost_delta = ((total_cost - prev_cost) / prev_cost * 100) if prev_cost != 0 else 0
        except:
            prev_cost = 0
            cost_delta = 0
        
        avg_cost_per_km = (cost_df["Total Cost (R)"] / cost_df["Distance (km)"]).mean()
        profitable_trucks = cost_df[cost_df["Profit (R)"] > 0]["TruckID"].nunique()
        total_trucks = cost_df["TruckID"].nunique()
    
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(kpi_card("Total Revenue", f"R{total_revenue:,.2f}", icon="currency-dollar", delta=revenue_delta), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Total Cost", f"R{total_cost:,.2f}", icon="cash-stack", delta=cost_delta), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Avg Cost per KM", f"R{avg_cost_per_km:,.2f}", icon="calculator"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("Profitable Trucks", f"{profitable_trucks} / {total_trucks}", icon="graph-up"), unsafe_allow_html=True)
        
        st.caption(f"Data from {cost_df['Date'].min().date()} to {cost_df['Date'].max().date()}")
    
        with st.container():
            col1, col2 = st.columns(2)
            
            # Cost Breakdown per Truck
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
                    color_discrete_map={
                        "Variable Cost (R)": COLOR_MAP["Variable Cost"],
                        "Daily Fixed Cost (R/day)": COLOR_MAP["Fixed Cost"]
                    }
                )
                fig = apply_chart_style(fig, "Cost Structure by Truck")
                st.plotly_chart(fig, use_container_width=True)
            
            # Profitability by Truck
            with col2:
                fig2 = px.bar(
                    grouped_cost,
                    x="TruckID",
                    y="Profit (R)",
                    color="Profit (R)",
                    color_continuous_scale=[(0, "#d32f2f"), (1, ACCENT_TEAL)],
                    title="Profit by Truck",
                    labels={"Profit (R)": "Profit (R)"}
                )
                fig2 = apply_chart_style(fig2, "Profit by Truck")
                st.plotly_chart(fig2, use_container_width=True)
        
        with st.container():
            # Route profitability heatmap
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
                x0=0, y0=0, x1=route_profit["Revenue (R)"].max()*1.1,
                y1=route_profit["Revenue (R)"].max()*1.1
            )
            fig3 = apply_chart_style(fig3, "Route Profitability Analysis")
            st.plotly_chart(fig3, use_container_width=True)
        
        # Loss-Making Analysis
        loss_df = cost_df[cost_df["Profit (R)"] < 0]
        
        if not loss_df.empty:
            st.warning(f"🚨 {len(loss_df)} trips resulted in losses totaling R{loss_df['Profit (R)'].sum():,.2f}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Top Loss-Making Trucks**")
                loss_trucks = loss_df.groupby("TruckID")["Profit (R)"].sum().sort_values().reset_index()
                fig4 = px.bar(
                    loss_trucks,
                    x="TruckID",
                    y="Profit (R)",
                    color="Profit (R)",
                    color_continuous_scale=[(0, "#d32f2f"), (1, "#d32f2f")],
                    title="Cumulative Loss by Truck"
                )
                fig4 = apply_chart_style(fig4, "Cumulative Loss by Truck")
                st.plotly_chart(fig4, use_container_width=True)
            
            with col2:
                st.markdown("**Loss-Making Routes**")
                loss_routes = loss_df.groupby("Route Code")["Profit (R)"].sum().sort_values().reset_index()
                fig5 = px.bar(
                    loss_routes,
                    x="Route Code",
                    y="Profit (R)",
                    color="Profit (R)",
                    color_continuous_scale=[(0, "#d32f2f"), (1, "#d32f2f")],
                    title="Cumulative Loss by Route"
                )
                fig5 = apply_chart_style(fig5, "Cumulative Loss by Route")
                st.plotly_chart(fig5, use_container_width=True)
        else:
            st.success("✅ All trips were profitable in the selected period.")

elif selected == "Operations":
    st.markdown("Monitor daily truck activities and performance metrics")
    
    # Prepare operations data
    ops_df = filtered_ops.copy()
    ops_df = ops_df.merge(loi[["Route Code", "Distance (km)"]], on="Route Code", how="left")
    ops_df = ops_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
    
    # KPIs
    active_trucks = ops_df["TruckID"].nunique()
    total_tons = ops_df[ops_df["Doc Type"] == "Offloading"]["Ton Reg"].sum()
    total_km = ops_df["Distance (km)"].sum()
    route_count = ops_df["Route Code"].nunique()
    
    # Calculate deltas
    prev_active_trucks = prev_month_filtered["TruckID"].nunique() if not prev_month_filtered.empty else 0
    active_trucks_delta = ((active_trucks - prev_active_trucks) / prev_active_trucks * 100) if prev_active_trucks != 0 else 0
    
    prev_tons = prev_month_filtered[prev_month_filtered["Doc Type"] == "Offloading"]["Ton Reg"].sum() if not prev_month_filtered.empty else 0
    tons_delta = ((total_tons - prev_tons) / prev_tons * 100) if prev_tons != 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(kpi_card("Active Trucks", active_trucks, icon="truck", delta=active_trucks_delta), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("Total Tons Moved", f"{total_tons:,.1f}", icon="stack", delta=tons_delta), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Distance Covered", f"{total_km:,.0f} km", icon="speedometer2"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Routes Used", route_count, icon="signpost"), unsafe_allow_html=True)
    
    st.caption(f"Data from {ops_df['Date'].min().date()} to {ops_df['Date'].max().date()}")
    
    with st.container():
        # Daily tons moved
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
        
        # Tons by Truck
        with col1:
            tons_per_truck = ops_df.groupby(["TruckID", "Driver Name"])["Ton Reg"].sum().reset_index()
            tons_per_truck = tons_per_truck.sort_values("Ton Reg", ascending=False)
            
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
        
        # Trips by Truck
        with col2:
            trips_per_truck = ops_df[ops_df["Doc Type"] == "Offloading"].groupby(["TruckID", "Driver Name"]).size().reset_index(name="Trips")
            trips_per_truck = trips_per_truck.sort_values("Trips", ascending=False)
            
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
    
    # Idle Trucks Analysis
    moved_trucks = ops_df["TruckID"].unique()
    all_trucks = truck_pak["TruckID"].unique()
    idle_trucks = list(set(all_trucks) - set(moved_trucks))
    
    if idle_trucks:
        idle_df = truck_pak[truck_pak["TruckID"].isin(idle_trucks)][["TruckID", "Driver Name", "Current Mileage"]]
        st.warning(f"🚨 {len(idle_trucks)} trucks had no activity in the selected period.")
        st.dataframe(idle_df)
    else:
        st.success("✅ All trucks were active during the selected period.")

elif selected == "Fuel":
    st.markdown("Monitor fuel consumption patterns and identify optimization opportunities")
    
    # Prepare fuel data
    fuel_df = filtered_ops[filtered_ops["Doc Type"] == "Fuel"].copy()
    fuel_df = fuel_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
    fuel_df = fuel_df.merge(loi[["Route Code", "Distance (km)"]], on="Route Code", how="left")
    
    # Calculate fuel efficiency
    fuel_df["Fuel Efficiency (km/L)"] = fuel_df["Distance (km)"] / fuel_df["Ton Reg"]
    fuel_df["Fuel Cost per km (R/km)"] = fuel_df["Ton Reg"] / fuel_df["Distance (km)"]
    
    # KPIs
    avg_efficiency = fuel_df["Fuel Efficiency (km/L)"].mean()
    total_fuel_used = fuel_df["Ton Reg"].sum()
    fuel_cost_per_km = fuel_df["Fuel Cost per km (R/km)"].mean()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            kpi_card("Avg Fuel Efficiency", f"{avg_efficiency:.2f} km/L", icon="speedometer"),
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(kpi_card("Total Fuel Used", f"{total_fuel_used:,.1f} L", icon="fuel-pump"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Avg Fuel Cost per km", f"R{fuel_cost_per_km:.2f}", icon="currency-dollar"), unsafe_allow_html=True)
    
    st.caption(f"Data from {fuel_df['Date'].min().date()} to {fuel_df['Date'].max().date()}")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        # Daily fuel efficiency
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
        
        # Efficiency by Truck
        with col2:
            truck_eff = fuel_df.groupby(["TruckID", "Driver Name"])["Fuel Efficiency (km/L)"].mean().reset_index()
            truck_eff = truck_eff.sort_values("Fuel Efficiency (km/L)", ascending=False)
            
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
    
    with st.container():
        # Fuel vs Distance
        fig3 = px.scatter(
            fuel_df,
            x="Distance (km)",
            y="Ton Reg",
            color="Fuel Efficiency (km/L)",
            hover_name="TruckID",
            hover_data=["Driver Name", "Route Code"],
            title="Fuel Consumption vs Distance",
            trendline="lowess",
            color_continuous_scale=[(0, "#d32f2f"), (1, ACCENT_TEAL)]
        )
        fig3.update_layout(
            xaxis_title="Distance (km)",
            yaxis_title="Fuel Used (L)"
        )
        fig3 = apply_chart_style(fig3, "Fuel Consumption vs Distance")
        st.plotly_chart(fig3, use_container_width=True)
    
    # Outliers Analysis
    inefficient_trips = fuel_df[fuel_df["Fuel Efficiency (km/L)"] < 2.0]
    
    if not inefficient_trips.empty:
        st.warning(f"Found {len(inefficient_trips)} trips with efficiency below 2.0 km/L")
        st.dataframe(inefficient_trips[["Date", "TruckID", "Driver Name", "Route Code", 
                                      "Distance (km)", "Ton Reg", "Fuel Efficiency (km/L)"]])
    else:
        st.success("✅ No extremely inefficient trips found")

elif selected == "Maintenance":
    st.markdown("Track vehicle maintenance schedules and compliance status")
    
    # Prepare maintenance data
    maint_df = truck_pak.copy()
    maint_df["KM Since Service"] = maint_df["Current Mileage"] - maint_df["Last Service Mileage"]
    maint_df["Service Due"] = maint_df["KM Since Service"] > 10000
    
    # Date-based expiry checks
    today = pd.to_datetime("today").normalize()  # Ensure we're working with dates only
    
    expiry_fields = {
        "Vehicle License Expiry": "License Expiry",
        "Driver License Expiry": "Driver License",
        "GIT Insurance Expiry": "GIT Insurance"
    }
    
    for col, label in expiry_fields.items():
        # First ensure the column is in datetime format
        maint_df[col] = pd.to_datetime(maint_df[col], errors='coerce')
        
        # Calculate days left (returns NaN for invalid dates)
        maint_df[f"{label} Days Left"] = (maint_df[col] - today).dt.days
        
        # Mark as expiring if <= 30 days and not NaN
        maint_df[f"{label} Expiring"] = (
            maint_df[f"{label} Days Left"].notna() & 
            (maint_df[f"{label} Days Left"] <= 30)
        )
    
    # KPIs
    overdue_services = maint_df["Service Due"].sum()
    license_expiring = maint_df["License Expiry Expiring"].sum()
    driver_expiring = maint_df["Driver License Expiring"].sum()
    git_expiring = maint_df["GIT Insurance Expiring"].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(kpi_card("Overdue Services", int(overdue_services), icon="tools"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("Vehicle Licenses Expiring", license_expiring, icon="car-front"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Driver Licenses Expiring", driver_expiring, icon="person-vcard"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("GIT Insurance Expiring", git_expiring, icon="shield-exclamation"), unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        # KM Since Service
        with col1:
            fig1 = px.bar(
                maint_df.sort_values("KM Since Service", ascending=False),
                x="TruckID",
                y="KM Since Service",
                color="Service Due",
                color_discrete_map={True: "#d32f2f", False: ACCENT_TEAL},
                title="KM Since Last Service",
                hover_data=["Current Mileage", "Last Service Mileage"]
            )
            fig1.add_hline(y=10000, line_dash="dash", line_color=ACCENT_GOLD, 
                          annotation_text="Service Threshold")
            fig1 = apply_chart_style(fig1, "KM Since Last Service")
            st.plotly_chart(fig1, use_container_width=True)
        
        # Upcoming Expiries
        with col2:
            expiring_df = maint_df[
                maint_df["License Expiry Expiring"] |
                maint_df["Driver License Expiring"] |
                maint_df["GIT Insurance Expiring"]
            ]
            
            if expiring_df.empty:
                st.success("✅ No licenses or insurance expiring soon.")
            else:
                # Convert to datetime with error handling
                date_cols = ["Vehicle License Expiry", "Driver License Expiry", "GIT Insurance Expiry"]
                for col in date_cols:
                    expiring_df[col] = pd.to_datetime(expiring_df[col], errors='coerce')
                
                today = pd.Timestamp.today().normalize()  # Use normalize() to remove time component
                
                # Calculate days remaining with NaN handling
                days_matrix = expiring_df[date_cols].apply(
                    lambda col: (col - today).dt.days
                )
                
                # Replace NaT with NaN and handle negative values
                days_matrix = days_matrix.replace({pd.NaT: np.nan})
                days_matrix = days_matrix.clip(lower=0, upper=30)  # Only show 0-30 days range
                
                # Create heatmap with improved data validation
                fig2 = go.Figure(data=go.Heatmap(
                    z=days_matrix.values,
                    x=days_matrix.columns,
                    y=expiring_df["TruckID"],
                    colorscale=[
                        [0.0, "darkred"],
                        [0.2, "orangered"],
                        [0.5, "orange"],
                        [0.8, "yellow"],
                        [1.0, "lightyellow"]
                    ],
                    colorbar=dict(
                        title="Days to Expiry",
                        tickvals=[0, 10, 20, 30],
                        ticktext=["0 (Expired)", "10", "20", "30+"]
                    ),
                    hoverongaps=False,
                    hovertemplate="TruckID %{y}<br>%{x}: %{z} days<br>Expiry Date: %{customdata}",
                    customdata=expiring_df[date_cols].apply(lambda x: x.dt.strftime('%Y-%m-%d'))
                ))
                
                fig2.update_layout(
                    title="Expiring Licenses & Insurance (Next 30 Days)",
                    xaxis_title="Document Type",
                    yaxis_title="Truck",
                    margin=dict(l=30, r=10, t=60, b=40),  # Increased top margin for title
                    height=max(400, 50 * len(expiring_df)),  # Dynamic height based on rows
                    paper_bgcolor=PRIMARY_BG,
                    plot_bgcolor=SECONDARY_NAVY,
                    font=dict(color=WHITE),
                    xaxis=dict(side="bottom")  # Move x-axis to top for better readability
                )
                
                st.plotly_chart(fig2, use_container_width=True)
    
    # Service Due Table
    st.markdown("### 🔧 Vehicles Due for Service")
    due_service_df = maint_df[maint_df["Service Due"]].sort_values("KM Since Service", ascending=False)
    
    if not due_service_df.empty:
        st.warning(f"🚨 {len(due_service_df)} trucks are overdue for service")
        st.dataframe(due_service_df[["TruckID", "Driver Name", "Current Mileage", 
                                   "Last Service Mileage", "KM Since Service"]])
    else:
        st.success("✅ All trucks are within service limits")

elif selected == "Alerts":
    st.markdown("Actionable recommendations to optimize fleet performance")
    
    # Prepare data for insights with error handling
    try:
        cost_df = filtered_ops.copy()
        # Ensure numeric columns are properly formatted
        numeric_cols = ["Ton Reg", "Rate per ton", "Distance (km)", 
                       "Fuel Cost (R/km)", "Maintenance Cost (R/km)", 
                       "Tyres (R/km)", "Daily Fixed Cost (R/day)"]
        
        for col in numeric_cols:
            if col in cost_df.columns:
                cost_df[col] = pd.to_numeric(cost_df[col], errors='coerce').fillna(0)
        
        # Merge operations with error handling
        cost_df = cost_df.merge(loi[["Route Code", "Rate per ton"]], on="Route Code", how="left")
        cost_df = cost_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        cost_df = cost_df.merge(tracker[["TruckID", "Distance (km)"]], on="TruckID", how="left")
        cost_df = cost_df.merge(vcs[["TruckID", "Fuel Cost (R/km)", "Maintenance Cost (R/km)", 
                                   "Tyres (R/km)", "Daily Fixed Cost (R/day)"]],
                        on="TruckID", how="left")
        
        # Calculations with fallbacks
        cost_df["Revenue (R)"] = cost_df["Ton Reg"] * cost_df["Rate per ton"].fillna(0)
        cost_df["Variable Cost (R)"] = cost_df["Distance (km)"] * (
            cost_df["Fuel Cost (R/km)"].fillna(0) + 
            cost_df["Maintenance Cost (R/km)"].fillna(0) + 
            cost_df["Tyres (R/km)"].fillna(0)
        )
        cost_df["Total Cost (R)"] = cost_df["Variable Cost (R)"] + cost_df["Daily Fixed Cost (R/day)"].fillna(0)
        cost_df["Profit (R)"] = cost_df["Revenue (R)"] - cost_df["Total Cost (R)"]
        
        # Prepare fuel efficiency data
        fuel_df = filtered_ops[filtered_ops["Doc Type"] == "Fuel"].copy()
        fuel_df = fuel_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        fuel_df = fuel_df.merge(loi[["Route Code", "Distance (km)"]], on="Route Code", how="left")
        
        # Ensure numeric columns for fuel calculations
        fuel_df["Ton Reg"] = pd.to_numeric(fuel_df["Ton Reg"], errors='coerce').fillna(0)
        fuel_df["Distance (km)"] = pd.to_numeric(fuel_df["Distance (km)"], errors='coerce').fillna(0)
        fuel_df["Fuel Efficiency (km/L)"] = np.where(
            fuel_df["Ton Reg"] > 0,
            fuel_df["Distance (km)"] / fuel_df["Ton Reg"],
            0
        )
        
    except Exception as e:
        st.error(f"Error preparing data for analysis: {str(e)}")
        cost_df = pd.DataFrame()
        fuel_df = pd.DataFrame()

    # Top Performers Section
    with st.container():
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <h2 style='color: {ACCENT_GOLD}; border-bottom: 2px solid {ACCENT_TEAL}; 
                    display: inline-block; padding-bottom: 5px;'>🏆 Performance Dashboard</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Top Performers Row
        st.markdown("### 🌟 Top Performers")
        col1, col2 = st.columns(2)
        
        # Most Profitable Truck Card
        with col1:
            try:
                if not cost_df.empty:
                    profitable_truck = (
                        cost_df.groupby(["TruckID", "Driver Name"])["Profit (R)"]
                        .sum()
                        .astype(float)
                        .nlargest(1)
                        .reset_index()
                    )
                    if not profitable_truck.empty:
                        truck = profitable_truck.iloc[0]
                        st.markdown(f"""
                            <div style='background-color: {SECONDARY_NAVY}; padding: 20px; 
                                border-radius: 12px; border-left: 5px solid {ACCENT_TEAL};
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1); height: 100%;'>
                                <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 15px;'>
                                    <div style='background: {ACCENT_GOLD}; width: 50px; height: 50px; 
                                        border-radius: 50%; display: flex; align-items: center; justify-content: center;'>
                                        <span style='font-size: 24px;'>🚛</span>
                                    </div>
                                    <h4 style='color: {ACCENT_GOLD}; margin: 0;'>Most Profitable Truck</h4>
                                </div>
                                <p style='font-size: 16px; margin-bottom: 5px; color: #e0e0e0;'>Truck ID</p>
                                <p style='font-size: 20px; margin-top: 0; margin-bottom: 15px;'><strong>{truck['TruckID']}</strong></p>
                                <p style='font-size: 16px; margin-bottom: 5px; color: #e0e0e0;'>Driver</p>
                                <p style='font-size: 18px; margin-top: 0; margin-bottom: 20px;'>{truck['Driver Name']}</p>
                                <p style='font-size: 16px; margin-bottom: 5px; color: #e0e0e0;'>Total Profit</p>
                                <p style='font-size: 28px; color: {ACCENT_TEAL}; margin: 0; font-weight: bold;'>R{truck['Profit (R)']:,.2f}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No cost data available for analysis")
            except Exception as e:
                st.error(f"Error calculating profitable truck: {str(e)}")
        
        # Most Efficient Route Card
        with col2:
            try:
                if not cost_df.empty:
                    efficient_route = (
                        cost_df.groupby("Route Code")["Profit (R)"]
                        .mean()
                        .astype(float)
                        .nlargest(1)
                        .reset_index()
                    )
                    if not efficient_route.empty:
                        route = efficient_route.iloc[0]
                        st.markdown(f"""
                            <div style='background-color: {SECONDARY_NAVY}; padding: 20px; 
                                border-radius: 12px; border-left: 5px solid {ACCENT_TEAL};
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1); height: 100%;'>
                                <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 15px;'>
                                    <div style='background: {ACCENT_GOLD}; width: 50px; height: 50px; 
                                        border-radius: 50%; display: flex; align-items: center; justify-content: center;'>
                                        <span style='font-size: 24px;'>🛣️</span>
                                    </div>
                                    <h4 style='color: {ACCENT_GOLD}; margin: 0;'>Most Profitable Route</h4>
                                </div>
                                <p style='font-size: 16px; margin-bottom: 5px; color: #e0e0e0;'>Route Code</p>
                                <p style='font-size: 20px; margin-top: 0; margin-bottom: 20px;'><strong>{route['Route Code']}</strong></p>
                                <p style='font-size: 16px; margin-bottom: 5px; color: #e0e0e0;'>Average Profit</p>
                                <p style='font-size: 28px; color: {ACCENT_TEAL}; margin: 0; font-weight: bold;'>R{route['Profit (R)']:,.2f}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No route data available for analysis")
            except Exception as e:
                st.error(f"Error calculating efficient route: {str(e)}")
    
    # Optimization Opportunities Section
    with st.container():
        st.markdown("### ⚡ Optimization Opportunities")
        col1, col2 = st.columns(2)
        
        # Least Fuel-Efficient Trucks Card
        with col1:
            try:
                if not fuel_df.empty:
                    inefficient_trucks = (
                        fuel_df.groupby(["TruckID", "Driver Name"])["Fuel Efficiency (km/L)"]
                        .mean()
                        .astype(float)
                        .nsmallest(3)
                        .reset_index()
                    )
                    if not inefficient_trucks.empty:
                        st.markdown(f"""
                            <div style='background-color: {SECONDARY_NAVY}; padding: 20px; 
                                border-radius: 12px; border-left: 5px solid #d32f2f;
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1); height: 100%;'>
                                <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 15px;'>
                                    <div style='background: #d32f2f; width: 50px; height: 50px; 
                                        border-radius: 50%; display: flex; align-items: center; justify-content: center;'>
                                        <span style='font-size: 24px;'>⛽</span>
                                    </div>
                                    <h4 style='color: #d32f2f; margin: 0;'>Least Fuel-Efficient Trucks</h4>
                                </div>
                                <div style='margin-top: 20px;'>
                                    <table style='width: 100%; border-collapse: collapse;'>
                                        <thead>
                                            <tr style='border-bottom: 1px solid #444;'>
                                                <th style='text-align: left; padding: 8px 0; color: #e0e0e0;'>Truck</th>
                                                <th style='text-align: left; padding: 8px 0; color: #e0e0e0;'>Driver</th>
                                                <th style='text-align: right; padding: 8px 0; color: #e0e0e0;'>Efficiency</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        """, unsafe_allow_html=True)
                        
                        for _, row in inefficient_trucks.iterrows():
                            st.markdown(f"""
                                <tr style='border-bottom: 1px solid #333;'>
                                    <td style='padding: 8px 0;'><strong>{row['TruckID']}</strong></td>
                                    <td style='padding: 8px 0;'>{row['Driver Name']}</td>
                                    <td style='padding: 8px 0; text-align: right; color: #ff5252;'>{row['Fuel Efficiency (km/L)']:.2f} km/L</td>
                                </tr>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("""
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("All trucks meet fuel efficiency standards")
                else:
                    st.warning("No fuel efficiency data available")
            except Exception as e:
                st.error(f"Error calculating inefficient trucks: {str(e)}")
            
        
        # Loss-Making Routes Card
        with col2:
            try:
                if not cost_df.empty:
                    loss_routes = (
                        cost_df.groupby("Route Code")["Profit (R)"]
                        .sum()
                        .astype(float)
                        .nsmallest(3)
                        .reset_index()
                    )
                    if not loss_routes.empty:
                        st.markdown(f"""
                            <div style='background-color: {SECONDARY_NAVY}; padding: 20px; 
                                border-radius: 12px; border-left: 5px solid #d32f2f;
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1); height: 100%;'>
                                <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 15px;'>
                                    <div style='background: #d32f2f; width: 50px; height: 50px; 
                                        border-radius: 50%; display: flex; align-items: center; justify-content: center;'>
                                        <span style='font-size: 24px;'>🔴</span>
                                    </div>
                                    <h4 style='color: #d32f2f; margin: 0;'>Top Loss-Making Routes</h4>
                                </div>
                                <div style='margin-top: 20px;'>
                                    <table style='width: 100%; border-collapse: collapse;'>
                                        <thead>
                                            <tr style='border-bottom: 1px solid #444;'>
                                                <th style='text-align: left; padding: 8px 0; color: #e0e0e0;'>Route Code</th>
                                                <th style='text-align: right; padding: 8px 0; color: #e0e0e0;'>Total Loss</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        """, unsafe_allow_html=True)
                        
                        for _, row in loss_routes.iterrows():
                            st.markdown(f"""
                                <tr style='border-bottom: 1px solid #333;'>
                                    <td style='padding: 8px 0;'><strong>{row['Route Code']}</strong></td>
                                    <td style='padding: 8px 0; text-align: right; color: #ff5252;'>R{abs(row['Profit (R)']):,.2f}</td>
                                </tr>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("""
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("No loss-making routes found")
                else:
                    st.warning("No route data available for analysis")
            except Exception as e:
                st.error(f"Error calculating loss routes: {str(e)}")

    # Pricing Recommendations Section
    try:
        if not cost_df.empty:
            route_analysis = cost_df.groupby("Route Code").agg({
                "Rate per ton": "mean",
                "Profit (R)": "mean",
                "Ton Reg": "sum"
            }).reset_index()
            
            # Ensure numeric columns
            route_analysis["Rate per ton"] = pd.to_numeric(route_analysis["Rate per ton"], errors='coerce').fillna(0)
            route_analysis["Profit (R)"] = pd.to_numeric(route_analysis["Profit (R)"], errors='coerce').fillna(0)
            route_analysis["Ton Reg"] = pd.to_numeric(route_analysis["Ton Reg"], errors='coerce').fillna(0)
            
            # Identify routes where profit is negative but volume is high
            high_volume_low_profit = route_analysis[
                (route_analysis["Profit (R)"] < 0) & 
                (route_analysis["Ton Reg"] > route_analysis["Ton Reg"].quantile(0.75))
            ]
            
            if not high_volume_low_profit.empty:
                st.warning("The following high-volume routes are currently unprofitable. Consider rate adjustments:")
                
                for _, row in high_volume_low_profit.iterrows():
                    current_rate = row["Rate per ton"]
                    suggested_rate = current_rate * 1.15  # 15% increase
                    st.markdown(f"""
                        - **{row['Route Code']}**: Current rate R{current_rate:.2f}/ton → 
                        Suggest R{suggested_rate:.2f}/ton (15% increase)
                    """)
            else:
                st.success("No major pricing issues detected in high-volume routes")
        else:
            st.warning("No data available for pricing recommendations")
    except Exception as e:
        st.error(f"Error generating pricing recommendations: {str(e)}")

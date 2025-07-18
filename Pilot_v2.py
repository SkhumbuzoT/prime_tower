import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import gspread
from google.oauth2 import service_account

# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# Brand Colors
PRIMARY_BG = "#000000"  # Jet Black
ACCENT_TEAL = "#008080"  # Teal
ACCENT_GOLD = "#D4AF37"  # Gold
SECONDARY_NAVY = "#0A1F44"  # Navy Blue
WHITE = "#FFFFFF"  # White
LIGHT_GRAY = "#F8F9FA"  # Light Gray for backgrounds

# Color Map for Charts
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

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

# Page Configuration
st.set_page_config(
    page_title="PrimeTower Fleet Dashboard",
    page_icon=":truck:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# STYLES & THEMES
# =============================================================================

def apply_custom_styles():
    """Apply custom CSS styles to the application."""
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
                height: 120px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
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
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .metric-card p {{
                font-family: 'Poppins', sans-serif;
                font-size: 1.2rem;  /* Reduced from 1.8rem to 1.4rem */
                color: #D4AF37;     /* Directly using the gold color for consistency */
                margin: 0;
                line-height: 1;
                font-weight: 600;   /* Added semi-bold weight for better readability */
            }}
            .metric-card .emoji {{
                font-size: 1.5rem;
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

def configure_chart_theme():
    """Configure the default Plotly theme for charts."""
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

# Apply styles and themes
apply_custom_styles()
configure_chart_theme()

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def apply_chart_style(fig, title, height=400):
    """Apply consistent styling to Plotly charts."""
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

def kpi_card(title, value, emoji=None):
    """Generate a standardized KPI card without inline styles"""
    emoji_html = f'<span class="metric-emoji">{emoji}</span>' if emoji else ""
    
    return f"""
        <div class="metric-card">
            <h3>{emoji_html}{title}</h3>
            <p>{value}</p>
        </div>
    """

# =============================================================================
# DATA LOADING
# =============================================================================

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

# =============================================================================
# AUTHENTICATION
# =============================================================================

def show_login():
    """Display the login interface."""
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
    """Authenticate user credentials."""
    # Note: In production, use secure authentication methods
    users = {"admin": "1234", "user1": "pass123"}
    
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.first_visit = True
        st.rerun()
    else:
        st.error("Invalid credentials")

# Check authentication
if not st.session_state.logged_in:
    show_login()
    st.stop()

# =============================================================================
# DATA PREPARATION
# =============================================================================

def prepare_data(operations_df):
    """Prepare and process the operations data."""
    operations_df["Date_only"] = operations_df["Date"].dt.date
    operations_df["Year-Month"] = operations_df["Date"].dt.to_period("M").astype(str)
    operations_df["Month_Display"] = operations_df["Date"].dt.strftime("%B %Y")
    
    # Create month mapping for filters
    month_mapping = operations_df[["Year-Month", "Month_Display"]].drop_duplicates()
    month_dict = dict(zip(month_mapping["Month_Display"], month_mapping["Year-Month"]))
    available_months_display = sorted(month_dict.keys(), key=lambda m: month_dict[m])
    
    return operations_df, month_dict, available_months_display

operations, month_dict, available_months_display = prepare_data(operations)

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

with st.sidebar:
    # User greeting
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <h4 style='color: {ACCENT_TEAL};'>Welcome, {st.session_state.username}</h4>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
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
    
    # Filters
    with st.form("filters_form"):
        col1, col2, col3 = st.columns([1, 1, 1])
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
    
    # Get current filter values from session state
    selected_month_display = st.session_state.get("month_filter", available_months_display[-1])
    selected_truck = st.session_state.get("truck_filter", "All")
    selected_route = st.session_state.get("route_filter", "All")
    selected_month = month_dict[selected_month_display]
    
    # Logout button
    if st.button("Logout", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# =============================================================================
# DATA FILTERING
# =============================================================================

def apply_filters(df, month, truck, route):
    """Apply filters to the data based on user selections."""
    filtered_df = df[df["Year-Month"] == month]
    
    if truck != "All":
        filtered_df = filtered_df[filtered_df["TruckID"] == truck]
    
    if route != "All":
        filtered_df = filtered_df[filtered_df["Route Code"] == route]
    
    return filtered_df

filtered_ops = apply_filters(operations, selected_month, selected_truck, selected_route)

# Calculate previous period for delta comparisons
prev_month = (pd.to_datetime(selected_month) - pd.DateOffset(months=1)).strftime("%Y-%m")
prev_month_filtered = operations[operations["Year-Month"] == prev_month]

# =============================================================================
# PAGE CONTENT
# =============================================================================

# HOME TAB
if selected == "Home":
    st.session_state.first_visit = False
    
    # Header
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: {ACCENT_TEAL};'>🚀 PrimeTower Fleet Dashboard</h1>
            <p style='font-size: 1.2rem; color: {LIGHT_GRAY};'>
                Real-time insights for smarter trucking operations
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Introduction
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
    
    # Features
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
    
    # Call to action
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
    st.markdown("#### 📊 Financials Overview")
    
    try:
        # Prepare financial data
        cost_df = filtered_ops.copy()
        cost_df = cost_df.merge(loi[["Route Code", "Rate per ton"]], on="Route Code", how="left")
        cost_df = cost_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        cost_df = cost_df.merge(tracker[["TruckID", "Distance (km)"]], on="TruckID", how="left")
        cost_df = cost_df.merge(vcs[["TruckID", "Fuel Cost (R/km)", "Maintenance Cost (R/km)", 
                                    "Tyres (R/km)", "Daily Fixed Cost (R/day)"]], on="TruckID", how="left")
        
        # Calculate financial metrics
        cost_df["Revenue (R)"] = cost_df["Ton Reg"] * cost_df["Rate per ton"]
        cost_df["Variable Cost (R)"] = cost_df["Distance (km)"] * (
            cost_df["Fuel Cost (R/km)"] + cost_df["Maintenance Cost (R/km)"] + cost_df["Tyres (R/km)"]
        )
        cost_df["Total Cost (R)"] = cost_df["Variable Cost (R)"] + cost_df["Daily Fixed Cost (R/day)"]
        cost_df["Profit (R)"] = cost_df["Revenue (R)"] - cost_df["Total Cost (R)"]
        
        # Calculate KPIs
        total_revenue = cost_df["Revenue (R)"].sum()
        total_cost = cost_df["Total Cost (R)"].sum()
        avg_cost_per_km = (cost_df["Total Cost (R)"] / cost_df["Distance (km)"]).mean()
        profit_margin = (cost_df["Profit (R)"].sum() / cost_df["Revenue (R)"].sum()) if cost_df["Revenue (R)"].sum() > 0 else 0
        
        # Display exactly 4 KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(kpi_card("Total Revenue", f"R{total_revenue:,.2f}", emoji="💰"), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Total Cost", f"R{total_cost:,.2f}", emoji="📉"), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Avg Cost/km", f"R{avg_cost_per_km:,.2f}", emoji="🛣️"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("Profit Margin", f"{profit_margin:.1%}", emoji="📈"), unsafe_allow_html=True)
        
        st.caption(f"Data from {cost_df['Date'].min().date()} to {cost_df['Date'].max().date()}")
        
        # Charts
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
        
        # Route profitability scatter plot
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
            
            # Add break-even line
            max_value = route_profit[["Revenue (R)", "Total Cost (R)"]].max().max() * 1.1
            fig3.add_shape(
                type="line",
                line=dict(dash="dash", color=WHITE),
                x0=0, y0=0,
                x1=max_value, y1=max_value
            )
            
            fig3 = apply_chart_style(fig3, "Route Profitability")
            st.plotly_chart(fig3, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error in Financials tab: {str(e)}")

# OPERATIONS TAB
elif selected == "Operations":
    st.markdown("#### 🚛 Operations Dashboard")
    
    try:
        # Prepare operations data
        ops_df = filtered_ops.copy()
        
        # Use the correct column name 'Distance (km)' from LOI data
        if "Distance (km)" in loi.columns:
            ops_df = ops_df.merge(loi[["Route Code", "Distance (km)"]], on="Route Code", how="left")
            # Rename to 'Distance' for consistency in calculations
            ops_df = ops_df.rename(columns={"Distance (km)": "Distance"})
        else:
            st.warning("Column 'Distance (km)' not found in LOI data. Using default distance.")
            ops_df["Distance"] = 0
        
        ops_df = ops_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        
        # Calculate KPIs
        active_trucks = ops_df["TruckID"].nunique()
        total_tons = ops_df[ops_df["Doc Type"] == "Offloading"]["Ton Reg"].sum()
        total_km = ops_df["Distance"].sum()  # Now using the correctly named column
        avg_tons_per_truck = total_tons / active_trucks if active_trucks > 0 else 0
        
        # Display exactly 4 KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(kpi_card("Active Trucks", active_trucks, emoji="🚚"), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Total Tons", f"{total_tons:,.1f}", emoji="📦"), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Distance", f"{total_km:,.0f} km", emoji="🛣️"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("Avg Tons/Truck", f"{avg_tons_per_truck:,.1f}", emoji="⚖️"), unsafe_allow_html=True)
        
        st.caption(f"Data from {ops_df['Date'].min().date()} to {ops_df['Date'].max().date()}")
        
        # Daily tons moved chart
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
        
        # Performance by truck
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
    st.markdown("#### ⛽ Fuel Efficiency Dashboard")
    
    try:
        # Prepare fuel data
        fuel_df = filtered_ops[filtered_ops["Doc Type"] == "Fuel"].copy()
        fuel_df = fuel_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        
        if "Distance (km)" in loi.columns:
            fuel_df = fuel_df.merge(loi[["Route Code", "Distance (km)"]], on="Route Code", how="left")
            fuel_df = fuel_df.rename(columns={"Distance (km)": "Distance"})
        else:
            st.warning("Column 'Distance (km)' not found in LOI data. Using default distance.")
            fuel_df["Distance"] = 0
        
        # Calculate fuel metrics
        fuel_df["Fuel Efficiency (km/L)"] = fuel_df["Distance"] / fuel_df["Ton Reg"]
        fuel_df["Fuel Cost per km (R/km)"] = fuel_df["Ton Reg"] / fuel_df["Distance"]
        
        avg_efficiency = fuel_df["Fuel Efficiency (km/L)"].mean()
        total_fuel_used = fuel_df["Ton Reg"].sum()
        fuel_cost_per_km = fuel_df["Fuel Cost per km (R/km)"].mean()
        best_truck_eff = fuel_df.groupby("TruckID")["Fuel Efficiency (km/L)"].mean().max()
        
        # Display exactly 4 KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(kpi_card("Avg Efficiency", f"{avg_efficiency:.2f} km/L", emoji="🚀"), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Total Fuel", f"{total_fuel_used:,.1f} L", emoji="⛽"), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Fuel Cost/km", f"R{fuel_cost_per_km:.2f}", emoji="💸"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("Best Truck", f"{best_truck_eff:.2f} km/L", emoji="🏆"), unsafe_allow_html=True)
        
        st.caption(f"Data from {fuel_df['Date'].min().date()} to {fuel_df['Date'].max().date()}")
        
        # Fuel efficiency charts
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
                fig1.add_hline(
                    y=avg_efficiency,
                    line_dash="dash",
                    line_color=ACCENT_GOLD,
                    annotation_text=f"Avg: {avg_efficiency:.2f} km/L"
                )
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
    st.markdown("#### 🔧 Maintenance Dashboard")
    
    try:
        # Prepare maintenance data
        maint_df = truck_pak.copy()
        maint_df["KM Since Service"] = maint_df["Current Mileage"] - maint_df["Last Service Mileage"]
        maint_df["Service Due"] = maint_df["KM Since Service"] > 10000
        
        today = pd.to_datetime("today").normalize()
        expiry_fields = {
            "Vehicle License Expiry": "License Expiry",
            "Driver License Expiry": "Driver License",
            "GIT Insurance Expiry": "GIT Insurance"
        }
        
        # Calculate days until expiry for various documents
        for col, label in expiry_fields.items():
            # Ensure we're working with datetime objects
            maint_df[col] = pd.to_datetime(maint_df[col])
            # Calculate days left (handle NaT values)
            maint_df[f"{label} Days Left"] = (maint_df[col] - today).dt.days
            maint_df[f"{label} Expiring"] = maint_df[f"{label} Days Left"].le(30)
        
        # Calculate KPIs
        overdue_services = maint_df["Service Due"].sum()
        license_expiring = maint_df["License Expiry Expiring"].sum()
        driver_expiring = maint_df["Driver License Expiring"].sum()
        git_expiring = maint_df["GIT Insurance Expiring"].sum()
        
        # Display exactly 4 KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(kpi_card("Due Services", int(overdue_services), emoji="🔧"), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("License Expiry", license_expiring, emoji="📝"), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Driver License", driver_expiring, emoji="👤"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("Insurance", git_expiring, emoji="🛡️"), unsafe_allow_html=True)
        
        # Maintenance charts
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
                    hover_data=["Current Mileage", "Last Service Mileage"]
                )
                fig1.add_hline(
                    y=10000,
                    line_dash="dash",
                    line_color=ACCENT_GOLD,
                    annotation_text="Service Threshold"
                )
                fig1 = apply_chart_style(fig1, "KM Since Last Service")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Filter for expiring documents only
                expiring_df = maint_df[
                    maint_df["License Expiry Expiring"] |
                    maint_df["Driver License Expiring"] |
                    maint_df["GIT Insurance Expiring"]
                ]
                
                if not expiring_df.empty:
                    date_cols = ["Vehicle License Expiry", "Driver License Expiry", "GIT Insurance Expiry"]
                    # Calculate days left for each document type
                    days_matrix = expiring_df[date_cols].apply(
                        lambda col: (col - today).dt.days
                    )
                    days_matrix = days_matrix.clip(lower=0, upper=30)
                    
                    fig2 = go.Figure(data=go.Heatmap(
                        z=days_matrix.values,
                        x=days_matrix.columns,
                        y=expiring_df["TruckID"],
                        colorscale=[[0, "darkred"], [0.2, "orangered"], [0.5, "orange"], [0.8, "yellow"], [1, "lightyellow"]],
                        colorbar=dict(
                            title="Days to Expiry",
                            tickvals=[0, 10, 20, 30],
                            ticktext=["0 (Expired)", "10", "20", "30+"]
                        ),
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
    st.markdown("#### 🔔 Actionable Alerts")
    
    try:
        # Prepare financial data for alerts
        cost_df = filtered_ops.copy()
        cost_df = cost_df.merge(loi[["Route Code", "Rate per ton"]], on="Route Code", how="left")
        cost_df = cost_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        cost_df = cost_df.merge(tracker[["TruckID", "Distance (km)"]], on="TruckID", how="left")
        cost_df = cost_df.merge(vcs[["TruckID", "Fuel Cost (R/km)", "Maintenance Cost (R/km)", 
                                    "Tyres (R/km)", "Daily Fixed Cost (R/day)"]], on="TruckID", how="left")
        
        # Calculate financial metrics
        cost_df["Revenue (R)"] = cost_df["Ton Reg"] * cost_df["Rate per ton"]
        cost_df["Variable Cost (R)"] = cost_df["Distance (km)"] * (
            cost_df["Fuel Cost (R/km)"] + cost_df["Maintenance Cost (R/km)"] + cost_df["Tyres (R/km)"]
        )
        cost_df["Total Cost (R)"] = cost_df["Variable Cost (R)"] + cost_df["Daily Fixed Cost (R/day)"]
        cost_df["Profit (R)"] = cost_df["Revenue (R)"] - cost_df["Total Cost (R)"]
        
        # Top performers
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
        
        # Optimization opportunities
        st.markdown("### ⚡ Optimization Opportunities")
        
        # Fuel efficiency alerts
        fuel_df = filtered_ops[filtered_ops["Doc Type"] == "Fuel"].copy()
        if "Distance (km)" in loi.columns:
            fuel_df = fuel_df.merge(loi[["Route Code", "Distance (km)"]], on="Route Code", how="left")
            fuel_df = fuel_df.rename(columns={"Distance (km)": "Distance"})
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
        
        # Loss-making routes
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

"""
PrimeTower Fleet Dashboard – Enterprise Edition
Same business logic, upgraded visual polish.
"""

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
PRIMARY_BG     = "#000000"
ACCENT_TEAL    = "#008080"
ACCENT_GOLD    = "#D4AF37"
SECONDARY_NAVY = "#0A1F44"
WHITE          = "#FFFFFF"
LIGHT_GRAY     = "#F8F9FA"

COLOR_MAP = {
    "Revenue": ACCENT_GOLD,
    "Cost": "#d32f2f",
    "Profit": ACCENT_TEAL,
    "Fuel": "#ffa726",
    "Efficiency": "#26a69a",
    "Fixed Cost": "#9c27b0",
    "Variable Cost": "#d32f2f",
    True: "#d32f2f",
    False: "#2e7d32"
}

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
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Poppins:wght@600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            background-color: {PRIMARY_BG};
            color: {WHITE};
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Poppins', sans-serif;
            color: {WHITE};
        }}
        .metric-card {{
            background-color: {SECONDARY_NAVY};
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
            border-left: 4px solid {ACCENT_TEAL};
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 110px;
        }}
        .metric-card h3 {{
            font-size: 0.9rem;
            font-weight: 600;
            color: {LIGHT_GRAY};
            margin: 0 0 0.2rem 0;
            letter-spacing: .5px;
        }}
        .metric-card p {{
            font-size: 1.2rem;
            font-weight: 700;
            color: {ACCENT_GOLD};
            margin: 0;
        }}
        .metric-card .emoji {{
            font-size: 1.2rem;
            margin-right: 6px;
        }}
        [data-testid="stSidebar"] {{
            background-color: {SECONDARY_NAVY} !important;
            border-right: 2px solid {ACCENT_TEAL};
        }}
        .stTabs [role="tab"] {{
            font-family: 'Poppins', sans-serif;
            font-size: 0.95rem;
            color: {ACCENT_TEAL};
            padding: 0.6rem 1rem;
            border-radius: 8px;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {ACCENT_TEAL};
            color: {WHITE};
        }}
        .filter-container {{
            background-color: {SECONDARY_NAVY};
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid {ACCENT_TEAL};
        }}
        .filter-title {{
            font-family: 'Poppins', sans-serif;
            color: {ACCENT_TEAL};
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
            font-weight: 600;
        }}
        .dataframe {{
            border: none !important;
        }}
        .dataframe th, .dataframe td {{
            background-color: {SECONDARY_NAVY} !important;
            color: {WHITE} !important;
            border: 1px solid {ACCENT_TEAL};
            padding: 8px;
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
    </style>
    """, unsafe_allow_html=True)

def configure_chart_theme():
    pio.templates["prime_theme"] = go.layout.Template(
        layout=go.Layout(
            font=dict(family="Inter", size=12, color=WHITE),
            title=dict(font=dict(size=16, family="Poppins", color=WHITE)),
            paper_bgcolor=PRIMARY_BG,
            plot_bgcolor=SECONDARY_NAVY,
            margin=dict(l=40, r=20, t=50, b=40),
            xaxis=dict(showgrid=True, gridcolor="#333333"),
            yaxis=dict(showgrid=True, gridcolor="#333333"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=10, family="Inter")
            ),
            colorway=[ACCENT_TEAL, "#d32f2f", ACCENT_GOLD, "#ffa726", "#26a69a"]
        )
    )
    pio.templates.default = "prime_theme"

apply_custom_styles()
configure_chart_theme()

# =============================================================================
# UTILITIES
# =============================================================================

def apply_chart_style(fig, title, height=400):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Poppins", size=16, color=WHITE)),
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )
    return fig

def kpi_card(title, value, emoji=None):
    emoji_html = f'<span class="emoji">{emoji}</span>' if emoji else ""
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
            tracker    = pd.read_csv("data/demo_tracker.csv")
            loi        = pd.read_csv("data/demo_loi.csv")
            truck_pak  = pd.read_csv("data/demo_truck_pak.csv")
            vcs        = pd.read_csv("data/demo_vcs.csv")
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
            return pd.DataFrame(
                client.open_by_key("1QYHK9DoiBjJPLrQlovHxDkRuv4xImwtzbokul_rOdjI")
                .worksheet(sheet_name).get_all_records()
            )
        return (
            get_worksheet_df("operations"),
            get_worksheet_df("tracker"),
            get_worksheet_df("loi"),
            get_worksheet_df("truck_pak"),
            get_worksheet_df("vehicle_cost_schedule")
        )

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
# SIDEBAR NAV
# =============================================================================

with st.sidebar:
    st.markdown(f"<h4 style='color: {ACCENT_TEAL}; text-align:center;'>Welcome, {st.session_state.username}</h4>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=["Home", "Financials", "Operations", "Fuel", "Maintenance", "Alerts"],
        icons=["house", "cash-stack", "speedometer", "fuel-pump", "tools", "bell"],
        menu_icon="cast",
        default_index=0 if st.session_state.first_visit else 1,
        styles={
            "container": {"padding": "5px", "background-color": SECONDARY_NAVY},
            "icon": {"color": ACCENT_GOLD, "font-size": "18px"},
            "nav-link": {"color": WHITE, "font-size": "15px", "text-align": "left", "margin": "5px", "--hover-color": ACCENT_TEAL},
            "nav-link-selected": {"background-color": ACCENT_TEAL},
        }
    )

    with st.form("filters_form"):
        st.markdown('<p class="filter-title">FILTERS</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            month_disp = st.selectbox("Month", available_months_display, index=len(available_months_display)-1, key="month_select")
        with c2:
            truck = st.selectbox("Truck", ["All"] + sorted(truck_pak["TruckID"].unique()), index=0, key="truck_select")
        with c3:
            route = st.selectbox("Route", ["All"] + sorted(loi["Route Code"].unique()), index=0, key="route_select")
        submitted = st.form_submit_button("Apply Filters", type="primary", use_container_width=True)
        if submitted:
            st.session_state.month_filter = month_disp
            st.session_state.truck_filter = truck
            st.session_state.route_filter = route
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# =============================================================================
# DATA FILTERING
# =============================================================================

selected_month_display = st.session_state.get("month_filter", available_months_display[-1])
selected_truck         = st.session_state.get("truck_filter", "All")
selected_route         = st.session_state.get("route_filter", "All")
selected_month         = month_dict[selected_month_display]

def apply_filters(df, month, truck, route):
    filtered = df[df["Year-Month"] == month]
    if truck != "All":
        filtered = filtered[filtered["TruckID"] == truck]
    if route != "All":
        filtered = filtered[filtered["Route Code"] == route]
    return filtered

filtered_ops = apply_filters(operations, selected_month, selected_truck, selected_route)

# =============================================================================
# PAGE CONTENT (unchanged logic, only chart styling handled above)
# =============================================================================

if selected == "Home":
    st.session_state.first_visit = False
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: {ACCENT_TEAL}; margin-bottom: 0;'>
                <span style='font-size: 1.5em;'>🚛</span> Welcome Back, {st.session_state.username}
            </h1>
            <p style='font-size: 1.1rem; color: {LIGHT_GRAY};'>
                Your fleet at a glance • Last updated: {datetime.now().strftime("%d %b %Y %H:%M")}
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(kpi_card("Active Trucks", "12", emoji="🚚"), unsafe_allow_html=True)
        st.markdown(kpi_card("Today's Trips", "24", emoji="🛣️"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Fuel Efficiency", "3.2 km/L", emoji="⛽"), unsafe_allow_html=True)
        st.markdown(kpi_card("Avg Load", "18.5T", emoji="📦"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Today's Revenue", "R42,380", emoji="💰"), unsafe_allow_html=True)
        st.markdown(kpi_card("Alerts", "2", emoji="⚠️"), unsafe_allow_html=True)

    # … (rest of existing Home tab code unchanged)

# -----------------------------------------------------------------------------
# FINANCIALS TAB
elif selected == "Financials":
    st.markdown(f"<h4 style='color: {ACCENT_TEAL};'>Financials Overview</h4>", unsafe_allow_html=True)
    try:
        cost_df = filtered_ops.copy()
        cost_df = cost_df.merge(loi[["Route Code", "Rate per ton"]], on="Route Code", how="left")
        cost_df = cost_df.merge(truck_pak[["TruckID", "Driver Name"]], on="TruckID", how="left")
        cost_df = cost_df.merge(tracker[["TruckID", "Distance (km)"]], on="TruckID", how="left")
        cost_df = cost_df.merge(vcs[["TruckID", "Fuel Cost (R/km)", "Maintenance Cost (R/km)", "Tyres (R/km)", "Daily Fixed Cost (R/day)"]], on="TruckID", how="left")

        cost_df["Revenue (R)"] = cost_df["Ton Reg"] * cost_df["Rate per ton"]
        cost_df["Variable Cost (R)"] = cost_df["Distance (km)"] * (
            cost_df["Fuel Cost (R/km)"] + cost_df["Maintenance Cost (R/km)"] + cost_df["Tyres (R/km)"]
        )
        cost_df["Total Cost (R)"] = cost_df["Variable Cost (R)"] + cost_df["Daily Fixed Cost (R/day)"]
        cost_df["Profit (R)"] = cost_df["Revenue (R)"] - cost_df["Total Cost (R)"]

        total_revenue = cost_df["Revenue (R)"].sum()
        total_cost = cost_df["Total Cost (R)"].sum()
        avg_cost_per_km = (cost_df["Total Cost (R)"] / cost_df["Distance (km)"]).mean()
        profit_margin = (cost_df["Profit (R)"].sum() / cost_df["Revenue (R)"].sum()) if cost_df["Revenue (R)"].sum() > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(kpi_card("Total Revenue", f"R{total_revenue:,.2f}", emoji="💰"), unsafe_allow_html=True)
        with c2: st.markdown(kpi_card("Total Cost", f"R{total_cost:,.2f}", emoji="📉"), unsafe_allow_html=True)
        with c3: st.markdown(kpi_card("Avg Cost/km", f"R{avg_cost_per_km:,.2f}", emoji="🛣️"), unsafe_allow_html=True)
        with c4: st.markdown(kpi_card("Profit Margin", f"{profit_margin:.1%}", emoji="📈"), unsafe_allow_html=True)

        st.caption(f"Data from {cost_df['Date'].min().date()} to {cost_df['Date'].max().date()}")

        grouped_cost = cost_df.groupby("TruckID").agg({
            "Revenue (R)": "sum",
            "Variable Cost (R)": "sum",
            "Daily Fixed Cost (R/day)": "sum",
            "Total Cost (R)": "sum",
            "Profit (R)": "sum"
        }).reset_index()

        c1, c2 = st.columns(2)
        with c1:
            df_plot = grouped_cost[["TruckID", "Variable Cost (R)", "Daily Fixed Cost (R/day)"]].melt(id_vars="TruckID", var_name="Cost Type", value_name="Cost (R)")
            fig = px.bar(df_plot, x="TruckID", y="Cost (R)", color="Cost Type", barmode="stack", title="Cost Structure by Truck", color_discrete_map=COLOR_MAP)
            st.plotly_chart(apply_chart_style(fig, "Cost Structure by Truck"), use_container_width=True)

        with c2:
            fig2 = px.bar(grouped_cost, x="TruckID", y="Profit (R)", color="Profit (R)", color_continuous_scale=[(0, "#d32f2f"), (1, ACCENT_TEAL)], title="Profit by Truck")
            st.plotly_chart(apply_chart_style(fig2, "Profit by Truck"), use_container_width=True)

        route_profit = cost_df.groupby("Route Code").agg({"Revenue (R)": "mean", "Total Cost (R)": "mean", "Profit (R)": "mean", "Ton Reg": "sum"}).reset_index()
        fig3 = px.scatter(route_profit, x="Revenue (R)", y="Total Cost (R)", size="Ton Reg", color="Profit (R)", hover_name="Route Code",
                          title="Route Profitability (Bubble Size = Total Tons)", color_continuous_scale=[(0, "#d32f2f"), (1, ACCENT_TEAL)], size_max=40)
        max_val = route_profit[["Revenue (R)", "Total Cost (R)"]].max().max() * 1.1
        fig3.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(dash="dash", color=WHITE))
        st.plotly_chart(apply_chart_style(fig3, "Route Profitability"), use_container_width=True)

    except Exception as e:
        st.error(f"Error in Financials tab: {str(e)}")

# -----------------------------------------------------------------------------
# OPERATIONS TAB
elif selected == "Operations":
    st.markdown(f"<h4 style='color: {ACCENT_TEAL};'>Operations Dashboard</h4>", unsafe_allow_html=True)
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

# -----------------------------------------------------------------------------
# FUEL TAB
elif selected == "Fuel":
    st.markdown(f"<h4 style='color: {ACCENT_TEAL};'>Fuel Efficiency Dashboard</h4>", unsafe_allow_html=True)
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

# -----------------------------------------------------------------------------
# MAINTENANCE TAB
elif selected == "Maintenance":
    st.markdown(f"<h4 style='color: {ACCENT_TEAL};'>Maintenance Dashboard</h4>", unsafe_allow_html=True)
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

# -----------------------------------------------------------------------------
# ALERTS TAB
elif selected == "Alerts":
    st.markdown(f"<h4 style='color: {ACCENT_TEAL};'>Actionable Alerts</h4>", unsafe_allow_html=True)
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

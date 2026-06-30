import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from agents import run_conversational_audit

# Load environment variables (such as GEMINI_API_KEY)
load_dotenv()

# 1. Configure page settings (Wide layout with an enterprise title)
st.set_page_config(
    page_title="Conversational Enterprise Expense Auditor",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject premium dark theme CSS with custom fonts, glassmorphism, and gradient accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Main background and font */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 50%, #0F172A 0%, #020617 100%);
        color: #F1F5F9;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Custom Title and Subtitle */
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 5px;
        color: #F8FAFC;
        margin-top: -50px;
    }

    .gradient-text {
        background: linear-gradient(135deg, #6366F1 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 35px;
    }

    /* Custom Metrics Cards Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin-bottom: 35px;
    }

    .card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px -15px rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.3);
    }

    .card-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #94A3B8;
        margin-bottom: 12px;
        font-weight: 600;
    }

    .card-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.1;
        margin-bottom: 8px;
    }

    .card-sub {
        font-size: 0.75rem;
        color: #64748B;
    }

    /* Custom styles for headers and other elements */
    h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: #F8FAFC;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* Style Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #94A3B8;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC;
        background-color: rgba(99, 102, 241, 0.1);
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(99, 102, 241, 0.15) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #6366F1 !important;
    }

    /* Custom Sidebar Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #06B6D4 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Build the Sidebar
st.sidebar.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-audit-business-and-finance-flatart-icons-flat-flatarticons.png", width=60)
st.sidebar.markdown("<h2 style='margin-top:10px;'>Auditor Controls</h2>", unsafe_allow_html=True)

default_narrative = (
    "Yesterday I spent 65.20 dollars on a Team Dinner. I also renewed our Server "
    "Hosting subscription which cost 45.00. This morning I booked a Flight Ticket "
    "for 620.00 and bought a Client Coffee for 12.50."
)

narrative_input = st.sidebar.text_area(
    "📝 Expense Narrative",
    value=default_narrative,
    height=180,
    help="Enter unstructured conversational text detailing corporate expenses."
)

run_audit = st.sidebar.button("⚡ Run Conversational Audit")

# 4. Use st.session_state to store and persist audit results
if "audit_results" not in st.session_state:
    st.session_state.audit_results = None

# 5. Execute audit when triggered
if run_audit:
    with st.spinner("🔍 Executing 4-stage compliance audit pipeline..."):
        try:
            results = run_conversational_audit(narrative_input)
            st.session_state.audit_results = results
            st.toast("Audit completed successfully!", icon="✅")
        except Exception as e:
            st.error(f"Error executing audit: {e}")

# Header Section
st.markdown("""
<h1 class='main-title'>
  <span class='gradient-text'>Conversational Enterprise</span> Expense Auditor
</h1>
<div class='subtitle'>Automated single-pass compliance auditing powered by Google Gemini 2.5</div>
""", unsafe_allow_html=True)

# 6. Main Dashboard Layout (Visible only when session state contains data)
if st.session_state.audit_results is not None:
    # Convert results to DataFrame for easier analysis
    df = pd.DataFrame(st.session_state.audit_results)
    
    if not df.empty:
        # Calculate Metrics
        total_spend = df['amount'].sum()
        total_items = len(df)
        violations_count = len(df[df['status'] == 'VIOLATION'])
        compliance_rate = ((total_items - violations_count) / total_items) * 100 if total_items > 0 else 0
        
        # --- Executive Summary Row ---
        st.markdown(f"""
        <div class="metrics-grid">
            <div class="card">
                <div class="card-label">Total Extracted Spend</div>
                <div class="card-value">${total_spend:,.2f}</div>
                <div class="card-sub">Aggregated from narrative</div>
            </div>
            <div class="card">
                <div class="card-label">Identified Items</div>
                <div class="card-value">{total_items}</div>
                <div class="card-sub">Distinct expenses found</div>
            </div>
            <div class="card">
                <div class="card-label">Policy Violations</div>
                <div class="card-value" style="color: #F43F5E;">{violations_count}</div>
                <div class="card-sub" style="color: #F43F5E;">Requires manual override</div>
            </div>
            <div class="card">
                <div class="card-label">Compliance Rate</div>
                <div class="card-value" style="color: #10B981;">{compliance_rate:.1f}%</div>
                <div class="card-sub">Target threshold: > 90.0%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- Analytics Row ---
        st.markdown("### 📊 Compliance Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Status Distribution")
            status_counts = df['status'].value_counts()
            status_df = pd.DataFrame({
                'Status': status_counts.index,
                'Count': status_counts.values
            }).set_index('Status')
            # Plot native bar chart
            st.bar_chart(status_df, height=280)
            
        with col2:
            st.markdown("#### Spend Footprint by Category")
            category_spend = df.groupby('category')['amount'].sum()
            category_df = pd.DataFrame({
                'Category': category_spend.index,
                'Spend ($)': category_spend.values
            }).set_index('Category')
            # Plot native bar chart
            st.bar_chart(category_df, height=280)
            
        # --- Data Table Row ---
        st.markdown("### 📋 Audit Ledger & Verification")
        tab1, tab2, tab3 = st.tabs(["All Records", "Approved Clean Items", "Flagged Violations"])
        
        # Columns formatting config
        column_config = {
            "item": st.column_config.TextColumn("Item / Description", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "amount": st.column_config.NumberColumn("Amount", format="$%.2f", width="small"),
            "status": st.column_config.SelectboxColumn(
                "Status", 
                options=["APPROVED", "VIOLATION"],
                width="small"
            ),
            "reason": st.column_config.TextColumn("Audit Reason / Details", width="large")
        }
        
        with tab1:
            st.dataframe(
                df[["item", "category", "amount", "status", "reason"]],
                column_config=column_config,
                use_container_width=True,
                hide_index=True
            )
            
        with tab2:
            approved_df = df[df['status'] == 'APPROVED']
            if not approved_df.empty:
                st.dataframe(
                    approved_df[["item", "category", "amount", "status", "reason"]],
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No approved items found in this audit.")
                
        with tab3:
            violations_df = df[df['status'] == 'VIOLATION']
            if not violations_df.empty:
                st.dataframe(
                    violations_df[["item", "category", "amount", "status", "reason"]],
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("🎉 Excellent! No policy violations were detected.")
    else:
        st.warning("No expense items could be extracted. Please check the narrative formatting.")

else:
    # 7. Welcoming st.info message advising the user to begin
    st.info("👋 **Welcome to the Conversational Expense Auditor!** Please enter your expense narrative in the sidebar and click the **⚡ Run Conversational Audit** button to extract items and verify compliance.")
    
    # Beautiful Policy Guide Card shown when idle
    st.markdown("""
    <div class="card" style="margin-top: 25px; border-left: 5px solid #6366F1;">
        <h3 style="color: #F8FAFC; margin-top: 0; font-size: 1.3rem;">📋 Corporate Expense Policy Guidelines</h3>
        <p style="color: #94A3B8; font-size: 0.95rem;">
            This system runs an automated audit against corporate spend limits. Any item exceeding the defined threshold will be flagged as a <strong>VIOLATION</strong>.
        </p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px; color: #F1F5F9; font-size: 0.9rem;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); text-align: left;">
                    <th style="padding: 8px 0; color: #6366F1;">Expense Category</th>
                    <th style="padding: 8px 0; color: #6366F1;">Threshold Limit</th>
                    <th style="padding: 8px 0; color: #6366F1;">Policy Description</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 10px 0; font-weight: 600;">Meals</td>
                    <td style="padding: 10px 0; color: #10B981;">Max $50.00</td>
                    <td style="padding: 10px 0; color: #94A3B8;">Covers client lunches, team dinners, coffee meetings, and travel dining.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 10px 0; font-weight: 600;">Software</td>
                    <td style="padding: 10px 0; color: #10B981;">Max $100.00</td>
                    <td style="padding: 10px 0; color: #94A3B8;">Covers subscriptions, developer tools, cloud hosting, and SaaS products.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 10px 0; font-weight: 600;">Travel</td>
                    <td style="padding: 10px 0; color: #10B981;">Max $500.00</td>
                    <td style="padding: 10px 0; color: #94A3B8;">Covers flights, hotel bookings, trains, car rentals, and long-distance transport.</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

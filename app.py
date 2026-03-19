"""
Super-Scraper - AI-Powered Lead Generation Platform
Built with LangGraph, Streamlit, and advanced AI agents
"""
import streamlit as st
from agents.graph import graph
from agents.state import create_initial_state
from database import db
from datetime import datetime
import uuid
import json

# Page config
st.set_page_config(
    page_title="Super-Scraper",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .agent-message {
        padding: 10px;
        border-left: 3px solid #667eea;
        background-color: #f0f2f6;
        margin: 5px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "job_results" not in st.session_state:
    st.session_state.job_results = None
if "job_messages" not in st.session_state:
    st.session_state.job_messages = []

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 Super-Scraper")
    st.markdown("AI-Powered Lead Generation")
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    total_leads = len(db.get_all_leads())
    st.metric("Total Leads", total_leads)
    
    st.markdown("---")
    st.markdown("### 🔑 API Status")
    
    from config import settings
    
    if settings.google_api_key:
        st.success("✅ Google Gemini Connected")
    else:
        st.error("❌ Google Gemini Not Configured")
    
    if settings.serpapi_key:
        st.success("✅ SerpAPI Connected")
    else:
        st.warning("⚠️ SerpAPI Not Configured")
    
    if settings.tavily_api_key:
        st.success("✅ Tavily Connected")
    else:
        st.warning("⚠️ Tavily Not Configured")

# Main content
st.markdown('<h1 class="main-header">🚀 Super-Scraper</h1>', unsafe_allow_html=True)
st.markdown("**The AI platform that finds, scrapes, and qualifies leads automatically**")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Advanced Scraper",
    "💼 Lead Database",
    "📞 Sales & Outreach (Coming Soon)",
    "⚙️ Settings"
])

# TAB 1: SCRAPER
with tab1:
    st.markdown("### 💬 What do you want to find?")
    
    # Example queries
    with st.expander("📝 Example Queries"):
        st.markdown("""
        - **Local Businesses:** "Find gyms in Austin without websites"
        - **Lead Generation:** "Find companies that just got Series A funding"
        - **Wedding Services:** "All wedding-related businesses within 5km of downtown Miami"
        - **Tech Startups:** "YC-backed startups hiring AI engineers"
        - **Real Estate:** "Real estate agencies on Google Maps without active websites"
        """)
    
    # Query input
    user_query = st.text_area(
        "Enter your search query:",
        height=100,
        placeholder="Example: Find all gyms in San Francisco that don't have a website"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        run_button = st.button("🚀 Run Scraper", type="primary", use_container_width=True)
    
    if run_button and user_query:
        # Create initial state
        initial_state = create_initial_state(user_query)
        job_id = str(uuid.uuid4())
        
        # Save job to database
        db.save_job({
            "job_id": job_id,
            "query": user_query,
            "status": "running"
        })
        
        st.markdown("---")
        st.markdown("### 🤖 AI Agents Working...")
        
        # Progress containers
        progress_container = st.container()
        messages_container = st.container()
        
        # Run the LangGraph workflow
        config = {"configurable": {"thread_id": job_id}}
        
        all_messages = []
        
        with st.spinner("Processing your request..."):
            try:
                # Stream the workflow
                for output in graph.stream(initial_state, config):
                    for node_name, node_output in output.items():
                        # Display messages
                        if "messages" in node_output:
                            for msg in node_output["messages"]:
                                all_messages.append(msg)
                                with messages_container:
                                    st.markdown(f'<div class="agent-message">{msg}</div>', unsafe_allow_html=True)
                
                # Get final state
                final_state = graph.get_state(config)
                leads = final_state.values.get("leads", [])
                
                st.session_state.job_results = leads
                st.session_state.job_messages = all_messages
                
                # Save leads to database
                for lead in leads:
                    db.save_lead({
                        **lead,
                        "query_type": final_state.values.get("query_type")
                    })
                
                st.success(f"✅ Complete! Found {len(leads)} leads")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)
    
    # Display results
    if st.session_state.job_results:
        st.markdown("---")
        st.markdown("### 📊 Results")
        
        leads = st.session_state.job_results
        
        if leads:
            # Convert to list of dicts for display
            leads_data = []
            for lead in leads:
                leads_data.append({
                    "Company": lead.get("company_name", "N/A"),
                    "Website": lead.get("website", "N/A"),
                    "Phone": lead.get("phone", "N/A"),
                    "Email": lead.get("email", "N/A"),
                    "Address": lead.get("address", "N/A"),
                    "Rating": lead.get("rating", "N/A")
                })
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Leads", len(leads))
            col2.metric("With Website", len([l for l in leads if l.get("website")]))
            col3.metric("With Phone", len([l for l in leads if l.get("phone")]))
            col4.metric("With Email", len([l for l in leads if l.get("email")]))
            
            # Display table
            st.table(leads_data)
            
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV export
                import io
                csv_buffer = io.StringIO()
                # Write CSV manually
                if leads_data:
                    keys = leads_data[0].keys()
                    csv_buffer.write(','.join(keys) + '\n')
                    for row in leads_data:
                        csv_buffer.write(','.join(str(row[k]) for k in keys) + '\n')
                    
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = json.dumps(leads, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        else:
            st.info("No leads found. Try refining your query.")

# TAB 2: LEAD DATABASE
with tab2:
    st.markdown("### 💼 Lead Database")
    
    all_leads = db.get_all_leads(limit=500)
    
    if all_leads:
        # Convert to list of dicts for display
        leads_data = []
        for lead in all_leads:
            leads_data.append({
                "ID": lead.id,
                "Company": lead.company_name,
                "Website": lead.website or "N/A",
                "Phone": lead.phone or "N/A",
                "Email": lead.email or "N/A",
                "Address": lead.address or "N/A",
                "Rating": lead.rating or "N/A",
                "Status": lead.website_status,
                "Found": lead.found_at.strftime("%Y-%m-%d %H:%M")
            })
        
        st.table(leads_data)
        
        # Export all leads
        import io
        csv_buffer = io.StringIO()
        if leads_data:
            keys = leads_data[0].keys()
            csv_buffer.write(','.join(keys) + '\n')
            for row in leads_data:
                csv_buffer.write(','.join(str(row[k]) for k in keys) + '\n')
        
        st.download_button(
            label="📥 Export All Leads (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"all_leads_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No leads in database yet. Run a scraper job to find leads!")

# TAB 3: SALES & OUTREACH
with tab3:
    st.markdown("### 📞 Sales & Outreach")
    st.info("🚧 Coming Soon: Automated outreach, voice calling (ElevenLabs), email campaigns")
    
    st.markdown("""
    **Future Features:**
    - 📧 Email campaign builder
    - 📞 Automated voice calls with ElevenLabs
    - 📅 Calendar scheduling integration
    - 🤖 AI sales assistant
    - 📊 Outreach analytics
    """)

# TAB 4: SETTINGS
with tab4:
    st.markdown("### ⚙️ Settings")
    
    st.markdown("#### API Configuration")
    st.info("Edit the `.env` file to configure API keys")
    
    st.markdown("#### Current Configuration")
    
    config_status = {
        "Google Gemini API": "✅ Configured" if settings.google_api_key else "❌ Not configured",
        "SerpAPI (Maps)": "✅ Configured" if settings.serpapi_key else "❌ Not configured",
        "Tavily (Search)": "✅ Configured" if settings.tavily_api_key else "❌ Not configured",
    }
    
    for service, status in config_status.items():
        st.markdown(f"**{service}:** {status}")
    
    st.markdown("---")
    st.markdown("#### Database")
    st.text(f"Location: {settings.database_path}")
    
    if st.button("🗑️ Clear All Leads (Dangerous!)"):
        st.warning("This feature is not yet implemented for safety")

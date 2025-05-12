import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import csv
import io

# Initialize session state
if 'mode_data' not in st.session_state:
    st.session_state.mode_data = {
        'Child Safe Mode': {'whitelist': [], 'blacklist': []},
        'High School Teen Safe Mode': {'whitelist': [], 'blacklist': []},
        'Custom Mode': {'whitelist': [], 'blacklist': []}
    }

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'Child Safe Mode'

# Page config
st.set_page_config(
    page_title="Content Filter",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
        color: #1f1f1f;
    }
    .stButton button {
        background-color: #f0f2f6;
        color: #1f1f1f;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #e6e9ef;
        border-color: #d0d0d0;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff;
        color: #1f1f1f;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 0.75rem;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #7c8db0;
        box-shadow: 0 0 0 1px #7c8db0;
    }
    .stSelectbox [data-testid='stSelectbox'] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
    }
    div[data-testid='stToolbar'] {
        display: none;
    }
    div[data-testid='stSidebarNav'] {
        background-color: #f8f9fa;
    }
    .stAlert {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
    }
    .css-1dp5vir {
        background-color: #ffffff;
    }
    .css-1p05t8e {
        border-right-color: #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# Add custom fonts
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# Application header
st.title("Content Filter")

# Info container
with st.container():
    st.markdown("### CSCW Concepts")
    st.write("Collaborative Content Moderation • Group Awareness • Access Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### User Groups")
        st.markdown("""
        - **Moderators**  
          Create and manage filtering rules
        - **Content Creators**  
          Use filters to ensure content meets guidelines
        """)
    
    with col2:
        st.markdown("### Key Features")
        st.markdown("""
        - Collaborative whitelist/blacklist management
        - Multiple safety modes for different contexts
        - Import/Export for team sharing
        - Real-time statistics for group awareness
        """)
    
    st.divider()
col1, col2 = st.columns([2, 3])

with col1:
    selected_mode = st.selectbox(
        "Select Mode",
        options=['Child Safe Mode', 'High School Teen Safe Mode', 'Custom Mode'],
        index=list(['Child Safe Mode', 'High School Teen Safe Mode', 'Custom Mode']).index(st.session_state.current_mode)
    )

    if selected_mode != st.session_state.current_mode:
        st.session_state.current_mode = selected_mode

# Description based on mode
mode_descriptions = {
    'Child Safe Mode': 'Strict filtering for children.',
    'High School Teen Safe Mode': 'Moderate filtering for teens.',
    'Custom Mode': 'Customize your own filtering.'
}
with col2:
    st.info(mode_descriptions[st.session_state.current_mode])

# Main content
col_wl, col_bl = st.columns(2)

# Whitelist column
with col_wl:
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #2e7d32; margin-bottom: 1rem;'>Whitelist</h3>", unsafe_allow_html=True)
    wl_input = st.text_input("Add to whitelist...", key="wl_input")
    if st.button("Add to Whitelist"):
        item = wl_input.strip()
        if item and item not in st.session_state.mode_data[st.session_state.current_mode]['whitelist']:
            st.session_state.mode_data[st.session_state.current_mode]['whitelist'].append(item)
            st.success(f"Added '{item}' to whitelist")

    # Show whitelist items
    wl_items = st.session_state.mode_data[st.session_state.current_mode]['whitelist']
    if wl_items:
        selected_wl = st.multiselect(
            "Current whitelist items:",
            options=wl_items,
            default=wl_items,
            key="wl_select"
        )
        if len(selected_wl) < len(wl_items):
            removed = set(wl_items) - set(selected_wl)
            st.session_state.mode_data[st.session_state.current_mode]['whitelist'] = selected_wl
            st.warning(f"Removed {', '.join(removed)} from whitelist")

# Blacklist column
with col_bl:
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #c62828; margin-bottom: 1rem;'>Blacklist</h3>", unsafe_allow_html=True)
    bl_input = st.text_input("Add to blacklist...", key="bl_input")
    if st.button("Add to Blacklist"):
        item = bl_input.strip()
        if item and item not in st.session_state.mode_data[st.session_state.current_mode]['blacklist']:
            st.session_state.mode_data[st.session_state.current_mode]['blacklist'].append(item)
            st.success(f"Added '{item}' to blacklist")

    # Show blacklist items
    bl_items = st.session_state.mode_data[st.session_state.current_mode]['blacklist']
    if bl_items:
        selected_bl = st.multiselect(
            "Current blacklist items:",
            options=bl_items,
            default=bl_items,
            key="bl_select"
        )
        if len(selected_bl) < len(bl_items):
            removed = set(bl_items) - set(selected_bl)
            st.session_state.mode_data[st.session_state.current_mode]['blacklist'] = selected_bl
            st.warning(f"Removed {', '.join(removed)} from blacklist")

# Sidebar for additional features
with st.sidebar:
    st.markdown("<h2 style='font-size: 1.5rem; font-weight: 500; color: #1f1f1f; margin-bottom: 1.5rem;'>Tools</h2>", unsafe_allow_html=True)
    
    # Statistics
    if st.button("Show Statistics", use_container_width=True):
        st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #1f1f1f; margin: 1rem 0;'>Statistics</h3>", unsafe_allow_html=True)
        whitelist = st.session_state.mode_data[st.session_state.current_mode]['whitelist']
        blacklist = st.session_state.mode_data[st.session_state.current_mode]['blacklist']
        
        col_wl_stats, col_bl_stats = st.columns(2)
        
        with col_wl_stats:
            st.markdown("**Whitelist Stats:**")
            st.write(f"Total items: {len(whitelist)}")
            if whitelist:
                st.write(f"Avg length: {sum(len(x) for x in whitelist) / len(whitelist):.1f}")
                st.write(f"Shortest: {min((len(x), x) for x in whitelist)[1]}")
                st.write(f"Longest: {max((len(x), x) for x in whitelist)[1]}")
        
        with col_bl_stats:
            st.markdown("**Blacklist Stats:**")
            st.write(f"Total items: {len(blacklist)}")
            if blacklist:
                st.write(f"Avg length: {sum(len(x) for x in blacklist) / len(blacklist):.1f}")
                st.write(f"Shortest: {min((len(x), x) for x in blacklist)[1]}")
                st.write(f"Longest: {max((len(x), x) for x in blacklist)[1]}")

    # Sorting
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #1f1f1f; margin: 1.5rem 0 1rem;'>Sort Lists</h3>", unsafe_allow_html=True)
    if st.button("Sort Ascending"):
        for list_type in ['whitelist', 'blacklist']:
            st.session_state.mode_data[st.session_state.current_mode][list_type].sort()
        st.success("Lists sorted in ascending order")
    
    if st.button("Sort Descending"):
        for list_type in ['whitelist', 'blacklist']:
            st.session_state.mode_data[st.session_state.current_mode][list_type].sort(reverse=True)
        st.success("Lists sorted in descending order")

    # Import/Export
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #1f1f1f; margin: 1.5rem 0 1rem;'>Import/Export</h3>", unsafe_allow_html=True)
    
    # Export
    export_format = st.selectbox("Export Format", ["CSV", "TXT"])
    if st.button("Export Lists"):
        if export_format == "CSV":
            data = []
            for item in st.session_state.mode_data[st.session_state.current_mode]['whitelist']:
                data.append(['whitelist', item])
            for item in st.session_state.mode_data[st.session_state.current_mode]['blacklist']:
                data.append(['blacklist', item])
            
            df = pd.DataFrame(data, columns=['Type', 'Item'])
            csv = df.to_csv(index=False)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'content_filter_{st.session_state.current_mode}_{timestamp}.csv'
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=filename,
                mime='text/csv'
            )
        else:  # TXT
            content = f"=== {st.session_state.current_mode} ===\n\n"
            content += "=== Whitelist ===\n"
            content += "\n".join(st.session_state.mode_data[st.session_state.current_mode]['whitelist'])
            content += "\n\n=== Blacklist ===\n"
            content += "\n".join(st.session_state.mode_data[st.session_state.current_mode]['blacklist'])
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'content_filter_{st.session_state.current_mode}_{timestamp}.txt'
            
            st.download_button(
                label="Download TXT",
                data=content,
                file_name=filename,
                mime='text/plain'
            )
    
    # Import
    st.subheader("📥 Import")
    uploaded_file = st.file_uploader("Choose a file to import", type=['csv', 'txt'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                for _, row in df.iterrows():
                    if row['Type'] in ['whitelist', 'blacklist']:
                        if row['Item'] not in st.session_state.mode_data[st.session_state.current_mode][row['Type']]:
                            st.session_state.mode_data[st.session_state.current_mode][row['Type']].append(row['Item'])
            else:  # txt
                content = uploaded_file.getvalue().decode()
                current_list = None
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('=== Whitelist ==='):
                        current_list = 'whitelist'
                    elif line.startswith('=== Blacklist ==='):
                        current_list = 'blacklist'
                    elif line and not line.startswith('===') and current_list:
                        if line not in st.session_state.mode_data[st.session_state.current_mode][current_list]:
                            st.session_state.mode_data[st.session_state.current_mode][current_list].append(line)
            
            st.success("File imported successfully!")
        except Exception as e:
            st.error(f"Error importing file: {str(e)}")

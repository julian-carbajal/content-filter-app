import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import csv
import io
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import Counter

# Functions for loading and saving configurations
def save_configuration(data, filename='content_filter_config.json'):
    """Save filter configuration to a JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return True, f"Configuration saved to {filename}"
    except Exception as e:
        return False, f"Failed to save configuration: {str(e)}"

def load_configuration(filename='content_filter_config.json'):
    """Load filter configuration from a JSON file"""
    try:
        if Path(filename).exists():
            with open(filename) as f:
                return True, json.load(f)
        return False, "Configuration file not found"
    except Exception as e:
        return False, f"Failed to load configuration: {str(e)}"

# Function to load sample data from CSV
def load_sample_data():
    """Load sample filter data from CSV file"""
    try:
        sample_path = Path('sample_filter_data.csv')
        if sample_path.exists():
            df = pd.read_csv(sample_path)
            whitelist_items = df[df['Type'] == 'whitelist']['Item'].tolist()
            blacklist_items = df[df['Type'] == 'blacklist']['Item'].tolist()
            return {
                'Child Safe Mode': {
                    'whitelist': whitelist_items[:10],  # First 10 items for Child Safe Mode
                    'blacklist': blacklist_items
                },
                'High School Teen Safe Mode': {
                    'whitelist': whitelist_items,       # All whitelist items for Teen Mode
                    'blacklist': blacklist_items[5:]   # Skip first 5 blacklist items for Teen Mode
                },
                'Custom Mode': {
                    'whitelist': [],
                    'blacklist': []
                }
            }
        return None
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return None

# Initialize session state
if 'mode_data' not in st.session_state:
    # Try to load from default config first
    success, result = load_configuration()
    if success:
        st.session_state.mode_data = result
    else:
        # Try to load sample data if available
        sample_data = load_sample_data()
        if sample_data:
            st.session_state.mode_data = sample_data
        else:
            # Use default empty values if no data available
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
    layout="wide",
    initial_sidebar_state="expanded"
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

# Content Analysis Section
st.subheader("Content Filter Tester")

with st.expander("Test your content against current filters"):
    test_content = st.text_area(
        "Enter content to test against your filters",
        height=100,
        placeholder="Type or paste content here to analyze..."
    )
    
    if st.button("Analyze Content"):
        if test_content.strip():
            # Get filter lists from current mode
            whitelist = st.session_state.mode_data[st.session_state.current_mode]['whitelist']
            blacklist = st.session_state.mode_data[st.session_state.current_mode]['blacklist']
            
            # Simple content analysis
            words = test_content.lower().split()
            total_words = len(words)
            
            # Check against whitelist and blacklist
            whitelisted = [word for word in words if word in [w.lower() for w in whitelist]]
            blacklisted = [word for word in words if word in [b.lower() for b in blacklist]]
            
            # Determine if content passes the filter
            filter_status = "ALLOWED" if not blacklisted else "BLOCKED"
            
            # Display results
            st.markdown(f"### Analysis Results")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Words", total_words)
            col2.metric("Whitelisted Words", len(whitelisted), f"{len(whitelisted)/total_words*100:.1f}%" if total_words > 0 else "0%")
            col3.metric("Blacklisted Words", len(blacklisted), f"{len(blacklisted)/total_words*100:.1f}%" if total_words > 0 else "0%")
            
            # Display filter status with appropriate styling
            if filter_status == "ALLOWED":
                st.success("✅ This content would be **ALLOWED** by your current filter settings.")
            else:
                st.error("❌ This content would be **BLOCKED** by your current filter settings.")
                
            # Show detected words
            if blacklisted:
                st.markdown("**Detected blacklisted words:**")
                st.write(', '.join([f"'{word}'" for word in set(blacklisted)]))
        else:
            st.warning("Please enter some content to analyze")

st.divider()

# Main content
col_wl, col_bl = st.columns(2)

# Whitelist column
with col_wl:
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #2e7d32; margin-bottom: 1rem;'>Whitelist</h3>", unsafe_allow_html=True)
    
    # Search functionality for whitelist
    wl_search = st.text_input("Search whitelist...", key="wl_search")
    
    # Switch between single and bulk add modes
    wl_add_mode = st.radio(
        "Add mode:",
        ["Single Item", "Bulk Add"],
        horizontal=True,
        key="wl_add_mode"
    )
    
    if wl_add_mode == "Single Item":
        wl_input = st.text_input("Add to whitelist...", key="wl_input")
        if st.button("Add to Whitelist"):
            item = wl_input.strip()
            if item and item not in st.session_state.mode_data[st.session_state.current_mode]['whitelist']:
                st.session_state.mode_data[st.session_state.current_mode]['whitelist'].append(item)
                st.success(f"Added '{item}' to whitelist")
    else:  # Bulk Add mode
        wl_bulk_input = st.text_area(
            "Add multiple items (one per line)",
            height=100,
            key="wl_bulk_input"
        )
        if st.button("Add All to Whitelist"):
            items = [item.strip() for item in wl_bulk_input.split('\n') if item.strip()]
            added = 0
            for item in items:
                if item and item not in st.session_state.mode_data[st.session_state.current_mode]['whitelist']:
                    st.session_state.mode_data[st.session_state.current_mode]['whitelist'].append(item)
                    added += 1
            if added > 0:
                st.success(f"Added {added} items to whitelist")
            else:
                st.info("No new items to add")

    # Show whitelist items with filtering
    wl_items = st.session_state.mode_data[st.session_state.current_mode]['whitelist']
    
    # Filter the list based on search text
    if wl_search and wl_items:
        filtered_wl = [item for item in wl_items if wl_search.lower() in item.lower()]
    else:
        filtered_wl = wl_items
        
    if filtered_wl:
        selected_wl = st.multiselect(
            "Current whitelist items:",
            options=filtered_wl,
            default=filtered_wl,
            key="wl_select"
        )
        if len(selected_wl) < len(filtered_wl):
            removed = set(filtered_wl) - set(selected_wl)
            
            # Only remove items that are actually in the original list
            for item in removed:
                if item in st.session_state.mode_data[st.session_state.current_mode]['whitelist']:
                    st.session_state.mode_data[st.session_state.current_mode]['whitelist'].remove(item)
                    
            st.warning(f"Removed {', '.join(removed)} from whitelist")

# Blacklist column
with col_bl:
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #c62828; margin-bottom: 1rem;'>Blacklist</h3>", unsafe_allow_html=True)
    
    # Search functionality for blacklist
    bl_search = st.text_input("Search blacklist...", key="bl_search")
    
    # Switch between single and bulk add modes
    bl_add_mode = st.radio(
        "Add mode:",
        ["Single Item", "Bulk Add"],
        horizontal=True,
        key="bl_add_mode"
    )
    
    if bl_add_mode == "Single Item":
        bl_input = st.text_input("Add to blacklist...", key="bl_input")
        if st.button("Add to Blacklist"):
            item = bl_input.strip()
            if item and item not in st.session_state.mode_data[st.session_state.current_mode]['blacklist']:
                st.session_state.mode_data[st.session_state.current_mode]['blacklist'].append(item)
                st.success(f"Added '{item}' to blacklist")
    else:  # Bulk Add mode
        bl_bulk_input = st.text_area(
            "Add multiple items (one per line)",
            height=100,
            key="bl_bulk_input"
        )
        if st.button("Add All to Blacklist"):
            items = [item.strip() for item in bl_bulk_input.split('\n') if item.strip()]
            added = 0
            for item in items:
                if item and item not in st.session_state.mode_data[st.session_state.current_mode]['blacklist']:
                    st.session_state.mode_data[st.session_state.current_mode]['blacklist'].append(item)
                    added += 1
            if added > 0:
                st.success(f"Added {added} items to blacklist")
            else:
                st.info("No new items to add")

    # Show blacklist items with filtering
    bl_items = st.session_state.mode_data[st.session_state.current_mode]['blacklist']
    
    # Filter the list based on search text
    if bl_search and bl_items:
        filtered_bl = [item for item in bl_items if bl_search.lower() in item.lower()]
    else:
        filtered_bl = bl_items
        
    if filtered_bl:
        selected_bl = st.multiselect(
            "Current blacklist items:",
            options=filtered_bl,
            default=filtered_bl,
            key="bl_select"
        )
        if len(selected_bl) < len(filtered_bl):
            removed = set(filtered_bl) - set(selected_bl)
            
            # Only remove items that are actually in the original list
            for item in removed:
                if item in st.session_state.mode_data[st.session_state.current_mode]['blacklist']:
                    st.session_state.mode_data[st.session_state.current_mode]['blacklist'].remove(item)
                    
            st.warning(f"Removed {', '.join(removed)} from blacklist")

# Sidebar for additional features
with st.sidebar:
    st.markdown("<h2 style='font-size: 1.5rem; font-weight: 500; color: #1f1f1f; margin-bottom: 1.5rem;'>Tools</h2>", unsafe_allow_html=True)
    
    # Statistics with enhanced visualizations
    if st.button("Show Statistics", use_container_width=True):
        st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #1f1f1f; margin: 1rem 0;'>Statistics</h3>", unsafe_allow_html=True)
        whitelist = st.session_state.mode_data[st.session_state.current_mode]['whitelist']
        blacklist = st.session_state.mode_data[st.session_state.current_mode]['blacklist']
        
        # Summary tab with enhanced visual stats
        st.subheader("Summary Statistics")
        
        # Comparison chart for list sizes
        list_sizes = pd.DataFrame({
            'List': ['Whitelist', 'Blacklist'],
            'Count': [len(whitelist), len(blacklist)]
        })
        fig = px.bar(list_sizes, x='List', y='Count', color='List', 
                    color_discrete_map={'Whitelist': '#4CAF50', 'Blacklist': '#F44336'},
                    title='Number of Items per List')
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed stats tabs
        tab1, tab2 = st.tabs(["Whitelist Analysis", "Blacklist Analysis"])
        
        with tab1:
            st.markdown("**Whitelist Stats:**")
            st.write(f"Total items: {len(whitelist)}")
            
            if whitelist:
                avg_len = sum(len(x) for x in whitelist) / len(whitelist)
                min_item = min((len(x), x) for x in whitelist)[1] if whitelist else 'N/A'
                max_item = max((len(x), x) for x in whitelist)[1] if whitelist else 'N/A'
                
                st.write(f"Average length: {avg_len:.1f} characters")
                st.write(f"Shortest item: '{min_item}' ({len(min_item)} chars)")
                st.write(f"Longest item: '{max_item}' ({len(max_item)} chars)")
                
                # Length distribution
                lengths = [len(item) for item in whitelist]
                fig = px.histogram(x=lengths, nbins=20, title="Item Length Distribution",
                                labels={'x': 'Length (characters)', 'y': 'Count'},
                                color_discrete_sequence=['#4CAF50'])
                st.plotly_chart(fig, use_container_width=True)
                
                # First letter distribution
                if whitelist:
                    first_letters = [item[0].upper() if item else '' for item in whitelist]
                    letter_counts = Counter(first_letters)
                    letter_df = pd.DataFrame({
                        'Letter': list(letter_counts.keys()),
                        'Count': list(letter_counts.values())
                    }).sort_values('Letter')
                    
                    fig = px.bar(letter_df, x='Letter', y='Count', title="First Letter Distribution",
                                color_discrete_sequence=['#4CAF50'])
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("**Blacklist Stats:**")
            st.write(f"Total items: {len(blacklist)}")
            
            if blacklist:
                avg_len = sum(len(x) for x in blacklist) / len(blacklist)
                min_item = min((len(x), x) for x in blacklist)[1] if blacklist else 'N/A'
                max_item = max((len(x), x) for x in blacklist)[1] if blacklist else 'N/A'
                
                st.write(f"Average length: {avg_len:.1f} characters")
                st.write(f"Shortest item: '{min_item}' ({len(min_item)} chars)")
                st.write(f"Longest item: '{max_item}' ({len(max_item)} chars)")
                
                # Length distribution
                lengths = [len(item) for item in blacklist]
                fig = px.histogram(x=lengths, nbins=20, title="Item Length Distribution",
                                labels={'x': 'Length (characters)', 'y': 'Count'},
                                color_discrete_sequence=['#F44336'])
                st.plotly_chart(fig, use_container_width=True)
                
                # First letter distribution
                if blacklist:
                    first_letters = [item[0].upper() if item else '' for item in blacklist]
                    letter_counts = Counter(first_letters)
                    letter_df = pd.DataFrame({
                        'Letter': list(letter_counts.keys()),
                        'Count': list(letter_counts.values())
                    }).sort_values('Letter')
                    
                    fig = px.bar(letter_df, x='Letter', y='Count', title="First Letter Distribution",
                                color_discrete_sequence=['#F44336'])
                    st.plotly_chart(fig, use_container_width=True)

    # Bulk Actions section
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #1f1f1f; margin: 1.5rem 0 1rem;'>Bulk Actions</h3>", unsafe_allow_html=True)
    
    bulk_col1, bulk_col2 = st.columns(2)
    with bulk_col1:
        list_to_clear = st.selectbox("Select list", ["Whitelist", "Blacklist", "Both"])
    with bulk_col2:
        if st.button("Clear Selected List"):
            if list_to_clear == "Whitelist" or list_to_clear == "Both":
                st.session_state.mode_data[st.session_state.current_mode]['whitelist'] = []
            if list_to_clear == "Blacklist" or list_to_clear == "Both":
                st.session_state.mode_data[st.session_state.current_mode]['blacklist'] = []
            st.success(f"Cleared {list_to_clear.lower()}!")
    
    # Sorting section
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #1f1f1f; margin: 1.5rem 0 1rem;'>Sort Lists</h3>", unsafe_allow_html=True)
    
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        if st.button("Sort Ascending"):
            for list_type in ['whitelist', 'blacklist']:
                st.session_state.mode_data[st.session_state.current_mode][list_type].sort()
            st.success("Lists sorted in ascending order")
    
    with sort_col2:
        if st.button("Sort Descending"):
            for list_type in ['whitelist', 'blacklist']:
                st.session_state.mode_data[st.session_state.current_mode][list_type].sort(reverse=True)
            st.success("Lists sorted in descending order")

    # Save/Load Configuration
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 500; color: #1f1f1f; margin: 1.5rem 0 1rem;'>Configuration</h3>", unsafe_allow_html=True)
    
    # Save configuration
    save_col1, save_col2 = st.columns(2)
    with save_col1:
        config_filename = st.text_input("Config filename", "content_filter_config.json")
    with save_col2:
        if st.button("Save Config"):
            success, message = save_configuration(st.session_state.mode_data, config_filename)
            if success:
                st.success(message)
            else:
                st.error(message)
    
    # Load configuration
    load_col1, load_col2 = st.columns(2)
    
    with load_col1:
        uploaded_config = st.file_uploader("Upload config file", type=['json'])
    with load_col2:
        if st.button("Load Default Config"):
            success, result = load_configuration()
            if success:
                st.session_state.mode_data = result
                st.success("Default configuration loaded")
            else:
                st.error(result)
    
    if uploaded_config is not None:
        try:
            config_data = json.load(uploaded_config)
            st.session_state.mode_data = config_data
            st.success("Configuration loaded successfully")
        except Exception as e:
            st.error(f"Error loading configuration: {str(e)}")
    
    st.divider()
    
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

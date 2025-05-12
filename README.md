# Content Filter App

A collaborative content moderation tool built with Streamlit that enables teams to manage content filtering rules.

## CSCW Concepts

- **Collaborative Content Moderation**: Teams can work together to define and manage filtering rules
- **Group Awareness**: Real-time statistics and shared views of filtering rules
- **Access Control**: Different safety modes for various user contexts

## Features

- Multiple safety modes (Child Safe, High School Teen Safe, Custom)
- Collaborative whitelist/blacklist management
- Import/Export functionality for team sharing (CSV/TXT formats)
- Real-time statistics for group awareness
- Modern, responsive web interface

## User Groups

1. **Moderators**
   - Create and manage filtering rules
   - Define safety modes
   - Export/Import rule sets

2. **Content Creators**
   - Use filters to ensure content meets guidelines
   - View real-time statistics
   - Access appropriate safety modes

## Installation

```bash
# Clone the repository
git clone https://github.com/julian-carbajal/content-filter-app.git

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app locally
streamlit run streamlit_content_filter.py
```

## Deployment

This app can be deployed on Streamlit Cloud:

1. Push the code to GitHub
2. Visit https://share.streamlit.io/
3. Connect your GitHub account
4. Deploy the app

## Technologies

- Python 3.9+
- Streamlit 1.32.0
- Pandas 2.2.0

## License

MIT License 
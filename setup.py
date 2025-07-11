from setuptools import setup

setup(
    name="prime_tower",
    version="1.0",
    description="Prime Chain Solutions Control Tower Dashboard",
    long_description="Streamlit dashboard for fleet management and logistics analytics",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/prime_tower",
    packages=[],
    install_requires=[
        # Core Data & Math
        "numpy>=1.26.0",
        "pandas>=2.1.0",
        "scipy>=1.11.0",
        
        # Visualization
        "matplotlib>=3.8.0",
        "plotly>=5.18.0",
        "Pillow>=10.0.0",
        
        # Google Services
        "gspread>=6.0.0",
        "google-auth>=2.20.0",
        "oauth2client>=4.1.3",
        "google-generativeai>=0.3.0",
        
        # OpenAI
        "openai>=0.28.1",
        
        # Streamlit & Extensions
        "streamlit>=1.28.0",
        "streamlit-option-menu>=0.3.6",
        
        # Utilities
        "python-dateutil>=2.8.2",
        "requests>=2.31.0"
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Transportation Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    keywords="logistics fleet-management dashboard streamlit",
)

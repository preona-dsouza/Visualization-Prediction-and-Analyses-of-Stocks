# Stock Market Analysis, Visualisation and Prediction Dashboard

**Developed by Preona Dsouza**  
Copyright © 2026 Preona Dsouza. All rights reserved.

## About the Project

This project is a Python-based stock market dashboard that brings together stock analysis, data visualisation and prediction in one application.

It uses Python libraries and interactive dashboard frameworks to present stock-related information and analytical results through separate application modules.

## Project Modules

| File | Purpose |
|---|---|
| `start_dashboard.py` | Launches the dashboard applications |
| `visualize.py` | Stock data visualisation dashboard |
| `predict.py` | Stock prediction application |
| `Analysis.py` | Stock analysis application |
| `simulation_and_analysis.py` | Simulation and analysis application |
| `navbarpage.html` | Main landing page |
| `stockPred.ipynb` | Jupyter Notebook |

## Technologies Used

- Python
- Streamlit
- Dash
- TensorFlow and Keras
- NumPy and Pandas
- Scikit-learn
- XGBoost
- Prophet
- Plotly
- Matplotlib
- Yahoo Finance (`yfinance`)
- NewsAPI

## Requirements

- Windows
- Python 3.10
- Git (for cloning the repository)

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/preona-dsouza/Visualization-Prediction-and-Analyses-of-Stocks.git
```

### 2. Open the project directory

```bash
cd Visualization-Prediction-and-Analyses-of-Stocks
```

### 3. Create a virtual environment

```bash
py -3.10 -m venv .venv
```

### 4. Activate the virtual environment

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## API Configuration

The project uses a NewsAPI key in its news-related functionality.

Create the following file:

`.streamlit/secrets.toml`

Add your own API key:

```toml
NEWS_API_KEY = "your_newsapi_key"
```

Do not upload API keys, passwords or other credentials to GitHub.

## Running the Dashboard

After installing the dependencies and configuring the required settings, run:

```powershell
python start_dashboard.py
```

The launcher starts the applications and opens the main landing page in your browser.

### Local Application Addresses

| Application | Local address |
|---|---|
| Main landing page | http://127.0.0.1:8000/navbarpage.html |
| Visualisation | http://127.0.0.1:8050 |
| Prediction | http://127.0.0.1:8501 |
| Stock analysis | http://127.0.0.1:8502 |
| Simulation and analysis | http://127.0.0.1:8503 |

## Screenshots

Project screenshots are maintained in the `screenshoots` folder.

## Project Ownership

This project was developed by **Preona Dsouza**.

The original implementation, design and documentation are the author's work. Third-party libraries, frameworks and resources remain the property of their respective owners.

Copyright © 2026 Preona Dsouza. All rights reserved.

See [LICENSE](LICENSE) for the project's usage restrictions.

For authorship information, see [AUTHORS.md](AUTHORS.md).
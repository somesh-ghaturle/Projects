# 🏦 Agentic Finance Workflow

> **Enterprise-grade multi-agent financial analysis platform with professional web interface**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docke## 👨‍💻 Author & License

All code and content in this repository is for educational and personal use.

**Somesh Ramesh Ghaturle**  
MS in Data Science, Pace University

📧 **Email:** [someshghaturle@gmail.com](mailto:someshghaturle@gmail.com)  
🐙 **GitHub:** [https://github.com/somesh-ghaturle](https://github.com/somesh-ghaturle)  
💼 **LinkedIn:** [https://www.linkedin.com/in/someshghaturle/](https://www.linkedin.com/in/someshghaturle/)

### 📄 MIT License

```
MIT License

Copyright (c) 2025 Somesh Ramesh Ghaturle

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

**Agentic Finance Workflow** is a production-ready multi-agent system designed for comprehensive financial data analysis. The platform features three specialized AI agents working in harmony to provide data cleaning, risk analysis, and portfolio optimization capabilities through an intuitive web interface.

### ✨ Key Features

- **🤖 Multi-Agent Architecture**: Four specialized financial AI agents
- **🌐 Professional Web Interface**: Responsive UI with real-time analysis  
- **🐳 Docker Containerized**: Easy deployment with Docker support
- **⚡ FastAPI Backend**: High-performance REST API with automatic documentation
- **📊 Real Financial Calculations**: Professional-grade mathematical models
- **📈 Advanced Visualizations**: Interactive charts with Chart.js
- **🔮 Price Prediction Engine**: Multi-model ensemble forecasting with confidence intervals
- **💰 Comprehensive Stock Database**: 30+ stocks across multiple sectors

## 🏗️ Agent Architecture

### 🧹 Data Cleaner Agent

- **Purpose**: Data quality assurance and preprocessing
- **Capabilities**:
  - Data validation and cleaning
  - Missing value handling
  - Outlier detection and treatment
  - Quality score generation

### 📊 Risk Analysis Agent

- **Purpose**: Comprehensive risk assessment
- **Capabilities**:
  - Value at Risk (VaR) calculation
  - Volatility analysis using mathematical models
  - Beta calculation against market
  - Maximum drawdown analysis
  - Risk grade assignment

### 💼 Portfolio Optimizer Agent

- **Purpose**: Optimal asset allocation
- **Capabilities**:
  - Modern Portfolio Theory implementation
  - Efficient frontier generation
  - Weight optimization
  - Return/risk optimization

### 🔮 Price Prediction Agent

- **Purpose**: Advanced stock price forecasting
- **Capabilities**:
  - Multi-model ensemble predictions
  - Geometric Brownian Motion modeling
  - Mean reversion analysis
  - Momentum-based forecasting
  - Technical analysis integration
  - Trading signal generation
  - Confidence interval calculations

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd agentic-finance-workflow
```

### 2. Start the Application

**Option 1: One-Command Start (Recommended)**

```bash
# Start everything with one script
./start.sh
```

**Option 2: Manual Start**

```bash
# Start API server with Docker
docker-compose up -d

# Start web interface (in a new terminal)
python3 start_ui_server.py
```

**Option 3: Local Development**

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python app.py

# Run web interface (separate terminal)
python start_ui_server.py
```

### 3. Access the Application

- **🌐 Web Interface**: <http://localhost:3001/web_interface.html>
- **📚 API Documentation**: <http://localhost:8001/docs>
- **💚 Health Check**: <http://localhost:8001/health>

## 💻 Web Interface Features

### 🎛️ Professional Dashboard

- **📊 Stock Selection**: Dropdown with 30+ stocks across sectors (Tech, Healthcare, Finance, Energy)
- **🤖 Agent Controls**: Individual agent analysis or complete workflow
- **📈 Real-time Data**: Live market data fetching and analysis
- **🎨 Advanced Visualizations**: 4 interactive chart types powered by Chart.js

### 📋 Analysis Options

1. **🔍 Individual Agent Analysis**: Run specific agents (Data Cleaner, Risk Analyzer, Portfolio Optimizer, Price Predictor)
2. **⚡ Complete Workflow**: Execute all agents in sequence  
3. **📊 Get Market Data**: Fetch 30 days of OHLCV data for selected stock
4. **� Predict Price**: Generate 30-day price forecasts with confidence intervals
5. **�🗑️ Clear Results**: Reset interface for new analysis

### 📊 Visualization Types

1. **📈 Risk Analysis Charts**: VaR, volatility, and risk metrics
2. **💼 Portfolio Optimization**: Efficient frontier and allocation charts
3. **📊 Performance Metrics**: Returns, Sharpe ratio, and drawdown analysis
4. **🔗 Correlation Analysis**: Market correlation and beta visualization
5. **🔮 Price Predictions**: Future price forecasts with confidence bands
4. **🔗 Correlation Analysis**: Market correlation and beta visualization

## 🔧 API Endpoints

### Core Endpoints

```bash
# Individual agent analysis
POST /agent/{agent_name}
{
  "agent_name": "data_cleaner|risk_analyzer|portfolio_optimizer|price_predictor",
  "symbol": "AAPL",
  "data_type": "daily"
}

# Complete workflow
POST /workflow
{
  "workflow_type": "complete_analysis", 
  "data": {"symbol": "AAPL"}
}

# Price prediction (30-day forecast)
POST /predict/{symbol}

# Market data (30 days OHLCV)
GET /market-data/{symbol}

# Market data with predictions
GET /market-data/{symbol}?include_predictions=true

# Available agents
GET /agents

# Health check
GET /health
```

### 📊 Example Responses

**Portfolio Analysis:**
```json
{
  "portfolio_metrics": {
    "total_value": 145000,
    "sharpe_ratio": 1.2,
    "volatility": 0.16,
    "max_drawdown": -0.12
  },
  "asset_allocation": {
    "AAPL": 0.25,
    "GOOGL": 0.20,
    "MSFT": 0.15,
    "TSLA": 0.10
  }
}
```

**Price Prediction:**
```json
{
  "symbol": "AAPL",
  "current_price": 185.20,
  "predicted_price_30d": 192.45,
  "price_change_percentage": 3.91,
  "prediction_confidence": 84.5,
  "trading_signal": "BUY",
  "models_used": [
    "geometric_brownian_motion",
    "mean_reversion", 
    "momentum_analysis",
    "technical_analysis"
  ],
  "forecast_horizon": "30 days"
}
```

## 📁 Project Structure

```
agentic-finance-workflow/
├── app.py                      # Main FastAPI application with financial calculations
├── web_interface.html          # Professional web interface
├── start_ui_server.py          # Web server with CORS support
├── start.sh                    # One-command startup script
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation
```

## 🔄 Usage Examples

### Example 1: Complete Analysis

1. Open <http://localhost:3001/web_interface.html>
2. Select "TSLA" from the stock dropdown
3. Click "⚡ Run Complete Workflow"
4. View comprehensive analysis with:
   - Data quality scores
   - Risk metrics (VaR, volatility, beta)
   - Portfolio optimization results
   - Interactive visualizations

### Example 2: Risk Analysis Only

1. Select "AAPL" from dropdown
2. Click "🔍 Analyze with Agent"
3. View risk assessment including:
   - Value at Risk calculation
   - Volatility analysis
   - Maximum drawdown
   - Risk grade assignment

### Example 3: Market Data Exploration

1. Select any stock (e.g., "GOOGL")
2. Click "📊 Get Market Data"
3. Explore 30 days of:
   - OHLC price data
   - Volume information
   - Realistic price movements generated by Geometric Brownian Motion

## 🎯 Financial Calculations

### Real Mathematical Models

- **Geometric Brownian Motion**: For realistic price generation
- **Modern Portfolio Theory**: For portfolio optimization
- **Value at Risk (VaR)**: Using historical simulation method
- **Volatility Calculation**: Annualized standard deviation
- **Beta Calculation**: Against market benchmark
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Peak-to-trough loss analysis

### Stock Database

**Technology**: AAPL, GOOGL, MSFT, TSLA, NVDA, META, AMZN

**Healthcare**: JNJ, PFE, UNH, ABBV, MRK

**Finance**: JPM, BAC, WFC, GS, MS

**Energy**: XOM, CVX, COP, EOG

**And 10+ more across various sectors**

## 📈 Interactive Visualizations

The platform features Chart.js-powered interactive visualizations that automatically appear with every analysis:

### 🎯 Risk Analysis Charts

- **Doughnut Chart**: Risk distribution (Low/Medium/High Risk)
- **Interactive Legend**: Click to toggle risk categories
- **Real-time Updates**: Automatically updates with new analysis

### 💼 Portfolio Allocation Charts  

- **Pie Chart**: Optimal asset allocation weights
- **Dynamic Colors**: Each asset gets a unique color scheme
- **Hover Details**: See exact percentages and values

### 📊 Performance Metrics Charts

- **Bar Chart**: Volatility, Beta, Sharpe Ratio, Max Drawdown
- **Color-coded**: Red for risk, green for returns
- **Interactive Tooltips**: Detailed metric explanations

### 🔗 Correlation Matrix

- **Heat Map**: Stock correlation visualization
- **Market Beta**: Individual stock market correlation
- **Portfolio Diversification**: Visual assessment of portfolio balance

## 🛠️ Technical Details

### Backend Architecture

- **FastAPI**: Modern Python web framework with automatic OpenAPI documentation
- **Pydantic**: Data validation and serialization
- **Docker**: Containerized deployment for consistency
- **Mathematical Libraries**: NumPy, SciPy for financial calculations

### Frontend Technology

- **Vanilla JavaScript**: No heavy frameworks, fast loading
- **Chart.js**: Professional interactive charts
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live data fetching and display

### Financial Models

- **Geometric Brownian Motion**: `dS = μS dt + σS dW`
- **Portfolio Optimization**: Modern Portfolio Theory implementation
- **VaR Calculation**: Historical simulation with confidence intervals
- **Risk Metrics**: Professional-grade financial risk assessment

## 🔍 Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Kill processes on specific ports
lsof -ti:8001 | xargs kill -9  # API port
lsof -ti:3001 | xargs kill -9  # UI port
```

**Docker Issues**
```bash
# Rebuild containers
docker-compose down
docker-compose up --build -d
```

**Dependencies**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Health Checks

```bash
# Check API health
curl http://localhost:8001/health

# Check web interface
curl http://localhost:3001/web_interface.html
```

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

## � Deployment Suggestions

### Option 1: Streamlit Cloud (Recommended)
- Fork this repository to your GitHub account
- Sign up for free at [Streamlit Cloud](https://streamlit.io/cloud)
- Deploy the Streamlit version directly from GitHub
- Perfect for showcasing financial analysis capabilities

### Option 2: FastAPI Cloud Deployment
- **Heroku**: Deploy the FastAPI backend with web interface
- **Railway**: Modern platform for full-stack deployment
- **Render**: Free tier available for FastAPI applications
- **Vercel**: Deploy the web interface as a static frontend

### Option 3: Docker Cloud Hosting
- **AWS ECS**: Enterprise-grade container deployment
- **Google Cloud Run**: Serverless scaling with pay-per-use
- **DigitalOcean Apps**: Simple container deployment platform

## �👨‍💻 Author & License

All code and content in this repository is for educational and personal use.

**Somesh Ramesh Ghaturle**  
MS in Data Science, Pace University

📧 **Email:** [someshghaturle@gmail.com](mailto:someshghaturle@gmail.com)  
🐙 **GitHub:** [https://github.com/somesh-ghaturle](https://github.com/somesh-ghaturle)  
💼 **LinkedIn:** [https://www.linkedin.com/in/someshghaturle/](https://www.linkedin.com/in/someshghaturle/)

---

### Built with ❤️ for professional financial analysis

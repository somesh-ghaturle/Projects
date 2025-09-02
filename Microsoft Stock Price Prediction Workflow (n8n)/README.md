# 📈 Microsoft Stock Price Prediction Workflow (n8n)

AI-powered trading platform for real-time Microsoft (MSFT) stock price prediction and automated trading using n8n workflow automation, local Ollama AI, and professional email notifications.

---

## 🚀 Features
- Real-time MSFT stock data processing from Yahoo Finance API
- Local Ollama AI integration for intelligent trading analysis
- Professional email notifications with trading recommendations
- Complete Docker containerization with health monitoring
- Visual n8n workflow editor for easy customization
- BUY/SELL/HOLD signals with risk assessment and price predictions

**Tech Stack:** `n8n` `Ollama AI` `Docker` `PostgreSQL` `Redis` `Yahoo Finance API` `Email Automation`

---

## 🛠️ Quick Start

```bash
# 1. Clone the repository and navigate to the project
cd "Microsoft Stock Price Prediction Workflow (n8n)"

# 2. Run setup script
./setup.sh

# 3. Start the platform (production)
docker-compose -f docker-compose.production.yml up -d

# 4. Access n8n workflow editor
http://localhost:5678
```

---

## 📦 Project Structure
```
Microsoft Stock Price Prediction Workflow (n8n)/
├── README.md
├── Dockerfile
├── docker-compose.production.yml
├── requirements.txt
├── setup.sh
├── workflows/
│   └── msft_stock_prediction_workflow.json
```

---

## 📊 Example Workflow
- The sample workflow (in `workflows/msft_stock_prediction_workflow.json`) fetches MSFT stock data, runs analysis with Ollama AI, and sends email alerts.

---

## 📝 License
MIT

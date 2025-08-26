# Microsoft Stock Price Prediction Workflow (n8n)

This project contains an n8n workflow for generating algorithmic trading signals (BUY/SELL/HOLD) for Microsoft (MSFT) stock using simulated LSTM/GRU predictions. The workflow fetches historical stock data, simulates a prediction, generates a trading signal, and sends a notification to Discord.

---

## Features
- Automated daily execution (customizable schedule)
- Fetches MSFT historical prices from Yahoo Finance
- Simulates LSTM/GRU model predictions (can be replaced with a real model API)
- Generates trading signals based on predicted price movement
- Sends formatted notifications to a Discord channel

---

## Requirements
- [n8n](https://n8n.io/) (self-hosted or desktop)
- Python (for code nodes in n8n)
- Discord account and webhook (for notifications)
- Internet access (to fetch Yahoo Finance data)

---

## Setup & Execution Steps

1. **Install n8n:**
   - [n8n Installation Guide](https://docs.n8n.io/hosting/installation/)

2. **Start n8n:**
   ```sh
   n8n start
   ```
   Or use the desktop app.

3. **Import the Workflow:**
   - In the n8n UI, go to "Workflows" > "Import from File" and select `trading-workflow.json`.

4. **Configure Discord Webhook:**
   - Create a Discord webhook in your server/channel.
   - In n8n, add a new credential for the Discord Webhook and link it to the "Send Discord Notification" node.

5. **(Optional) Replace Simulated Model:**
   - For real predictions, replace the "Simulated Model API (LSTM/GRU)" code node with an HTTP Request node to your deployed model's API.

6. **Activate the Workflow:**
   - Enable the workflow in n8n to run on schedule, or trigger manually for testing.

---

## Customization
- **Ticker & Date Range:**
  - The "Set Ticker & Dates" node is set to MSFT and the last 100 days. Change as needed.
- **Trading Logic:**
  - The threshold for BUY/SELL is set to 2%. Adjust in the "Generate Trading Signal" node.
- **Notification:**
  - The Discord message is fully customizable in the notification node.

---

## License
For educational and personal use only.

---

*Somesh Ramesh Ghaturle*
*MS in Data Science, Pace University*

# Trading Strategy AI Analyzer API Documentation

## Overview
This API provides AI-powered analysis of trading strategies using Claude and a team of specialized AI agents. It can analyze MQL5 strategy code alongside CSV backtest results to provide comprehensive insights.

## Base URL
```
https://your-repl-name.repl.co/api
```

## Authentication
Currently, no authentication is required. The API uses the `ANTHROPIC_API_KEY` from environment variables.

## Endpoints

### 1. Analyze Strategy (Standard)
**POST** `/api/analyze`

Analyzes a trading strategy using Claude AI.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `mq5_file`: MQL5 strategy file (required)
  - `csv_file`: CSV backtest results file (required)
  - `strategy_name`: Strategy name (optional)
  - `include_similar`: Include similar strategies (optional, default: true)

**Response:**
```json
{
  "success": true,
  "strategy_name": "Strategy_Name",
  "report_path": "reports/report_Strategy_Name_20250731_164121.txt",
  "summary": "Brief analysis summary...",
  "analysis": {
    "overview": "...",
    "weaknesses": "...",
    "improvements": "...",
    "risk_management": "..."
  }
}
```

### 2. Comprehensive Team Analysis
**POST** `/api/analyze-comprehensive`

Performs comprehensive analysis using multiple AI agents (Risk Manager, Optimizer, Code Reviewer, etc.).

**Request:**
- Same as standard analysis, with additional:
  - `use_team_analysis`: Enable team analysis (optional, default: true)

**Response:**
```json
{
  "success": true,
  "strategy_name": "Strategy_Name",
  "report_path": "reports/comprehensive_analysis_Strategy_Name_20250731_164420.md",
  "team_analysis": {
    "risk_analysis": {...},
    "optimization": {...},
    "code_review": {...},
    "performance_analysis": {...},
    "market_research": {...}
  }
}
```

### 3. Validate CSV Structure
**POST** `/api/validate-csv`

Validates if a CSV file has the correct structure for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: CSV file to validate

**Response:**
```json
{
  "valid": true,
  "format": "mt5",
  "message": "CSV structure is valid",
  "columns": ["Time", "Symbol", "Type", "Volume", "Price", ...]
}
```

### 4. List Reports
**GET** `/api/reports`

Lists all generated analysis reports.

**Response:**
```json
{
  "reports": [
    {
      "filename": "report_Strategy_Name_20250731_164121.txt",
      "size": "4.1KB",
      "modified": "2025-07-31T16:41:21"
    }
  ]
}
```

### 5. Get Report Content
**GET** `/api/reports/{filename}`

Retrieves the content of a specific report.

**Response:**
- Content-Type: `text/plain` or `text/markdown`
- Body: Report content

### 6. List Strategies
**GET** `/api/strategies`

Lists all stored strategies in the vector database.

**Response:**
```json
{
  "strategies": [
    {
      "name": "Strategy_Name",
      "metadata": {...}
    }
  ]
}
```

### 7. Get Strategy Statistics
**GET** `/api/stats`

Retrieves statistics about stored strategies.

**Response:**
```json
{
  "total_strategies": 10,
  "average_performance": {...},
  "common_patterns": [...]
}
```

## Error Responses
All endpoints may return error responses in the following format:

```json
{
  "detail": "Error description"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 422: Unprocessable Entity (validation error)
- 500: Internal Server Error

## Example Usage

### Python
```python
import requests

# Analyze a strategy
with open('strategy.mq5', 'rb') as mq5, open('backtest.csv', 'rb') as csv:
    files = {
        'mq5_file': ('strategy.mq5', mq5, 'text/plain'),
        'csv_file': ('backtest.csv', csv, 'text/csv')
    }
    data = {
        'strategy_name': 'MyStrategy',
        'include_similar': 'true'
    }
    
    response = requests.post('https://your-repl.repl.co/api/analyze', files=files, data=data)
    result = response.json()
    print(result['summary'])
```

### cURL
```bash
curl -X POST https://your-repl.repl.co/api/analyze \
  -F "mq5_file=@strategy.mq5" \
  -F "csv_file=@backtest.csv" \
  -F "strategy_name=MyStrategy"
```

## CSV File Format
The API supports two CSV formats:

### Standard Format
```csv
Timestamp,Action,Symbol,Price,PnL
2024-01-01 10:00:00,BUY,EURUSD,1.0950,0.00
2024-01-01 11:00:00,SELL,EURUSD,1.0960,10.00
```

### MT5 Format
```csv
Time,Symbol,Type,Volume,Price,OpenPrice,ClosePrice,SL,TP,Profit,Balance,Equity,Comment
2024-01-01 00:00:00,EURUSD,deposit,0.00,0.0000,0.0000,0.0000,0.0000,0.0000,0.00,100000.00,100000.00,Initial deposit
```

## Environment Variables
Required environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude access
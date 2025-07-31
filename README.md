# Trading Strategy AI Analyzer API

A powerful API service that uses Claude AI and specialized agent teams to analyze trading strategies.

## Features

- **AI-Powered Analysis**: Uses Claude 3.5 Sonnet for intelligent strategy analysis
- **Team Agent System**: Multiple specialized AI agents for comprehensive analysis
  - Risk Manager Agent
  - Strategy Optimizer Agent  
  - Code Reviewer Agent
  - Performance Analyst Agent
  - Market Researcher Agent
- **Multi-Format Support**: Handles both standard and MT5 CSV formats
- **Vector Database**: Stores and compares strategies using ChromaDB
- **RESTful API**: Easy integration with any platform

## Quick Start on Replit

1. Fork this repl
2. Add your Anthropic API key as a secret:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your API key from [Anthropic Console](https://console.anthropic.com/)
3. Click "Run" to start the API server

## API Endpoints

- `POST /api/analyze` - Standard strategy analysis
- `POST /api/analyze-comprehensive` - Comprehensive team analysis
- `POST /api/validate-csv` - Validate CSV file format
- `GET /api/reports` - List all reports
- `GET /api/reports/{filename}` - Get specific report
- `GET /api/strategies` - List stored strategies
- `GET /api/stats` - Get strategy statistics

See [API_DOCS.md](API_DOCS.md) for detailed documentation.

## Example Usage

```python
import requests

# Analyze a strategy
with open('strategy.mq5', 'rb') as mq5, open('backtest.csv', 'rb') as csv:
    files = {
        'mq5_file': mq5,
        'csv_file': csv
    }
    response = requests.post('https://your-repl.repl.co/api/analyze', files=files)
    print(response.json()['summary'])
```

## Environment Variables

- `ANTHROPIC_API_KEY`: Required - Your Anthropic API key

## Tech Stack

- **FastAPI**: Modern web framework
- **Anthropic Claude**: AI analysis engine
- **ChromaDB**: Vector database for strategy storage
- **Pandas**: Data processing
- **Python 3.11**: Runtime

## License

MIT License - See LICENSE file for details
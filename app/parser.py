import re
import pandas as pd
from typing import Dict, List, Tuple, Optional
import os

class MQL5Parser:
    """Parser for MQL5 trading strategy code"""
    
    def __init__(self):
        self.keywords = [
            'OnTick', 'OnInit', 'OnDeinit', 'OrderSend', 'OrderModify', 'OrderClose',
            'iMA', 'iRSI', 'iMACD', 'iStochastic', 'iBands', 'iATR', 'iCCI',
            'Buy', 'Sell', 'StopLoss', 'TakeProfit', 'LotSize', 'MagicNumber'
        ]
    
    def parse_mq5_file(self, file_path: str) -> Dict:
        """Parse MQL5 file and extract key components"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extract strategy name
            strategy_name = self._extract_strategy_name(content)
            
            # Extract key functions
            functions = self._extract_functions(content)
            
            # Extract trading logic
            trading_logic = self._extract_trading_logic(content)
            
            # Extract parameters
            parameters = self._extract_parameters(content)
            
            # Extract indicators used
            indicators = self._extract_indicators(content)
            
            return {
                'strategy_name': strategy_name,
                'functions': functions,
                'trading_logic': trading_logic,
                'parameters': parameters,
                'indicators': indicators,
                'raw_content': content[:5000]  # Truncate for safety
            }
        except Exception as e:
            return {
                'error': f"Failed to parse MQL5 file: {str(e)}",
                'strategy_name': 'Unknown',
                'functions': [],
                'trading_logic': '',
                'parameters': [],
                'indicators': [],
                'raw_content': ''
            }
    
    def _extract_strategy_name(self, content: str) -> str:
        """Extract strategy name from MQL5 code"""
        # Look for common patterns
        patterns = [
            r'string\s+StrategyName\s*=\s*["\']([^"\']+)["\']',
            r'//\s*Strategy:\s*([^\n]+)',
            r'#property\s+description\s*["\']([^"\']+)["\']',
            r'//\|\s*([A-Za-z0-9_\s]+)\.mq5',  # MT5 header format
            r'//\|\s*([A-Za-z0-9_\s]+)\s*-\s*[A-Za-z0-9_\s]+',  # Enhanced MT5 format
            r'//\s*([A-Za-z0-9_\s]+)\.mq5\s*-\s*[A-Za-z0-9_\s]+'  # File header
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if name and name != "Unknown":
                    return name
        
        # Look for specific patterns in the content
        if "VolumeBreakout" in content:
            return "VolumeBreakoutEA"
        elif "Claude_MTX" in content:
            return "Claude_MTX_Strategy"
        
        # Fallback: use filename or default
        return "Trading_Strategy"
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function definitions"""
        functions = []
        function_pattern = r'(\w+)\s+(\w+)\s*\([^)]*\)\s*\{'
        matches = re.findall(function_pattern, content)
        
        for return_type, func_name in matches:
            if func_name in self.keywords or func_name.startswith('On'):
                functions.append(f"{return_type} {func_name}()")
        
        return functions
    
    def _extract_trading_logic(self, content: str) -> str:
        """Extract trading logic from OnTick function"""
        on_tick_pattern = r'void\s+OnTick\s*\(\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
        match = re.search(on_tick_pattern, content, re.DOTALL)
        
        if match:
            logic = match.group(1)
            # Clean up the logic
            logic = re.sub(r'//.*?\n', '\n', logic)  # Remove comments
            logic = re.sub(r'\s+', ' ', logic)  # Normalize whitespace
            return logic.strip()[:1000]  # Truncate for safety
        
        return "Trading logic not found"
    
    def _extract_parameters(self, content: str) -> List[str]:
        """Extract input parameters"""
        params = []
        param_pattern = r'input\s+(\w+)\s+(\w+)\s*=\s*([^;]+);'
        matches = re.findall(param_pattern, content)
        
        for param_type, param_name, default_value in matches:
            params.append(f"{param_type} {param_name} = {default_value.strip()}")
        
        return params
    
    def _extract_indicators(self, content: str) -> List[str]:
        """Extract indicators used in the strategy"""
        indicators = []
        indicator_patterns = [
            r'iMA\s*\(',
            r'iRSI\s*\(',
            r'iMACD\s*\(',
            r'iStochastic\s*\(',
            r'iBands\s*\(',
            r'iATR\s*\(',
            r'iCCI\s*\('
        ]
        
        for pattern in indicator_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                indicator_name = pattern.replace(r'\s*\(', '').replace('\\', '')
                indicators.append(indicator_name)
        
        return list(set(indicators))  # Remove duplicates


class CSVBacktestParser:
    """Parser for CSV backtest results"""
    
    def __init__(self):
        self.required_columns = ['Timestamp', 'Action', 'Symbol', 'Price', 'PnL']
    
    def parse_csv_file(self, file_path: str) -> Dict:
        """Parse CSV backtest file and compute statistics"""
        try:
            # Read CSV with comment lines
            df = pd.read_csv(file_path, comment='#')
            
            # Store file path for later use
            df._metadata = {'file_path': file_path}
            
            # Check for different column formats
            if 'Time' in df.columns and 'Type' in df.columns:
                # MT5 format: Time,Symbol,Type,Volume,Price,OpenPrice,ClosePrice,SL,TP,Profit,Balance,Equity,Comment
                return self._parse_mt5_format(df)
            elif 'Timestamp' in df.columns and 'Action' in df.columns:
                # Standard format: Timestamp,Action,Symbol,Price,PnL
                return self._parse_standard_format(df)
            else:
                return {
                    'error': f'Unknown CSV format. Available columns: {list(df.columns)}',
                    'stats': {},
                    'trades': []
                }
            
        except Exception as e:
            return {
                'error': f"Failed to parse CSV file: {str(e)}",
                'stats': {},
                'trades': []
            }
    
    def _parse_mt5_format(self, df: pd.DataFrame) -> Dict:
        """Parse MT5-style CSV format"""
        try:
            # Filter only trade entries (buy/sell/close) - exclude deposit and summary
            trade_df = df[df['Type'].isin(['buy', 'sell', 'close'])]
            
            if trade_df.empty:
                return {
                    'stats': {
                        'total_trades': 0,
                        'win_rate': 0,
                        'total_pnl': 0,
                        'average_pnl': 0,
                        'max_profit': 0,
                        'max_loss': 0,
                        'winning_trades': 0,
                        'losing_trades': 0
                    },
                    'trades': [],
                    'total_trades': 0,
                    'columns': list(df.columns)
                }
            
            # Extract backtest configuration from comments
            config = self._extract_backtest_config(df)
            
            # Compute statistics
            stats = self._compute_mt5_statistics(trade_df, config)
            
            # Get recent trades
            recent_trades = self._get_mt5_recent_trades(trade_df)
            
            return {
                'stats': stats,
                'trades': recent_trades,
                'total_trades': len(trade_df),
                'columns': list(df.columns),
                'config': config
            }
            
        except Exception as e:
            return {
                'error': f'Error parsing MT5 CSV: {str(e)}',
                'stats': {},
                'trades': []
            }
    
    def _parse_standard_format(self, df: pd.DataFrame) -> Dict:
        """Parse standard CSV format"""
        try:
            # Validate required columns
            missing_cols = [col for col in self.required_columns if col not in df.columns]
            if missing_cols:
                return {
                    'error': f"Missing required columns: {missing_cols}",
                    'stats': {},
                    'trades': []
                }
            
            # Compute statistics
            stats = self._compute_statistics(df)
            
            # Get recent trades
            recent_trades = self._get_recent_trades(df)
            
            return {
                'stats': stats,
                'trades': recent_trades,
                'total_trades': len(df),
                'columns': list(df.columns)
            }
        except Exception as e:
            return {
                'error': f"Failed to parse CSV file: {str(e)}",
                'stats': {},
                'trades': []
            }
    
    def _compute_statistics(self, df: pd.DataFrame) -> Dict:
        """Compute trading statistics"""
        stats = {}
        
        # Basic stats
        stats['total_trades'] = len(df)
        stats['buy_trades'] = len(df[df['Action'].str.contains('Buy', case=False, na=False)])
        stats['sell_trades'] = len(df[df['Action'].str.contains('Sell', case=False, na=False)])
        
        # PnL analysis
        if 'PnL' in df.columns:
            pnl_series = pd.to_numeric(df['PnL'], errors='coerce').dropna()
            stats['total_pnl'] = pnl_series.sum()
            stats['average_pnl'] = pnl_series.mean()
            stats['max_profit'] = pnl_series.max()
            stats['max_loss'] = pnl_series.min()
            stats['winning_trades'] = len(pnl_series[pnl_series > 0])
            stats['losing_trades'] = len(pnl_series[pnl_series < 0])
            stats['win_rate'] = (stats['winning_trades'] / len(pnl_series) * 100) if len(pnl_series) > 0 else 0
        
        # Symbol analysis
        if 'Symbol' in df.columns:
            stats['unique_symbols'] = df['Symbol'].nunique()
            stats['most_traded_symbol'] = df['Symbol'].mode().iloc[0] if len(df['Symbol'].mode()) > 0 else 'Unknown'
        
        # Time analysis
        if 'Timestamp' in df.columns:
            try:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                stats['trading_period'] = {
                    'start': df['Timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
                    'end': df['Timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
                }
            except:
                stats['trading_period'] = {'start': 'Unknown', 'end': 'Unknown'}
        
        return stats
    
    def _get_recent_trades(self, df: pd.DataFrame, limit: int = 10) -> List[Dict]:
        """Get recent trades for analysis"""
        recent_df = df.tail(limit)
        trades = []
        
        for _, row in recent_df.iterrows():
            trade = {
                'timestamp': str(row.get('Timestamp', 'Unknown')),
                'action': str(row.get('Action', 'Unknown')),
                'symbol': str(row.get('Symbol', 'Unknown')),
                'price': str(row.get('Price', 'Unknown')),
                'pnl': str(row.get('PnL', 'Unknown'))
            }
            trades.append(trade)
        
        return trades
    
    def _extract_backtest_config(self, df: pd.DataFrame) -> Dict:
        """Extract backtest configuration from the CSV file"""
        config = {}
        
        # Read the original file to get comments
        try:
            with open(df._metadata.get('file_path', ''), 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    if 'Expert Advisor:' in line:
                        config['expert_advisor'] = line.split('Expert Advisor:')[1].strip()
                    elif 'Symbol:' in line:
                        config['symbol'] = line.split('Symbol:')[1].strip()
                    elif 'Timeframe:' in line:
                        config['timeframe'] = line.split('Timeframe:')[1].strip()
                    elif 'Period:' in line:
                        config['period'] = line.split('Period:')[1].strip()
                    elif 'Initial Deposit:' in line:
                        config['initial_deposit'] = line.split('Initial Deposit:')[1].strip()
                    elif 'Leverage:' in line:
                        config['leverage'] = line.split('Leverage:')[1].strip()
                    elif 'Total Trades:' in line:
                        config['total_trades'] = line.split('Total Trades:')[1].strip()
                    elif 'Win Rate:' in line:
                        config['win_rate'] = line.split('Win Rate:')[1].strip()
                    elif 'Net Profit:' in line:
                        config['net_profit'] = line.split('Net Profit:')[1].strip()
                    elif 'Final Balance:' in line:
                        config['final_balance'] = line.split('Final Balance:')[1].strip()
                    elif 'Max Drawdown:' in line:
                        config['max_drawdown'] = line.split('Max Drawdown:')[1].strip()
                    elif 'Sharpe Ratio:' in line:
                        config['sharpe_ratio'] = line.split('Sharpe Ratio:')[1].strip()
        except:
            pass
        
        return config

    def _compute_mt5_statistics(self, df: pd.DataFrame, config: Dict = None) -> Dict:
        """Compute trading statistics for MT5 format"""
        stats = {}
        
        # Basic stats
        stats['total_trades'] = len(df)
        stats['buy_trades'] = len(df[df['Type'].str.contains('buy', case=False, na=False)])
        stats['sell_trades'] = len(df[df['Type'].str.contains('sell', case=False, na=False)])
        stats['close_trades'] = len(df[df['Type'].str.contains('close', case=False, na=False)])
        
        # Use config data if available
        if config:
            stats['expert_advisor'] = config.get('expert_advisor', 'Unknown')
            stats['symbol'] = config.get('symbol', 'Unknown')
            stats['timeframe'] = config.get('timeframe', 'Unknown')
            stats['period'] = config.get('period', 'Unknown')
            stats['initial_deposit'] = config.get('initial_deposit', 'Unknown')
            stats['leverage'] = config.get('leverage', 'Unknown')
            stats['config_total_trades'] = config.get('total_trades', 'Unknown')
            stats['config_win_rate'] = config.get('win_rate', 'Unknown')
            stats['config_net_profit'] = config.get('net_profit', 'Unknown')
            stats['config_final_balance'] = config.get('final_balance', 'Unknown')
            stats['config_max_drawdown'] = config.get('max_drawdown', 'Unknown')
            stats['config_sharpe_ratio'] = config.get('sharpe_ratio', 'Unknown')
        
        # Profit analysis from actual trade data
        if 'Profit' in df.columns:
            profit_series = pd.to_numeric(df['Profit'], errors='coerce').dropna()
            if len(profit_series) > 0:
                stats['total_pnl'] = profit_series.sum()
                stats['average_pnl'] = profit_series.mean()
                stats['max_profit'] = profit_series.max()
                stats['max_loss'] = profit_series.min()
                stats['winning_trades'] = len(profit_series[profit_series > 0])
                stats['losing_trades'] = len(profit_series[profit_series < 0])
                stats['win_rate'] = (stats['winning_trades'] / len(profit_series) * 100) if len(profit_series) > 0 else 0
            else:
                # If no profit data in trades, use config data
                stats['total_pnl'] = 0
                stats['average_pnl'] = 0
                stats['max_profit'] = 0
                stats['max_loss'] = 0
                stats['winning_trades'] = 0
                stats['losing_trades'] = 0
                stats['win_rate'] = 0
        
        # Symbol analysis
        if 'Symbol' in df.columns:
            stats['unique_symbols'] = df['Symbol'].nunique()
            stats['most_traded_symbol'] = df['Symbol'].mode().iloc[0] if len(df['Symbol'].mode()) > 0 else 'Unknown'
        
        # Time analysis
        if 'Time' in df.columns:
            try:
                df['Time'] = pd.to_datetime(df['Time'])
                stats['trading_period'] = {
                    'start': df['Time'].min().strftime('%Y-%m-%d %H:%M:%S'),
                    'end': df['Time'].max().strftime('%Y-%m-%d %H:%M:%S')
                }
            except:
                stats['trading_period'] = {'start': 'Unknown', 'end': 'Unknown'}
        
        return stats
    
    def _get_mt5_recent_trades(self, df: pd.DataFrame, limit: int = 10) -> List[Dict]:
        """Get recent trades for MT5 format"""
        recent_df = df.tail(limit)
        trades = []
        
        for _, row in recent_df.iterrows():
            trade = {
                'timestamp': str(row.get('Time', 'Unknown')),
                'action': str(row.get('Type', 'Unknown')),
                'symbol': str(row.get('Symbol', 'Unknown')),
                'price': str(row.get('Price', 'Unknown')),
                'pnl': str(row.get('Profit', 'Unknown'))
            }
            trades.append(trade)
        
        return trades


def create_summary(mq5_data: Dict, csv_data: Dict) -> str:
    """Create a comprehensive summary for Claude analysis"""
    summary = "=== TRADING STRATEGY ANALYSIS SUMMARY ===\n\n"
    
    # MQL5 Strategy Information
    summary += "STRATEGY CODE ANALYSIS:\n"
    summary += f"Strategy Name: {mq5_data.get('strategy_name', 'Unknown')}\n"
    summary += f"Functions Found: {', '.join(mq5_data.get('functions', []))}\n"
    summary += f"Indicators Used: {', '.join(mq5_data.get('indicators', []))}\n"
    summary += f"Parameters: {', '.join(mq5_data.get('parameters', []))}\n"
    summary += f"Trading Logic: {mq5_data.get('trading_logic', 'Not found')}\n\n"
    
    # Backtest Configuration
    config = csv_data.get('config', {})
    if config:
        summary += "BACKTEST CONFIGURATION:\n"
        summary += f"Expert Advisor: {config.get('expert_advisor', 'Unknown')}\n"
        summary += f"Symbol: {config.get('symbol', 'Unknown')}\n"
        summary += f"Timeframe: {config.get('timeframe', 'Unknown')}\n"
        summary += f"Period: {config.get('period', 'Unknown')}\n"
        summary += f"Initial Deposit: {config.get('initial_deposit', 'Unknown')}\n"
        summary += f"Leverage: {config.get('leverage', 'Unknown')}\n\n"
    
    # Backtest Results
    summary += "BACKTEST RESULTS:\n"
    stats = csv_data.get('stats', {})
    
    # Use config data if available, otherwise use computed stats
    if config:
        summary += f"Total Trades: {config.get('total_trades', stats.get('total_trades', 0))}\n"
        win_rate = config.get('win_rate', f"{stats.get('win_rate', 0):.2f}%")
        summary += f"Win Rate: {win_rate}\n"
        net_profit = config.get('net_profit', f"{stats.get('total_pnl', 0):.2f}")
        summary += f"Net Profit: {net_profit}\n"
        summary += f"Final Balance: {config.get('final_balance', 'Unknown')}\n"
        summary += f"Max Drawdown: {config.get('max_drawdown', 'Unknown')}\n"
        summary += f"Sharpe Ratio: {config.get('sharpe_ratio', 'Unknown')}\n"
    else:
        summary += f"Total Trades: {stats.get('total_trades', 0)}\n"
        summary += f"Win Rate: {stats.get('win_rate', 0):.2f}%\n"
        summary += f"Total PnL: {stats.get('total_pnl', 0):.2f}\n"
        summary += f"Average PnL: {stats.get('average_pnl', 0):.2f}\n"
        summary += f"Winning Trades: {stats.get('winning_trades', 0)}\n"
        summary += f"Losing Trades: {stats.get('losing_trades', 0)}\n"
        summary += f"Max Profit: {stats.get('max_profit', 0):.2f}\n"
        summary += f"Max Loss: {stats.get('max_loss', 0):.2f}\n"
    
    if 'trading_period' in stats:
        period = stats['trading_period']
        summary += f"Trading Period: {period.get('start', 'Unknown')} to {period.get('end', 'Unknown')}\n"
    
    summary += f"Symbols Traded: {stats.get('unique_symbols', 0)}\n"
    summary += f"Most Traded Symbol: {stats.get('most_traded_symbol', 'Unknown')}\n\n"
    
    # Recent Trades
    summary += "RECENT TRADES (Last 5):\n"
    recent_trades = csv_data.get('trades', [])[:5]
    for i, trade in enumerate(recent_trades, 1):
        summary += f"{i}. {trade.get('timestamp', 'Unknown')} - {trade.get('action', 'Unknown')} {trade.get('symbol', 'Unknown')} @ {trade.get('price', 'Unknown')} (PnL: {trade.get('pnl', 'Unknown')})\n"
    
    return summary 
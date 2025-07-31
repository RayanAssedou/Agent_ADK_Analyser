import os
import anthropic
from typing import Dict, List, Optional
from datetime import datetime
import json

class ClaudeAgent:
    """Claude AI agent for trading strategy analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Using Claude 3.5 Sonnet
    
    def analyze_strategy(self, mq5_data: Dict, csv_data: Dict, summary: str, 
                        similar_strategies: List[Dict] = None) -> Dict:
        """Analyze trading strategy using Claude"""
        try:
            # Create comprehensive prompt
            prompt = self._create_analysis_prompt(mq5_data, csv_data, summary, similar_strategies)
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            claude_response = response.content[0].text
            
            # Parse and structure the response
            structured_response = self._parse_claude_response(claude_response)
            
            return {
                'success': True,
                'analysis': structured_response,
                'raw_response': claude_response,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis': {},
                'raw_response': '',
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
    
    def _create_analysis_prompt(self, mq5_data: Dict, csv_data: Dict, summary: str, 
                               similar_strategies: List[Dict] = None) -> str:
        """Create a comprehensive prompt for Claude analysis"""
        
        prompt = """You are an expert trading strategy analyst with deep knowledge of MQL5, MetaTrader 5, and algorithmic trading. 

Your task is to analyze a trading strategy based on its MQL5 code and backtest results, then provide actionable improvement suggestions.

ANALYSIS REQUIREMENTS:
1. Identify weaknesses in the current strategy logic
2. Suggest specific improvements with code examples
3. Recommend parameter optimizations
4. Provide risk management enhancements
5. Suggest additional indicators or filters if beneficial
6. Give MQL5 code snippets for improvements

Please structure your response in the following format:

## STRATEGY OVERVIEW
[Brief summary of what the strategy does]

## WEAKNESSES IDENTIFIED
[List specific weaknesses found in the code and results]

## IMPROVEMENT RECOMMENDATIONS
[Detailed improvement suggestions with specific code examples]

## RISK MANAGEMENT ENHANCEMENTS
[Specific risk management improvements]

## CODE IMPROVEMENTS
[Actual MQL5 code snippets for improvements]

## PARAMETER OPTIMIZATION
[Suggested parameter changes with reasoning]

## SIMILAR STRATEGIES INSIGHTS
[If similar strategies are provided, include insights from them]

---

STRATEGY DATA TO ANALYZE:

"""
        
        # Add strategy summary
        prompt += f"STRATEGY SUMMARY:\n{summary}\n\n"
        
        # Add MQL5 code details
        prompt += "MQL5 CODE ANALYSIS:\n"
        prompt += f"Strategy Name: {mq5_data.get('strategy_name', 'Unknown')}\n"
        prompt += f"Functions: {', '.join(mq5_data.get('functions', []))}\n"
        prompt += f"Indicators Used: {', '.join(mq5_data.get('indicators', []))}\n"
        prompt += f"Parameters: {', '.join(mq5_data.get('parameters', []))}\n"
        prompt += f"Trading Logic: {mq5_data.get('trading_logic', 'Not found')}\n\n"
        
        # Add backtest results
        prompt += "BACKTEST RESULTS:\n"
        stats = csv_data.get('stats', {})
        prompt += f"Total Trades: {stats.get('total_trades', 0)}\n"
        prompt += f"Win Rate: {stats.get('win_rate', 0):.2f}%\n"
        prompt += f"Total PnL: {stats.get('total_pnl', 0):.2f}\n"
        prompt += f"Average PnL: {stats.get('average_pnl', 0):.2f}\n"
        prompt += f"Max Profit: {stats.get('max_profit', 0):.2f}\n"
        prompt += f"Max Loss: {stats.get('max_loss', 0):.2f}\n\n"
        
        # Add similar strategies if available
        if similar_strategies:
            prompt += "SIMILAR STRATEGIES FOR REFERENCE:\n"
            for i, strategy in enumerate(similar_strategies[:3], 1):
                metadata = strategy.get('metadata', {})
                prompt += f"{i}. {metadata.get('strategy_name', 'Unknown')} "
                prompt += f"(Win Rate: {metadata.get('win_rate', 0):.2f}%, "
                prompt += f"Total PnL: {metadata.get('total_pnl', 0):.2f})\n"
            prompt += "\n"
        
        prompt += """Please provide a comprehensive analysis focusing on practical improvements that can be implemented in MQL5 code. Be specific with code examples and parameter suggestions."""
        
        return prompt
    
    def _parse_claude_response(self, response: str) -> Dict:
        """Parse Claude's response into structured format"""
        try:
            # Try to extract sections from the response
            sections = {
                'overview': '',
                'weaknesses': '',
                'improvements': '',
                'risk_management': '',
                'code_improvements': '',
                'parameter_optimization': '',
                'similar_insights': ''
            }
            
            # Simple parsing based on headers
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('## STRATEGY OVERVIEW'):
                    current_section = 'overview'
                elif line.startswith('## WEAKNESSES IDENTIFIED'):
                    current_section = 'weaknesses'
                elif line.startswith('## IMPROVEMENT RECOMMENDATIONS'):
                    current_section = 'improvements'
                elif line.startswith('## RISK MANAGEMENT ENHANCEMENTS'):
                    current_section = 'risk_management'
                elif line.startswith('## CODE IMPROVEMENTS'):
                    current_section = 'code_improvements'
                elif line.startswith('## PARAMETER OPTIMIZATION'):
                    current_section = 'parameter_optimization'
                elif line.startswith('## SIMILAR STRATEGIES INSIGHTS'):
                    current_section = 'similar_insights'
                elif current_section and line:
                    sections[current_section] += line + '\n'
            
            return sections
            
        except Exception as e:
            # If parsing fails, return the raw response
            return {
                'raw_response': response,
                'parsing_error': str(e)
            }
    
    def generate_report_filename(self, strategy_name: str) -> str:
        """Generate filename for the analysis report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c for c in strategy_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        return f"report_{safe_name}_{timestamp}.txt"
    
    def save_analysis_report(self, analysis_result: Dict, strategy_name: str, 
                           reports_dir: str = "reports") -> str:
        """Save analysis report to file"""
        try:
            # Create reports directory if it doesn't exist
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate filename
            filename = self.generate_report_filename(strategy_name)
            filepath = os.path.join(reports_dir, filename)
            
            # Prepare report content
            report_content = f"""TRADING STRATEGY ANALYSIS REPORT
Generated: {analysis_result.get('timestamp', 'Unknown')}
Strategy: {strategy_name}
Model: {analysis_result.get('model_used', 'Unknown')}

{'='*50}

"""
            
            # Add structured analysis
            analysis = analysis_result.get('analysis', {})
            if isinstance(analysis, dict):
                for section, content in analysis.items():
                    if content and section != 'raw_response':
                        report_content += f"\n{section.upper().replace('_', ' ')}:\n"
                        report_content += f"{'='*30}\n"
                        report_content += content + "\n"
            else:
                report_content += analysis_result.get('raw_response', 'No analysis available')
            
            # Add metadata
            report_content += f"\n\n{'='*50}\n"
            report_content += f"Report generated by Claude AI Agent\n"
            report_content += f"Timestamp: {analysis_result.get('timestamp', 'Unknown')}\n"
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return filepath
            
        except Exception as e:
            print(f"Failed to save report: {str(e)}")
            return ""
    
    def get_analysis_summary(self, analysis_result: Dict) -> str:
        """Extract a brief summary from the analysis"""
        try:
            analysis = analysis_result.get('analysis', {})
            if isinstance(analysis, dict) and 'overview' in analysis:
                return analysis['overview'][:200] + "..." if len(analysis['overview']) > 200 else analysis['overview']
            else:
                raw_response = analysis_result.get('raw_response', '')
                return raw_response[:200] + "..." if len(raw_response) > 200 else raw_response
        except:
            return "Analysis summary not available" 
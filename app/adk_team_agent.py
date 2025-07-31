import os
import anthropic
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import asyncio
from dataclasses import dataclass
from enum import Enum

class AgentRole(Enum):
    SENIOR_DEVELOPER = "senior_developer"
    TRADING_ANALYST = "trading_analyst"
    RISK_MANAGER = "risk_manager"
    CODE_REVIEWER = "code_reviewer"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"

@dataclass
class AgentResponse:
    role: AgentRole
    content: str
    confidence: float
    recommendations: List[str]
    code_snippets: List[str]
    timestamp: str

class ADKTeamAgent:
    """Google ADK-based team agent for comprehensive MQL5 analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        # Configure Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Using Claude 3.5 Sonnet
        
        # Initialize team agents
        self.agents = self._initialize_agents()
        
    def _initialize_agents(self) -> Dict[AgentRole, Dict]:
        """Initialize specialized team agents with their roles and expertise"""
        return {
            AgentRole.SENIOR_DEVELOPER: {
                "name": "Senior MQL5 Developer",
                "expertise": [
                    "Advanced MQL5 programming",
                    "Algorithm optimization",
                    "Code architecture",
                    "Best practices implementation",
                    "Performance tuning"
                ],
                "prompt_template": self._get_senior_dev_prompt(),
                "focus_areas": ["code_quality", "architecture", "optimization"]
            },
            AgentRole.TRADING_ANALYST: {
                "name": "Trading Strategy Analyst",
                "expertise": [
                    "Market analysis",
                    "Strategy evaluation",
                    "Backtest interpretation",
                    "Trading psychology",
                    "Market conditions"
                ],
                "prompt_template": self._get_trading_analyst_prompt(),
                "focus_areas": ["strategy_logic", "market_analysis", "performance"]
            },
            AgentRole.RISK_MANAGER: {
                "name": "Risk Management Specialist",
                "expertise": [
                    "Position sizing",
                    "Stop loss optimization",
                    "Drawdown management",
                    "Risk-reward ratios",
                    "Portfolio protection"
                ],
                "prompt_template": self._get_risk_manager_prompt(),
                "focus_areas": ["risk_management", "position_sizing", "protection"]
            },
            AgentRole.CODE_REVIEWER: {
                "name": "Code Review Specialist",
                "expertise": [
                    "Code quality assessment",
                    "Bug detection",
                    "Security vulnerabilities",
                    "Maintainability",
                    "Documentation"
                ],
                "prompt_template": self._get_code_reviewer_prompt(),
                "focus_areas": ["code_quality", "bugs", "security", "maintainability"]
            },
            AgentRole.PERFORMANCE_OPTIMIZER: {
                "name": "Performance Optimization Expert",
                "expertise": [
                    "Execution speed optimization",
                    "Memory usage optimization",
                    "CPU utilization",
                    "Latency reduction",
                    "Resource management"
                ],
                "prompt_template": self._get_performance_optimizer_prompt(),
                "focus_areas": ["performance", "optimization", "efficiency"]
            }
        }
    
    def _get_senior_dev_prompt(self) -> str:
        """Get the senior developer prompt template"""
        return """You are a Senior MQL5 Developer with 15+ years of experience in algorithmic trading. 
Your expertise includes advanced MQL5 programming, algorithm optimization, and best practices implementation.

ANALYSIS FOCUS:
1. Code Architecture & Structure
2. Algorithm Efficiency & Optimization
3. MQL5 Best Practices Implementation
4. Advanced Programming Techniques
5. Code Maintainability & Scalability

Provide detailed analysis with:
- Specific code improvements with examples
- Architecture recommendations
- Performance optimization suggestions
- Best practices implementation
- Advanced MQL5 techniques

Format your response with clear sections and actionable code snippets."""

    def _get_trading_analyst_prompt(self) -> str:
        """Get the trading analyst prompt template"""
        return """You are a Senior Trading Strategy Analyst with deep expertise in market analysis and strategy evaluation.
Your focus is on trading logic, market conditions, and strategy performance optimization.

ANALYSIS FOCUS:
1. Trading Logic & Strategy Evaluation
2. Market Condition Analysis
3. Entry/Exit Optimization
4. Strategy Robustness
5. Market Adaptability

Provide insights on:
- Strategy logic effectiveness
- Market condition adaptability
- Entry/exit point optimization
- Strategy robustness across different markets
- Performance improvement suggestions"""

    def _get_risk_manager_prompt(self) -> str:
        """Get the risk manager prompt template"""
        return """You are a Risk Management Specialist with expertise in trading risk control and portfolio protection.
Your focus is on minimizing losses and optimizing risk-reward ratios.

ANALYSIS FOCUS:
1. Position Sizing Optimization
2. Stop Loss & Take Profit Strategies
3. Drawdown Management
4. Risk-Reward Ratios
5. Portfolio Protection

Provide recommendations for:
- Optimal position sizing
- Dynamic stop loss strategies
- Maximum drawdown limits
- Risk-reward optimization
- Portfolio protection mechanisms"""

    def _get_code_reviewer_prompt(self) -> str:
        """Get the code reviewer prompt template"""
        return """You are a Code Review Specialist with expertise in MQL5 code quality and security.
Your focus is on identifying issues and ensuring code maintainability.

ANALYSIS FOCUS:
1. Code Quality Assessment
2. Bug Detection & Prevention
3. Security Vulnerabilities
4. Code Maintainability
5. Documentation Quality

Review for:
- Code quality issues
- Potential bugs and errors
- Security vulnerabilities
- Maintainability concerns
- Documentation needs"""

    def _get_performance_optimizer_prompt(self) -> str:
        """Get the performance optimizer prompt template"""
        return """You are a Performance Optimization Expert specializing in MQL5 execution efficiency.
Your focus is on maximizing speed and minimizing resource usage.

ANALYSIS FOCUS:
1. Execution Speed Optimization
2. Memory Usage Optimization
3. CPU Utilization Efficiency
4. Latency Reduction
5. Resource Management

Optimize for:
- Faster execution times
- Reduced memory footprint
- Efficient CPU usage
- Lower latency
- Better resource management"""

    async def analyze_strategy_team(self, mq5_data: Dict, csv_data: Dict, summary: str,
                                  similar_strategies: List[Dict] = None) -> Dict:
        """Perform comprehensive team analysis using all specialized agents"""
        try:
            # Create analysis context
            context = self._create_analysis_context(mq5_data, csv_data, summary, similar_strategies)
            
            # Run all agents in parallel
            tasks = []
            for role in AgentRole:
                task = self._run_agent_analysis(role, context)
                tasks.append(task)
            
            # Wait for all agents to complete
            agent_responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process and structure responses
            team_analysis = self._process_team_responses(agent_responses)
            
            # Generate team consensus and final recommendations
            final_analysis = await self._generate_team_consensus(team_analysis, context)
            
            return {
                'success': True,
                'team_analysis': team_analysis,
                'final_analysis': final_analysis,
                'timestamp': datetime.now().isoformat(),
                'model_used': 'gemini-1.5-pro',
                'team_size': len(AgentRole)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'team_analysis': {},
                'final_analysis': {},
                'timestamp': datetime.now().isoformat(),
                'model_used': 'gemini-1.5-pro'
            }

    def _create_analysis_context(self, mq5_data: Dict, csv_data: Dict, summary: str,
                               similar_strategies: List[Dict] = None) -> str:
        """Create comprehensive analysis context for all agents"""
        context = f"""
STRATEGY ANALYSIS CONTEXT
========================

STRATEGY SUMMARY:
{summary}

MQL5 CODE:
{mq5_data.get('content', 'No code provided')}

BACKTEST RESULTS:
- Total Trades: {csv_data.get('total_trades', 0)}
- Win Rate: {csv_data.get('win_rate', 0):.2f}%
- Total PnL: {csv_data.get('total_pnl', 0):.2f}
- Max Drawdown: {csv_data.get('max_drawdown', 0):.2f}
- Sharpe Ratio: {csv_data.get('sharpe_ratio', 0):.2f}
- Average Trade: {csv_data.get('avg_trade', 0):.2f}

PERFORMANCE METRICS:
{json.dumps(csv_data.get('metrics', {}), indent=2)}

SIMILAR STRATEGIES:
{json.dumps(similar_strategies or [], indent=2)}

ANALYSIS REQUIREMENTS:
1. Provide specific, actionable recommendations
2. Include code snippets for improvements
3. Rate confidence level (0-100%)
4. Prioritize recommendations by impact
5. Consider both code and trading aspects
"""
        return context

    async def _run_agent_analysis(self, role: AgentRole, context: str) -> AgentResponse:
        """Run analysis for a specific agent role"""
        try:
            agent_info = self.agents[role]
            prompt = f"{agent_info['prompt_template']}\n\n{context}"
            
            # Generate response using Google ADK
            response = await self._generate_response(prompt, role)
            
            # Parse and structure the response
            parsed_response = self._parse_agent_response(response, role)
            
            return parsed_response
            
        except Exception as e:
            return AgentResponse(
                role=role,
                content=f"Error in {role.value} analysis: {str(e)}",
                confidence=0.0,
                recommendations=[],
                code_snippets=[],
                timestamp=datetime.now().isoformat()
            )

    async def _generate_response(self, prompt: str, role: AgentRole) -> str:
        """Generate response using Anthropic Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating response for {role.value}: {str(e)}"

    def _parse_agent_response(self, response: str, role: AgentRole) -> AgentResponse:
        """Parse and structure agent response"""
        try:
            # Extract confidence level (look for patterns like "confidence: 85%" or "85% confidence")
            confidence = self._extract_confidence(response)
            
            # Extract recommendations
            recommendations = self._extract_recommendations(response)
            
            # Extract code snippets
            code_snippets = self._extract_code_snippets(response)
            
            return AgentResponse(
                role=role,
                content=response,
                confidence=confidence,
                recommendations=recommendations,
                code_snippets=code_snippets,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return AgentResponse(
                role=role,
                content=response,
                confidence=0.0,
                recommendations=[],
                code_snippets=[],
                timestamp=datetime.now().isoformat()
            )

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence level from text"""
        import re
        patterns = [
            r'confidence:\s*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s*confidence',
            r'confidence\s*level:\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)/100\s*confidence'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 75.0  # Default confidence

    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from text"""
        import re
        recommendations = []
        
        # Look for numbered or bulleted recommendations
        patterns = [
            r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)',
            r'[-*]\s*(.+?)(?=\n[-*]|\n\n|$)',
            r'recommendation[s]?:\s*(.+?)(?=\n\n|$)',
            r'suggest[s]?:\s*(.+?)(?=\n\n|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            recommendations.extend([match.strip() for match in matches])
        
        return list(set(recommendations))  # Remove duplicates

    def _extract_code_snippets(self, text: str) -> List[str]:
        """Extract code snippets from text"""
        import re
        code_snippets = []
        
        # Look for code blocks
        patterns = [
            r'```mql5\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
            r'`([^`]+)`'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            code_snippets.extend([match.strip() for match in matches])
        
        return list(set(code_snippets))  # Remove duplicates

    def _process_team_responses(self, agent_responses: List[AgentResponse]) -> Dict:
        """Process and organize team responses"""
        team_analysis = {
            'agents': {},
            'consensus': {},
            'priorities': {},
            'summary': {}
        }
        
        for response in agent_responses:
            if isinstance(response, Exception):
                continue
                
            team_analysis['agents'][response.role.value] = {
                'name': self.agents[response.role]['name'],
                'content': response.content,
                'confidence': response.confidence,
                'recommendations': response.recommendations,
                'code_snippets': response.code_snippets,
                'timestamp': response.timestamp
            }
        
        return team_analysis

    async def _generate_team_consensus(self, team_analysis: Dict, context: str) -> Dict:
        """Generate team consensus and final recommendations"""
        try:
            consensus_prompt = self._create_consensus_prompt(team_analysis, context)
            consensus_response = await self._generate_response(consensus_prompt, AgentRole.SENIOR_DEVELOPER)
            
            return {
                'consensus_analysis': consensus_response,
                'priority_recommendations': self._extract_recommendations(consensus_response),
                'implementation_plan': self._create_implementation_plan(team_analysis),
                'risk_assessment': self._create_risk_assessment(team_analysis),
                'improvement_prompts': self._create_improvement_prompts(team_analysis)
            }
        except Exception as e:
            return {
                'consensus_analysis': f"Error generating consensus: {str(e)}",
                'priority_recommendations': [],
                'implementation_plan': {},
                'risk_assessment': {},
                'improvement_prompts': []
            }

    def _create_consensus_prompt(self, team_analysis: Dict, context: str) -> str:
        """Create prompt for team consensus generation"""
        return f"""
TEAM CONSENSUS ANALYSIS
======================

Based on the analysis from all team members, provide a comprehensive consensus and final recommendations.

TEAM ANALYSIS:
{json.dumps(team_analysis, indent=2)}

ORIGINAL CONTEXT:
{context}

TASK:
1. Synthesize all agent recommendations
2. Prioritize improvements by impact and feasibility
3. Create an implementation roadmap
4. Identify critical issues that need immediate attention
5. Provide specific MQL5 code improvements
6. Create improvement prompts for the developer

Format your response with clear sections and actionable items.
"""

    def _create_implementation_plan(self, team_analysis: Dict) -> Dict:
        """Create implementation plan from team analysis"""
        plan = {
            'immediate_actions': [],
            'short_term_improvements': [],
            'long_term_optimizations': [],
            'code_changes': [],
            'testing_requirements': []
        }
        
        for role, analysis in team_analysis['agents'].items():
            if analysis['confidence'] > 80:
                plan['immediate_actions'].extend(analysis['recommendations'][:2])
            elif analysis['confidence'] > 60:
                plan['short_term_improvements'].extend(analysis['recommendations'][:2])
            else:
                plan['long_term_optimizations'].extend(analysis['recommendations'][:1])
            
            plan['code_changes'].extend(analysis['code_snippets'])
        
        return plan

    def _create_risk_assessment(self, team_analysis: Dict) -> Dict:
        """Create risk assessment from team analysis"""
        risks = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': [],
            'mitigation_strategies': []
        }
        
        # Extract risk-related recommendations
        for role, analysis in team_analysis['agents'].items():
            if 'risk' in role.lower() or 'risk' in analysis['content'].lower():
                for rec in analysis['recommendations']:
                    if any(word in rec.lower() for word in ['critical', 'urgent', 'immediate']):
                        risks['high_risk'].append(rec)
                    elif any(word in rec.lower() for word in ['important', 'significant']):
                        risks['medium_risk'].append(rec)
                    else:
                        risks['low_risk'].append(rec)
        
        return risks

    def _create_improvement_prompts(self, team_analysis: Dict) -> List[str]:
        """Create specific improvement prompts for MQL5 development"""
        prompts = []
        
        for role, analysis in team_analysis['agents'].items():
            if analysis['code_snippets']:
                prompts.append(f"Based on {analysis['name']} analysis, implement the following improvements:")
                prompts.extend([f"- {rec}" for rec in analysis['recommendations'][:3]])
                prompts.append("Code examples:")
                prompts.extend(analysis['code_snippets'])
                prompts.append("")
        
        return prompts

    def generate_report_filename(self, strategy_name: str) -> str:
        """Generate filename for team analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in strategy_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        return f"team_analysis_{safe_name}_{timestamp}.json"

    def save_team_analysis_report(self, analysis_result: Dict, strategy_name: str,
                                reports_dir: str = "reports") -> str:
        """Save team analysis report to file"""
        try:
            os.makedirs(reports_dir, exist_ok=True)
            filename = self.generate_report_filename(strategy_name)
            filepath = os.path.join(reports_dir, filename)
            
            # Add metadata
            report_data = {
                'metadata': {
                    'strategy_name': strategy_name,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'team_size': len(AgentRole),
                    'model_used': 'gemini-1.5-pro',
                    'analysis_type': 'team_agent_analysis'
                },
                'analysis_result': analysis_result
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error saving team analysis report: {str(e)}")

    def get_team_analysis_summary(self, analysis_result: Dict) -> str:
        """Generate summary of team analysis"""
        if not analysis_result.get('success', False):
            return "Team analysis failed to complete successfully."
        
        summary_parts = []
        
        # Agent summary
        agents = analysis_result.get('team_analysis', {}).get('agents', {})
        summary_parts.append(f"Team Analysis completed with {len(agents)} specialized agents:")
        
        for role, analysis in agents.items():
            confidence = analysis.get('confidence', 0)
            rec_count = len(analysis.get('recommendations', []))
            summary_parts.append(f"- {analysis.get('name', role)}: {confidence:.1f}% confidence, {rec_count} recommendations")
        
        # Final analysis summary
        final_analysis = analysis_result.get('final_analysis', {})
        if final_analysis:
            priority_count = len(final_analysis.get('priority_recommendations', []))
            summary_parts.append(f"\nFinal Analysis: {priority_count} priority recommendations identified")
        
        return "\n".join(summary_parts) 
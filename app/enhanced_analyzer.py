import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .claude_agent import ClaudeAgent
from .adk_team_agent import ADKTeamAgent
from .prompt_engineer import MQL5PromptEngineer

class EnhancedAnalyzer:
    """Enhanced analyzer combining Claude and Google ADK team agents"""
    
    def __init__(self, claude_api_key: Optional[str] = None, google_api_key: Optional[str] = None):
        # Use the same Anthropic API key for both agents
        anthropic_key = claude_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.claude_agent = ClaudeAgent(anthropic_key)
        self.adk_team_agent = ADKTeamAgent(anthropic_key)  # Now uses Anthropic too
        self.prompt_engineer = MQL5PromptEngineer()
        
    async def analyze_strategy_comprehensive(self, mq5_data: Dict, csv_data: Dict, summary: str,
                                           similar_strategies: List[Dict] = None, 
                                           use_team_analysis: bool = True) -> Dict:
        """Perform comprehensive analysis using both Claude and ADK team agents"""
        
        results = {
            'claude_analysis': None,
            'team_analysis': None,
            'comprehensive_report': None,
            'improvement_prompts': None,
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'comprehensive'
        }
        
        try:
            # Run Claude analysis
            print("Starting Claude analysis...")
            claude_result = self.claude_agent.analyze_strategy(mq5_data, csv_data, summary, similar_strategies)
            results['claude_analysis'] = claude_result
            
            # Run ADK team analysis if requested
            if use_team_analysis:
                print("Starting ADK team analysis...")
                team_result = await self.adk_team_agent.analyze_strategy_team(mq5_data, csv_data, summary, similar_strategies)
                results['team_analysis'] = team_result
                
                # Generate improvement prompts
                if team_result.get('success', False):
                    results['improvement_prompts'] = self.prompt_engineer.create_improvement_prompts_section(
                        team_result.get('team_analysis', {})
                    )
            
            # Generate comprehensive report
            results['comprehensive_report'] = self._generate_comprehensive_report(results)
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'claude_analysis': results.get('claude_analysis'),
                'team_analysis': results.get('team_analysis'),
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'comprehensive'
            }
    
    def _generate_comprehensive_report(self, results: Dict) -> Dict:
        """Generate comprehensive report combining both analyses"""
        
        report = {
            'executive_summary': '',
            'critical_findings': [],
            'priority_recommendations': [],
            'implementation_plan': {},
            'code_improvements': [],
            'risk_assessment': {},
            'performance_optimizations': [],
            'team_insights': {},
            'improvement_prompts': results.get('improvement_prompts', '')
        }
        
        # Extract from Claude analysis
        claude_analysis = results.get('claude_analysis', {})
        if claude_analysis.get('success', False):
            claude_content = claude_analysis.get('analysis', {})
            if isinstance(claude_content, dict):
                report['executive_summary'] = claude_content.get('overview', '')
                report['critical_findings'].extend(self._extract_findings(claude_content.get('weaknesses', '')))
                report['priority_recommendations'].extend(self._extract_recommendations(claude_content.get('improvements', '')))
                report['code_improvements'].extend(self._extract_code_improvements(claude_content.get('code_improvements', '')))
        
        # Extract from team analysis
        team_analysis = results.get('team_analysis', {})
        if team_analysis.get('success', False):
            team_content = team_analysis.get('team_analysis', {})
            final_analysis = team_analysis.get('final_analysis', {})
            
            # Team insights
            report['team_insights'] = {
                'agents_used': len(team_content.get('agents', {})),
                'consensus_analysis': final_analysis.get('consensus_analysis', ''),
                'priority_recommendations': final_analysis.get('priority_recommendations', []),
                'implementation_plan': final_analysis.get('implementation_plan', {}),
                'risk_assessment': final_analysis.get('risk_assessment', {})
            }
            
            # Merge recommendations
            report['priority_recommendations'].extend(final_analysis.get('priority_recommendations', []))
            report['implementation_plan'] = final_analysis.get('implementation_plan', {})
            report['risk_assessment'] = final_analysis.get('risk_assessment', {})
            
            # Extract performance optimizations from team analysis
            agents = team_content.get('agents', {})
            for role, analysis in agents.items():
                if 'performance' in role.lower():
                    report['performance_optimizations'].extend(analysis.get('recommendations', []))
        
        # Remove duplicates
        report['critical_findings'] = list(set(report['critical_findings']))
        report['priority_recommendations'] = list(set(report['priority_recommendations']))
        report['code_improvements'] = list(set(report['code_improvements']))
        report['performance_optimizations'] = list(set(report['performance_optimizations']))
        
        return report
    
    def _extract_findings(self, text: str) -> List[str]:
        """Extract findings from text"""
        if not text:
            return []
        
        findings = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                findings.append(line[1:].strip())
            elif line and line[0].isdigit() and '.' in line:
                findings.append(line.split('.', 1)[1].strip() if '.' in line else line)
        
        return findings
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from text"""
        if not text:
            return []
        
        recommendations = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                recommendations.append(line[1:].strip())
            elif line and line[0].isdigit() and '.' in line:
                recommendations.append(line.split('.', 1)[1].strip() if '.' in line else line)
        
        return recommendations
    
    def _extract_code_improvements(self, text: str) -> List[str]:
        """Extract code improvements from text"""
        if not text:
            return []
        
        improvements = []
        lines = text.split('\n')
        current_improvement = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('```') or line.startswith('`'):
                if current_improvement:
                    improvements.append(current_improvement.strip())
                    current_improvement = ""
            elif line:
                current_improvement += line + "\n"
        
        if current_improvement:
            improvements.append(current_improvement.strip())
        
        return improvements
    
    def save_comprehensive_report(self, analysis_result: Dict, strategy_name: str,
                                reports_dir: str = "reports") -> str:
        """Save comprehensive analysis report"""
        try:
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in strategy_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"comprehensive_analysis_{safe_name}_{timestamp}.json"
            filepath = os.path.join(reports_dir, filename)
            
            # Add metadata
            report_data = {
                'metadata': {
                    'strategy_name': strategy_name,
                    'analysis_timestamp': analysis_result.get('timestamp'),
                    'analysis_type': analysis_result.get('analysis_type'),
                    'claude_success': analysis_result.get('claude_analysis', {}).get('success', False),
                    'team_analysis_success': analysis_result.get('team_analysis', {}).get('success', False)
                },
                'analysis_result': analysis_result
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error saving comprehensive report: {str(e)}")
    
    def generate_markdown_report(self, analysis_result: Dict, strategy_name: str) -> str:
        """Generate a markdown format report"""
        
        report = f"""# Comprehensive MQL5 Strategy Analysis Report

**Strategy:** {strategy_name}  
**Analysis Date:** {analysis_result.get('timestamp', 'Unknown')}  
**Analysis Type:** {analysis_result.get('analysis_type', 'comprehensive')}

---

## Executive Summary

{analysis_result.get('comprehensive_report', {}).get('executive_summary', 'No summary available')}

---

## Critical Findings

"""
        
        findings = analysis_result.get('comprehensive_report', {}).get('critical_findings', [])
        if findings:
            for i, finding in enumerate(findings, 1):
                report += f"{i}. {finding}\n"
        else:
            report += "No critical findings identified.\n"
        
        report += "\n---\n\n## Priority Recommendations\n\n"
        
        recommendations = analysis_result.get('comprehensive_report', {}).get('priority_recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
        else:
            report += "No priority recommendations available.\n"
        
        # Team Analysis Section
        team_insights = analysis_result.get('comprehensive_report', {}).get('team_insights', {})
        if team_insights:
            report += "\n---\n\n## Team Analysis Insights\n\n"
            report += f"**Agents Used:** {team_insights.get('agents_used', 0)}\n\n"
            
            consensus = team_insights.get('consensus_analysis', '')
            if consensus:
                report += "### Team Consensus\n\n"
                report += f"{consensus}\n\n"
        
        # Implementation Plan
        implementation_plan = analysis_result.get('comprehensive_report', {}).get('implementation_plan', {})
        if implementation_plan:
            report += "### Implementation Plan\n\n"
            
            immediate = implementation_plan.get('immediate_actions', [])
            if immediate:
                report += "#### Immediate Actions\n"
                for action in immediate:
                    report += f"- {action}\n"
                report += "\n"
            
            short_term = implementation_plan.get('short_term_improvements', [])
            if short_term:
                report += "#### Short-term Improvements\n"
                for improvement in short_term:
                    report += f"- {improvement}\n"
                report += "\n"
            
            long_term = implementation_plan.get('long_term_optimizations', [])
            if long_term:
                report += "#### Long-term Optimizations\n"
                for optimization in long_term:
                    report += f"- {optimization}\n"
                report += "\n"
        
        # Risk Assessment
        risk_assessment = analysis_result.get('comprehensive_report', {}).get('risk_assessment', {})
        if risk_assessment:
            report += "### Risk Assessment\n\n"
            
            high_risk = risk_assessment.get('high_risk', [])
            if high_risk:
                report += "#### High Risk Issues\n"
                for risk in high_risk:
                    report += f"- {risk}\n"
                report += "\n"
            
            medium_risk = risk_assessment.get('medium_risk', [])
            if medium_risk:
                report += "#### Medium Risk Issues\n"
                for risk in medium_risk:
                    report += f"- {risk}\n"
                report += "\n"
        
        # Code Improvements
        code_improvements = analysis_result.get('comprehensive_report', {}).get('code_improvements', [])
        if code_improvements:
            report += "---\n\n## Code Improvements\n\n"
            for i, improvement in enumerate(code_improvements, 1):
                report += f"### Improvement {i}\n\n"
                report += f"```mql5\n{improvement}\n```\n\n"
        
        # Performance Optimizations
        performance_optimizations = analysis_result.get('comprehensive_report', {}).get('performance_optimizations', [])
        if performance_optimizations:
            report += "---\n\n## Performance Optimizations\n\n"
            for i, optimization in enumerate(performance_optimizations, 1):
                report += f"{i}. {optimization}\n"
        
        # Improvement Prompts
        improvement_prompts = analysis_result.get('improvement_prompts', '')
        if improvement_prompts:
            report += "\n---\n\n## MQL5 Script Improvement Prompts\n\n"
            report += improvement_prompts
        
        report += "\n---\n\n*Report generated by Enhanced MQL5 Strategy Analyzer with Claude AI and Google ADK Team Agents*"
        
        return report
    
    def save_markdown_report(self, analysis_result: Dict, strategy_name: str,
                           reports_dir: str = "reports") -> str:
        """Save markdown format report"""
        try:
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in strategy_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"comprehensive_analysis_{safe_name}_{timestamp}.md"
            filepath = os.path.join(reports_dir, filename)
            
            markdown_content = self.generate_markdown_report(analysis_result, strategy_name)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error saving markdown report: {str(e)}")
    
    def get_analysis_summary(self, analysis_result: Dict) -> str:
        """Generate summary of comprehensive analysis"""
        if not analysis_result.get('comprehensive_report'):
            return "Comprehensive analysis not available."
        
        summary_parts = []
        
        # Claude analysis summary
        claude_success = analysis_result.get('claude_analysis', {}).get('success', False)
        summary_parts.append(f"Claude Analysis: {'✓ Completed' if claude_success else '✗ Failed'}")
        
        # Team analysis summary
        team_success = analysis_result.get('team_analysis', {}).get('success', False)
        if team_success:
            team_insights = analysis_result.get('comprehensive_report', {}).get('team_insights', {})
            agents_used = team_insights.get('agents_used', 0)
            summary_parts.append(f"Team Analysis: ✓ Completed with {agents_used} specialized agents")
        else:
            summary_parts.append("Team Analysis: ✗ Failed")
        
        # Key findings
        findings = analysis_result.get('comprehensive_report', {}).get('critical_findings', [])
        if findings:
            summary_parts.append(f"Critical Findings: {len(findings)} identified")
        
        # Recommendations
        recommendations = analysis_result.get('comprehensive_report', {}).get('priority_recommendations', [])
        if recommendations:
            summary_parts.append(f"Priority Recommendations: {len(recommendations)} provided")
        
        return " | ".join(summary_parts) 
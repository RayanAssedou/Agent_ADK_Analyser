import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    CODE_IMPROVEMENT = "code_improvement"
    ARCHITECTURE_REVIEW = "architecture_review"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    RISK_MANAGEMENT = "risk_management"
    BUG_FIXING = "bug_fixing"
    FEATURE_ENHANCEMENT = "feature_enhancement"

@dataclass
class PromptTemplate:
    name: str
    description: str
    template: str
    variables: List[str]
    expected_output: str
    confidence_threshold: float

class MQL5PromptEngineer:
    """Specialized prompt engineer for MQL5 script improvement"""
    
    def __init__(self):
        self.prompts = self._initialize_prompts()
        self.senior_dev_expertise = self._get_senior_dev_expertise()
        
    def _initialize_prompts(self) -> Dict[PromptType, PromptTemplate]:
        """Initialize specialized MQL5 improvement prompts"""
        return {
            PromptType.CODE_IMPROVEMENT: PromptTemplate(
                name="MQL5 Code Improvement",
                description="Comprehensive code improvement with senior developer expertise",
                template=self._get_code_improvement_template(),
                variables=["mq5_code", "analysis_results", "performance_metrics", "specific_issues"],
                expected_output="Detailed code improvements with specific MQL5 snippets",
                confidence_threshold=0.85
            ),
            PromptType.ARCHITECTURE_REVIEW: PromptTemplate(
                name="MQL5 Architecture Review",
                description="Architecture and structure optimization",
                template=self._get_architecture_review_template(),
                variables=["mq5_code", "current_structure", "complexity_analysis"],
                expected_output="Architecture recommendations and refactoring suggestions",
                confidence_threshold=0.90
            ),
            PromptType.PERFORMANCE_OPTIMIZATION: PromptTemplate(
                name="MQL5 Performance Optimization",
                description="Execution speed and resource optimization",
                template=self._get_performance_optimization_template(),
                variables=["mq5_code", "performance_metrics", "bottlenecks"],
                expected_output="Performance optimization techniques and code examples",
                confidence_threshold=0.88
            ),
            PromptType.RISK_MANAGEMENT: PromptTemplate(
                name="MQL5 Risk Management Enhancement",
                description="Risk management and position sizing improvements",
                template=self._get_risk_management_template(),
                variables=["mq5_code", "risk_metrics", "current_risk_controls"],
                expected_output="Risk management enhancements with code implementation",
                confidence_threshold=0.92
            ),
            PromptType.BUG_FIXING: PromptTemplate(
                name="MQL5 Bug Detection and Fixing",
                description="Bug identification and correction",
                template=self._get_bug_fixing_template(),
                variables=["mq5_code", "error_logs", "unexpected_behavior"],
                expected_output="Bug fixes with explanations and prevention strategies",
                confidence_threshold=0.95
            ),
            PromptType.FEATURE_ENHANCEMENT: PromptTemplate(
                name="MQL5 Feature Enhancement",
                description="Feature addition and enhancement suggestions",
                template=self._get_feature_enhancement_template(),
                variables=["mq5_code", "current_features", "market_requirements"],
                expected_output="Feature enhancement proposals with implementation code",
                confidence_threshold=0.80
            )
        }
    
    def _get_senior_dev_expertise(self) -> Dict[str, List[str]]:
        """Define senior developer expertise areas"""
        return {
            "mql5_advanced": [
                "Expert MQL5 programming with 15+ years experience",
                "Advanced algorithm optimization techniques",
                "Complex indicator and EA development",
                "Multi-timeframe analysis implementation",
                "Advanced order management systems",
                "Custom indicator development",
                "Expert Advisor optimization",
                "Market microstructure understanding"
            ],
            "trading_expertise": [
                "Deep understanding of market dynamics",
                "Advanced risk management techniques",
                "Portfolio optimization strategies",
                "Market regime detection",
                "Volatility analysis and adaptation",
                "Cross-asset correlation analysis",
                "High-frequency trading concepts",
                "Market microstructure analysis"
            ],
            "code_quality": [
                "Clean code principles in MQL5",
                "Design patterns for trading systems",
                "Code maintainability and scalability",
                "Error handling best practices",
                "Memory management optimization",
                "Execution speed optimization",
                "Code documentation standards",
                "Testing and validation strategies"
            ],
            "performance_optimization": [
                "CPU usage optimization",
                "Memory footprint reduction",
                "Execution latency minimization",
                "Algorithm complexity analysis",
                "Resource management optimization",
                "Parallel processing techniques",
                "Caching strategies",
                "I/O optimization"
            ]
        }
    
    def _get_code_improvement_template(self) -> str:
        """Get comprehensive code improvement prompt template"""
        return """You are a Senior MQL5 Developer with 15+ years of experience in algorithmic trading. 
Your expertise includes advanced MQL5 programming, algorithm optimization, and best practices implementation.

EXPERTISE AREAS:
{expertise_areas}

ANALYSIS CONTEXT:
- MQL5 Code: {mq5_code}
- Analysis Results: {analysis_results}
- Performance Metrics: {performance_metrics}
- Specific Issues: {specific_issues}

TASK: Provide comprehensive code improvements with senior developer expertise

REQUIREMENTS:
1. **Code Quality Assessment**: Identify code quality issues and suggest improvements
2. **Performance Optimization**: Suggest performance enhancements with specific code examples
3. **Best Practices Implementation**: Apply MQL5 best practices and design patterns
4. **Error Handling**: Improve error handling and robustness
5. **Documentation**: Suggest code documentation improvements
6. **Maintainability**: Enhance code maintainability and readability

OUTPUT FORMAT:
## CODE QUALITY IMPROVEMENTS
[Specific code quality issues and solutions]

## PERFORMANCE OPTIMIZATIONS
[Performance enhancement suggestions with code examples]

## BEST PRACTICES IMPLEMENTATION
[Best practices application with specific code changes]

## ERROR HANDLING ENHANCEMENTS
[Improved error handling with code examples]

## DOCUMENTATION IMPROVEMENTS
[Code documentation suggestions]

## MAINTAINABILITY ENHANCEMENTS
[Code maintainability improvements]

## IMPLEMENTATION PRIORITY
[Prioritized list of improvements by impact]

Provide specific MQL5 code snippets for each improvement suggestion."""

    def _get_architecture_review_template(self) -> str:
        """Get architecture review prompt template"""
        return """You are a Senior MQL5 Architect with expertise in trading system design and optimization.

ARCHITECTURE ANALYSIS CONTEXT:
- Current MQL5 Code: {mq5_code}
- Current Structure: {current_structure}
- Complexity Analysis: {complexity_analysis}

TASK: Conduct comprehensive architecture review and provide optimization recommendations

REQUIREMENTS:
1. **Architecture Assessment**: Evaluate current code architecture
2. **Structural Improvements**: Suggest structural optimizations
3. **Modularity Enhancement**: Improve code modularity and reusability
4. **Scalability Analysis**: Assess and improve scalability
5. **Design Patterns**: Apply appropriate design patterns
6. **Code Organization**: Improve code organization and structure

OUTPUT FORMAT:
## ARCHITECTURE ASSESSMENT
[Current architecture evaluation]

## STRUCTURAL IMPROVEMENTS
[Structural optimization suggestions]

## MODULARITY ENHANCEMENTS
[Modularity improvements with code examples]

## SCALABILITY OPTIMIZATIONS
[Scalability improvements]

## DESIGN PATTERN APPLICATIONS
[Design pattern implementations]

## CODE ORGANIZATION IMPROVEMENTS
[Code organization suggestions]

Provide specific refactoring examples and code structure improvements."""

    def _get_performance_optimization_template(self) -> str:
        """Get performance optimization prompt template"""
        return """You are a Performance Optimization Expert specializing in MQL5 execution efficiency.

PERFORMANCE ANALYSIS CONTEXT:
- MQL5 Code: {mq5_code}
- Performance Metrics: {performance_metrics}
- Identified Bottlenecks: {bottlenecks}

TASK: Provide comprehensive performance optimization recommendations

REQUIREMENTS:
1. **Execution Speed Optimization**: Identify and fix performance bottlenecks
2. **Memory Usage Optimization**: Reduce memory footprint
3. **CPU Utilization Optimization**: Optimize CPU usage
4. **Algorithm Efficiency**: Improve algorithm efficiency
5. **Resource Management**: Optimize resource usage
6. **Latency Reduction**: Minimize execution latency

OUTPUT FORMAT:
## PERFORMANCE BOTTLENECKS
[Identified performance issues]

## EXECUTION SPEED OPTIMIZATIONS
[Speed improvement techniques with code examples]

## MEMORY USAGE OPTIMIZATIONS
[Memory optimization strategies]

## CPU UTILIZATION IMPROVEMENTS
[CPU optimization techniques]

## ALGORITHM EFFICIENCY ENHANCEMENTS
[Algorithm optimization suggestions]

## RESOURCE MANAGEMENT OPTIMIZATIONS
[Resource usage improvements]

## PERFORMANCE MONITORING
[Performance monitoring suggestions]

Provide specific optimization techniques with code examples."""

    def _get_risk_management_template(self) -> str:
        """Get risk management enhancement prompt template"""
        return """You are a Risk Management Specialist with expertise in trading risk control.

RISK ANALYSIS CONTEXT:
- MQL5 Code: {mq5_code}
- Risk Metrics: {risk_metrics}
- Current Risk Controls: {current_risk_controls}

TASK: Provide comprehensive risk management enhancements

REQUIREMENTS:
1. **Position Sizing Optimization**: Improve position sizing logic
2. **Stop Loss Enhancement**: Optimize stop loss strategies
3. **Take Profit Optimization**: Improve take profit mechanisms
4. **Drawdown Management**: Enhance drawdown control
5. **Risk-Reward Optimization**: Improve risk-reward ratios
6. **Portfolio Protection**: Implement portfolio protection mechanisms

OUTPUT FORMAT:
## RISK ASSESSMENT
[Current risk profile analysis]

## POSITION SIZING IMPROVEMENTS
[Position sizing optimization with code examples]

## STOP LOSS ENHANCEMENTS
[Stop loss strategy improvements]

## TAKE PROFIT OPTIMIZATIONS
[Take profit mechanism enhancements]

## DRAWDOWN MANAGEMENT
[Drawdown control improvements]

## RISK-REWARD OPTIMIZATIONS
[Risk-reward ratio improvements]

## PORTFOLIO PROTECTION
[Portfolio protection mechanisms]

Provide specific risk management code implementations."""

    def _get_bug_fixing_template(self) -> str:
        """Get bug fixing prompt template"""
        return """You are a Bug Detection and Fixing Expert specializing in MQL5 code quality.

BUG ANALYSIS CONTEXT:
- MQL5 Code: {mq5_code}
- Error Logs: {error_logs}
- Unexpected Behavior: {unexpected_behavior}

TASK: Identify and fix bugs with prevention strategies

REQUIREMENTS:
1. **Bug Identification**: Identify potential bugs and issues
2. **Root Cause Analysis**: Analyze root causes of issues
3. **Bug Fixes**: Provide specific bug fixes with code examples
4. **Prevention Strategies**: Suggest bug prevention techniques
5. **Testing Recommendations**: Provide testing strategies
6. **Code Validation**: Suggest code validation methods

OUTPUT FORMAT:
## BUG IDENTIFICATION
[Identified bugs and issues]

## ROOT CAUSE ANALYSIS
[Root cause analysis for each bug]

## BUG FIXES
[Specific bug fixes with code examples]

## PREVENTION STRATEGIES
[Bug prevention techniques]

## TESTING RECOMMENDATIONS
[Testing strategies for bug prevention]

## CODE VALIDATION
[Code validation methods]

Provide specific bug fixes with detailed explanations."""

    def _get_feature_enhancement_template(self) -> str:
        """Get feature enhancement prompt template"""
        return """You are a Feature Enhancement Specialist with expertise in MQL5 development.

FEATURE ANALYSIS CONTEXT:
- MQL5 Code: {mq5_code}
- Current Features: {current_features}
- Market Requirements: {market_requirements}

TASK: Provide feature enhancement proposals with implementation

REQUIREMENTS:
1. **Feature Gap Analysis**: Identify missing features
2. **Enhancement Proposals**: Suggest feature enhancements
3. **Implementation Plans**: Provide implementation strategies
4. **Code Examples**: Provide specific code implementations
5. **Integration Guidance**: Suggest integration approaches
6. **Testing Strategies**: Provide testing recommendations

OUTPUT FORMAT:
## FEATURE GAP ANALYSIS
[Identified feature gaps]

## ENHANCEMENT PROPOSALS
[Feature enhancement suggestions]

## IMPLEMENTATION PLANS
[Implementation strategies]

## CODE EXAMPLES
[Specific code implementations]

## INTEGRATION GUIDANCE
[Integration approaches]

## TESTING STRATEGIES
[Testing recommendations]

Provide specific feature enhancement code examples."""

    def generate_improvement_prompt(self, prompt_type: PromptType, context: Dict[str, Any]) -> str:
        """Generate a specific improvement prompt based on type and context"""
        template = self.prompts[prompt_type]
        
        # Format the template with context variables
        formatted_prompt = template.template
        
        # Replace variables in the template
        for var in template.variables:
            placeholder = f"{{{var}}}"
            value = context.get(var, f"[{var} not provided]")
            formatted_prompt = formatted_prompt.replace(placeholder, str(value))
        
        # Add expertise areas
        expertise_text = self._format_expertise_areas()
        formatted_prompt = formatted_prompt.replace("{expertise_areas}", expertise_text)
        
        return formatted_prompt
    
    def _format_expertise_areas(self) -> str:
        """Format expertise areas for prompt inclusion"""
        expertise_text = []
        for category, skills in self.senior_dev_expertise.items():
            expertise_text.append(f"{category.upper()}:")
            for skill in skills:
                expertise_text.append(f"- {skill}")
            expertise_text.append("")
        
        return "\n".join(expertise_text)
    
    def create_comprehensive_improvement_prompt(self, mq5_code: str, analysis_results: Dict, 
                                              performance_metrics: Dict, team_analysis: Dict) -> str:
        """Create a comprehensive improvement prompt combining all aspects"""
        
        # Extract specific issues from team analysis
        specific_issues = self._extract_specific_issues(team_analysis)
        
        # Create context for comprehensive prompt
        context = {
            "mq5_code": mq5_code,
            "analysis_results": json.dumps(analysis_results, indent=2),
            "performance_metrics": json.dumps(performance_metrics, indent=2),
            "specific_issues": json.dumps(specific_issues, indent=2),
            "team_analysis": json.dumps(team_analysis, indent=2)
        }
        
        # Generate comprehensive prompt
        comprehensive_prompt = f"""You are a Senior MQL5 Development Team Lead with 15+ years of experience in algorithmic trading.

EXPERTISE AREAS:
{self._format_expertise_areas()}

COMPREHENSIVE ANALYSIS CONTEXT:
- MQL5 Code: {context['mq5_code']}
- Analysis Results: {context['analysis_results']}
- Performance Metrics: {context['performance_metrics']}
- Specific Issues: {context['specific_issues']}
- Team Analysis: {context['team_analysis']}

TASK: Provide comprehensive MQL5 script improvement recommendations with senior developer expertise

REQUIREMENTS:
1. **Critical Issues Resolution**: Address critical issues identified by the team
2. **Code Quality Enhancement**: Improve overall code quality and maintainability
3. **Performance Optimization**: Optimize execution speed and resource usage
4. **Risk Management Enhancement**: Improve risk management and position sizing
5. **Architecture Improvement**: Enhance code architecture and structure
6. **Feature Enhancement**: Suggest valuable feature additions
7. **Best Practices Implementation**: Apply MQL5 best practices throughout

OUTPUT FORMAT:

## CRITICAL ISSUES & IMMEDIATE FIXES
[Address critical issues with specific code fixes]

## CODE QUALITY IMPROVEMENTS
[Comprehensive code quality enhancements]

## PERFORMANCE OPTIMIZATIONS
[Performance improvement strategies with code examples]

## RISK MANAGEMENT ENHANCEMENTS
[Risk management improvements with implementation]

## ARCHITECTURE IMPROVEMENTS
[Architecture and structure optimizations]

## FEATURE ENHANCEMENTS
[Valuable feature additions with code examples]

## BEST PRACTICES IMPLEMENTATION
[Best practices application throughout the code]

## IMPLEMENTATION ROADMAP
[Prioritized implementation plan]

## CODE EXAMPLES
[Specific MQL5 code snippets for all improvements]

## TESTING RECOMMENDATIONS
[Testing strategies for validation]

Provide specific, actionable MQL5 code improvements with detailed explanations for each recommendation."""

        return comprehensive_prompt
    
    def _extract_specific_issues(self, team_analysis: Dict) -> List[str]:
        """Extract specific issues from team analysis"""
        issues = []
        
        if 'agents' in team_analysis:
            for role, analysis in team_analysis['agents'].items():
                if 'recommendations' in analysis:
                    issues.extend(analysis['recommendations'])
        
        return list(set(issues))  # Remove duplicates
    
    def create_improvement_prompts_section(self, team_analysis: Dict) -> str:
        """Create a dedicated prompts section for MQL5 script improvement"""
        
        prompts_section = """## MQL5 SCRIPT IMPROVEMENT PROMPTS

Based on the comprehensive team analysis, here are specific improvement prompts for enhancing your MQL5 script:

### 1. CODE QUALITY IMPROVEMENT PROMPT
```
You are a Senior MQL5 Developer. Analyze the following code and provide specific improvements for:
- Code structure and organization
- Variable naming and documentation
- Error handling and robustness
- Code maintainability and readability

MQL5 Code: [YOUR_CODE_HERE]
Analysis Results: [ANALYSIS_RESULTS]
```

### 2. PERFORMANCE OPTIMIZATION PROMPT
```
You are a Performance Optimization Expert. Optimize the following MQL5 code for:
- Execution speed improvement
- Memory usage reduction
- CPU utilization optimization
- Algorithm efficiency enhancement

MQL5 Code: [YOUR_CODE_HERE]
Performance Metrics: [PERFORMANCE_DATA]
```

### 3. RISK MANAGEMENT ENHANCEMENT PROMPT
```
You are a Risk Management Specialist. Enhance the risk management in this MQL5 strategy:
- Position sizing optimization
- Stop loss and take profit improvements
- Drawdown management
- Risk-reward ratio optimization

MQL5 Code: [YOUR_CODE_HERE]
Risk Metrics: [RISK_DATA]
```

### 4. ARCHITECTURE IMPROVEMENT PROMPT
```
You are an MQL5 Architect. Review and improve the architecture of this trading strategy:
- Code modularity and reusability
- Design pattern implementation
- Scalability improvements
- Code organization optimization

MQL5 Code: [YOUR_CODE_HERE]
Current Structure: [STRUCTURE_ANALYSIS]
```

### 5. FEATURE ENHANCEMENT PROMPT
```
You are a Feature Enhancement Specialist. Suggest improvements for this MQL5 strategy:
- Missing features identification
- Advanced indicator integration
- Market condition adaptation
- Strategy robustness enhancement

MQL5 Code: [YOUR_CODE_HERE]
Current Features: [FEATURE_LIST]
Market Requirements: [MARKET_NEEDS]
```

### 6. BUG DETECTION AND FIXING PROMPT
```
You are a Bug Detection Expert. Identify and fix issues in this MQL5 code:
- Potential bugs and errors
- Logic flaws and edge cases
- Error handling improvements
- Code validation and testing

MQL5 Code: [YOUR_CODE_HERE]
Error Logs: [ERROR_DATA]
Unexpected Behavior: [BEHAVIOR_ANALYSIS]
```

### IMPLEMENTATION GUIDELINES:
1. **Start with Critical Issues**: Address high-priority issues first
2. **Test Incrementally**: Test each improvement before proceeding
3. **Document Changes**: Document all modifications and their rationale
4. **Validate Results**: Backtest improvements to ensure positive impact
5. **Iterate**: Continuously improve based on testing results

### SENIOR DEVELOPER TIPS:
- Always consider market conditions and strategy robustness
- Implement proper error handling and logging
- Use MQL5 best practices and design patterns
- Optimize for both performance and maintainability
- Consider scalability and future enhancements
- Validate all changes with comprehensive testing

Use these prompts with your preferred AI assistant to get detailed, expert-level improvements for your MQL5 trading strategy."""

        return prompts_section 
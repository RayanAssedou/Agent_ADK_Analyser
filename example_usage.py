#!/usr/bin/env python3
"""
Example script showing how to use the Trading Strategy AI Analyzer API
"""

import requests
import json
import sys

# Configure your API endpoint
API_BASE_URL = "http://localhost:8000"  # Change to your Replit URL when deployed

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy:", response.json())
            return True
        else:
            print("❌ API health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def analyze_strategy(mq5_file_path, csv_file_path, strategy_name="TestStrategy"):
    """Analyze a trading strategy"""
    print(f"\n📊 Analyzing strategy: {strategy_name}")
    
    try:
        with open(mq5_file_path, 'rb') as mq5_file, open(csv_file_path, 'rb') as csv_file:
            files = {
                'mq5_file': (mq5_file_path, mq5_file, 'text/plain'),
                'csv_file': (csv_file_path, csv_file, 'text/csv')
            }
            data = {
                'strategy_name': strategy_name,
                'include_similar': 'true'
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/analyze",
                files=files,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Analysis completed successfully!")
                print(f"📄 Report saved: {result.get('report_path')}")
                print(f"\n📋 Summary:\n{result.get('summary')}")
                return result
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                print(response.json())
                return None
                
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_reports():
    """List all available reports"""
    print("\n📁 Fetching reports list...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/reports")
        if response.status_code == 200:
            reports = response.json().get('reports', [])
            print(f"Found {len(reports)} reports:")
            for report in reports:
                print(f"  - {report['filename']} ({report['size']})")
            return reports
        else:
            print("❌ Failed to fetch reports")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def get_report_content(filename):
    """Get the content of a specific report"""
    print(f"\n📖 Fetching report: {filename}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/reports/{filename}")
        if response.status_code == 200:
            print("✅ Report content retrieved")
            return response.text
        else:
            print("❌ Failed to fetch report content")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main example workflow"""
    print("Trading Strategy AI Analyzer - Example Usage")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("\nPlease make sure the API server is running.")
        print("Run: python main.py")
        sys.exit(1)
    
    # Example: Analyze a strategy (you need to provide your own files)
    # Uncomment and modify the paths below to test with your files
    """
    result = analyze_strategy(
        mq5_file_path="path/to/your/strategy.mq5",
        csv_file_path="path/to/your/backtest.csv",
        strategy_name="MyAwesomeStrategy"
    )
    """
    
    # List available reports
    reports = list_reports()
    
    # Get content of the first report (if any)
    if reports:
        first_report = reports[0]['filename']
        content = get_report_content(first_report)
        if content:
            print(f"\nFirst 500 characters of {first_report}:")
            print("-" * 50)
            print(content[:500] + "...")

if __name__ == "__main__":
    main()
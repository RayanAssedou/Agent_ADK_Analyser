from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import os
import tempfile
from datetime import datetime

from app.parser import MQL5Parser, CSVBacktestParser, create_summary
from app.basic_store import BasicStore
from app.claude_agent import ClaudeAgent
from app.enhanced_analyzer import EnhancedAnalyzer
from app.utils import (
    validate_file_upload, save_uploaded_file, list_reports, 
    read_report_content, format_file_size, validate_csv_structure
)

router = APIRouter()

# Initialize components
mq5_parser = MQL5Parser()
csv_parser = CSVBacktestParser()
chroma_store = BasicStore()

# Initialize agents (will be created when needed)
claude_agent = None
enhanced_analyzer = None

def get_claude_agent():
    """Get or create Claude agent instance"""
    global claude_agent
    if claude_agent is None:
        try:
            claude_agent = ClaudeAgent()
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
    return claude_agent

def get_enhanced_analyzer():
    """Get or create Enhanced Analyzer instance"""
    global enhanced_analyzer
    if enhanced_analyzer is None:
        try:
            enhanced_analyzer = EnhancedAnalyzer()
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
    return enhanced_analyzer

@router.post("/upload")
async def upload_files(
    mq5_file: UploadFile = File(...),
    csv_file: UploadFile = File(...),
    strategy_name: Optional[str] = Form(None)
):
    """Upload MQL5 and CSV files for analysis"""
    try:
        # Validate file types
        if not mq5_file.filename.lower().endswith('.mq5'):
            raise HTTPException(status_code=400, detail="MQL5 file must have .mq5 extension")
        
        if not csv_file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="CSV file must have .csv extension")
        
        # Save uploaded files
        upload_dir = "storage/uploads"
        mq5_path = save_uploaded_file(mq5_file, upload_dir)
        csv_path = save_uploaded_file(csv_file, upload_dir)
        
        # Validate CSV structure
        csv_validation = validate_csv_structure(csv_path)
        if not csv_validation['valid']:
            # Clean up uploaded files
            os.remove(mq5_path)
            os.remove(csv_path)
            raise HTTPException(status_code=400, detail=csv_validation['error'])
        
        return {
            "success": True,
            "message": "Files uploaded successfully",
            "mq5_file": os.path.basename(mq5_path),
            "csv_file": os.path.basename(csv_path),
            "strategy_name": strategy_name or "Unknown Strategy"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_strategy(
    mq5_file: UploadFile = File(...),
    csv_file: UploadFile = File(...),
    strategy_name: Optional[str] = Form(None),
    include_similar: bool = Form(True)
):
    """Analyze trading strategy using Claude AI"""
    try:
        # Get Claude agent
        claude = get_claude_agent()
        
        # Save uploaded files temporarily
        upload_dir = "storage/uploads"
        mq5_path = save_uploaded_file(mq5_file, upload_dir)
        csv_path = save_uploaded_file(csv_file, upload_dir)
        
        # Parse files
        mq5_data = mq5_parser.parse_mq5_file(mq5_path)
        csv_data = csv_parser.parse_csv_file(csv_path)
        
        # Check for parsing errors
        if 'error' in mq5_data:
            raise HTTPException(status_code=400, detail=f"MQL5 parsing error: {mq5_data['error']}")
        
        if 'error' in csv_data:
            raise HTTPException(status_code=400, detail=f"CSV parsing error: {csv_data['error']}")
        
        # Create summary
        summary = create_summary(mq5_data, csv_data)
        
        # Get similar strategies if requested
        similar_strategies = []
        if include_similar:
            similar_strategies = chroma_store.similarity_search(summary, n_results=3)
        
        # Analyze with Claude
        analysis_result = claude.analyze_strategy(
            mq5_data=mq5_data,
            csv_data=csv_data,
            summary=summary,
            similar_strategies=similar_strategies
        )
        
        if not analysis_result['success']:
            raise HTTPException(status_code=500, detail=f"Claude analysis failed: {analysis_result['error']}")
        
        # Store in ChromaDB
        strategy_name = strategy_name or mq5_data.get('strategy_name', 'Unknown Strategy')
        storage_result = chroma_store.store_strategy(
            strategy_name=strategy_name,
            mq5_data=mq5_data,
            csv_data=csv_data,
            summary=summary,
            claude_response=analysis_result['raw_response']
        )
        
        # Save report
        report_path = claude.save_analysis_report(
            analysis_result=analysis_result,
            strategy_name=strategy_name
        )
        
        # Clean up uploaded files
        try:
            os.remove(mq5_path)
            os.remove(csv_path)
        except:
            pass
        
        return {
            "success": True,
            "strategy_name": strategy_name,
            "analysis": analysis_result['analysis'],
            "summary": claude.get_analysis_summary(analysis_result),
            "report_path": report_path,
            "storage_result": storage_result,
            "similar_strategies_found": len(similar_strategies)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-comprehensive")
async def analyze_strategy_comprehensive(
    mq5_file: UploadFile = File(...),
    csv_file: UploadFile = File(...),
    strategy_name: Optional[str] = Form(None),
    include_similar: bool = Form(True),
    use_team_analysis: bool = Form(True)
):
    """Analyze trading strategy using both Claude and Google ADK team agents"""
    try:
        # Get Enhanced Analyzer
        analyzer = get_enhanced_analyzer()
        
        # Save uploaded files temporarily
        upload_dir = "storage/uploads"
        mq5_path = save_uploaded_file(mq5_file, upload_dir)
        csv_path = save_uploaded_file(csv_file, upload_dir)
        
        # Parse files
        mq5_data = mq5_parser.parse_mq5_file(mq5_path)
        csv_data = csv_parser.parse_csv_file(csv_path)
        
        # Check for parsing errors
        if 'error' in mq5_data:
            raise HTTPException(status_code=400, detail=f"MQL5 parsing error: {mq5_data['error']}")
        
        if 'error' in csv_data:
            raise HTTPException(status_code=400, detail=f"CSV parsing error: {csv_data['error']}")
        
        # Create summary
        summary = create_summary(mq5_data, csv_data)
        
        # Get similar strategies if requested
        similar_strategies = []
        if include_similar:
            similar_strategies = chroma_store.similarity_search(summary, n_results=3)
        
        # Perform comprehensive analysis
        analysis_result = await analyzer.analyze_strategy_comprehensive(
            mq5_data=mq5_data,
            csv_data=csv_data,
            summary=summary,
            similar_strategies=similar_strategies,
            use_team_analysis=use_team_analysis
        )
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {analysis_result['error']}")
        
        # Store in ChromaDB
        strategy_name = strategy_name or mq5_data.get('strategy_name', 'Unknown Strategy')
        storage_result = chroma_store.store_strategy(
            strategy_name=strategy_name,
            mq5_data=mq5_data,
            csv_data=csv_data,
            summary=summary,
            claude_response=analysis_result.get('claude_analysis', {}).get('raw_response', '')
        )
        
        # Save comprehensive report
        json_report_path = analyzer.save_comprehensive_report(
            analysis_result=analysis_result,
            strategy_name=strategy_name
        )
        
        # Save markdown report
        markdown_report_path = analyzer.save_markdown_report(
            analysis_result=analysis_result,
            strategy_name=strategy_name
        )
        
        # Clean up uploaded files
        try:
            os.remove(mq5_path)
            os.remove(csv_path)
        except:
            pass
        
        return {
            "success": True,
            "strategy_name": strategy_name,
            "comprehensive_analysis": analysis_result['comprehensive_report'],
            "summary": analyzer.get_analysis_summary(analysis_result),
            "json_report_path": json_report_path,
            "markdown_report_path": markdown_report_path,
            "storage_result": storage_result,
            "similar_strategies_found": len(similar_strategies),
            "team_analysis_enabled": use_team_analysis,
            "improvement_prompts": analysis_result.get('improvement_prompts', '')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def get_reports():
    """Get list of all analysis reports"""
    try:
        reports = list_reports()
        return {
            "success": True,
            "reports": reports,
            "total_reports": len(reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{filename}")
async def get_report_content(filename: str):
    """Get content of a specific report"""
    try:
        filepath = os.path.join("reports", filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Report not found")
        
        content = read_report_content(filepath)
        return {
            "success": True,
            "filename": filename,
            "content": content,
            "size": format_file_size(os.path.getsize(filepath))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{filename}/download")
async def download_report(filename: str):
    """Download a report file"""
    try:
        filepath = os.path.join("reports", filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='text/plain'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reports/{filename}")
async def delete_report(filename: str):
    """Delete a report file"""
    try:
        filepath = os.path.join("reports", filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Report not found")
        
        os.remove(filepath)
        return {"success": True, "message": f"Report {filename} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_stored_strategies():
    """Get all strategies stored in ChromaDB"""
    try:
        strategies = chroma_store.get_all_strategies()
        return {
            "success": True,
            "strategies": strategies,
            "total_strategies": len(strategies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/search")
async def search_strategies(query: str, limit: int = 5):
    """Search for similar strategies"""
    try:
        results = chroma_store.search_similar_strategies(query, n_results=limit)
        return {
            "success": True,
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/{strategy_id}")
async def get_strategy_by_id(strategy_id: str):
    """Get specific strategy by ID"""
    try:
        strategy = chroma_store.get_strategy_by_id(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return {
            "success": True,
            "strategy": strategy
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete strategy from ChromaDB"""
    try:
        success = chroma_store.delete_strategy(strategy_id)
        if not success:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return {"success": True, "message": f"Strategy {strategy_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        chroma_stats = chroma_store.get_statistics()
        reports = list_reports()
        
        return {
            "success": True,
            "chroma_stats": chroma_stats,
            "total_reports": len(reports),
            "total_strategies": chroma_stats.get('total_strategies', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-csv")
async def validate_csv_structure_endpoint(csv_file: UploadFile = File(...)):
    """Validate CSV file structure"""
    try:
        # Save file temporarily
        upload_dir = "storage/uploads"
        csv_path = save_uploaded_file(csv_file, upload_dir)
        
        # Validate structure
        validation = validate_csv_structure(csv_path)
        
        # Clean up
        try:
            os.remove(csv_path)
        except:
            pass
        
        return {
            "success": True,
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
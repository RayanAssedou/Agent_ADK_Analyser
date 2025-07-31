import os
import shutil
from typing import List, Dict, Optional
from datetime import datetime
import json

def validate_file_upload(file_path: str, allowed_extensions: List[str]) -> Dict:
    """Validate uploaded file"""
    try:
        if not os.path.exists(file_path):
            return {'valid': False, 'error': 'File does not exist'}
        
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in allowed_extensions:
            return {
                'valid': False, 
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }
        
        file_size = os.path.getsize(file_path)
        max_size = 10 * 1024 * 1024  # 10MB limit
        if file_size > max_size:
            return {
                'valid': False, 
                'error': f'File too large. Max size: {max_size // (1024*1024)}MB'
            }
        
        return {'valid': True, 'file_size': file_size}
        
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def save_uploaded_file(uploaded_file, upload_dir: str) -> str:
    """Save uploaded file to storage"""
    try:
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{uploaded_file.filename}"
        filepath = os.path.join(upload_dir, filename)
        
        # Save file
        with open(filepath, 'wb') as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)
        
        return filepath
        
    except Exception as e:
        raise Exception(f"Failed to save uploaded file: {str(e)}")

def get_file_info(file_path: str) -> Dict:
    """Get file information"""
    try:
        stat = os.stat(file_path)
        return {
            'filename': os.path.basename(file_path),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    except Exception as e:
        return {'error': str(e)}

def list_reports(reports_dir: str = "reports") -> List[Dict]:
    """List all analysis reports"""
    try:
        if not os.path.exists(reports_dir):
            return []
        
        reports = []
        for filename in os.listdir(reports_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(reports_dir, filename)
                file_info = get_file_info(filepath)
                
                # Try to extract strategy name from filename
                strategy_name = filename.replace('report_', '').replace('.txt', '')
                strategy_name = strategy_name.replace('_', ' ')
                
                reports.append({
                    'filename': filename,
                    'strategy_name': strategy_name,
                    'filepath': filepath,
                    'size': file_info.get('size', 0),
                    'created': file_info.get('created', ''),
                    'modified': file_info.get('modified', '')
                })
        
        # Sort by modification date (newest first)
        reports.sort(key=lambda x: x['modified'], reverse=True)
        return reports
        
    except Exception as e:
        print(f"Error listing reports: {str(e)}")
        return []

def read_report_content(filepath: str) -> str:
    """Read report content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading report: {str(e)}"

def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """Clean up old files in directory"""
    try:
        if not os.path.exists(directory):
            return 0
        
        current_time = datetime.now()
        deleted_count = 0
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if (current_time - file_time).total_seconds() > max_age_hours * 3600:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except:
                    pass
        
        return deleted_count
        
    except Exception as e:
        print(f"Error cleaning up files: {str(e)}")
        return 0

def create_backup(file_path: str, backup_dir: str = "backups") -> str:
    """Create backup of a file"""
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{timestamp}_{filename}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
        
    except Exception as e:
        raise Exception(f"Failed to create backup: {str(e)}")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def validate_csv_structure(file_path: str) -> Dict:
    """Validate CSV file structure for backtest data"""
    try:
        import pandas as pd
        
        # Try to read CSV with comment lines (for MT5 format)
        try:
            df = pd.read_csv(file_path, comment='#', nrows=5)
        except:
            # If that fails, try without comment parameter
            df = pd.read_csv(file_path, nrows=5)
        
        # Define expected column formats
        standard_columns = ['Timestamp', 'Action', 'Symbol', 'Price', 'PnL']
        mt5_columns = ['Time', 'Symbol', 'Type', 'Volume', 'Price', 'OpenPrice', 'ClosePrice', 'SL', 'TP', 'Profit', 'Balance', 'Equity', 'Comment']
        
        # Check if it matches standard format
        if all(col in df.columns for col in standard_columns):
            return {
                'valid': True,
                'format': 'standard',
                'columns': list(df.columns),
                'sample_rows': df.head(3).to_dict('records')
            }
        
        # Check if it matches MT5 format
        if all(col in df.columns for col in mt5_columns):
            return {
                'valid': True,
                'format': 'mt5',
                'columns': list(df.columns),
                'sample_rows': df.head(3).to_dict('records')
            }
        
        # If neither format matches exactly, check for partial matches
        standard_matches = sum(1 for col in standard_columns if col in df.columns)
        mt5_matches = sum(1 for col in mt5_columns if col in df.columns)
        
        if standard_matches >= 3:
            return {
                'valid': True,
                'format': 'standard_partial',
                'columns': list(df.columns),
                'sample_rows': df.head(3).to_dict('records'),
                'warning': f"Partial standard format match ({standard_matches}/{len(standard_columns)} columns)"
            }
        
        if mt5_matches >= 5:
            return {
                'valid': True,
                'format': 'mt5_partial',
                'columns': list(df.columns),
                'sample_rows': df.head(3).to_dict('records'),
                'warning': f"Partial MT5 format match ({mt5_matches}/{len(mt5_columns)} columns)"
            }
        
        # If no good match found
        return {
            'valid': False,
            'error': f"CSV format not recognized. Found columns: {list(df.columns)}",
            'found_columns': list(df.columns),
            'expected_standard': standard_columns,
            'expected_mt5': mt5_columns
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"Failed to validate CSV: {str(e)}"
        }

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext
    
    return filename

def get_system_info() -> Dict:
    """Get system information"""
    try:
        import platform
        import psutil
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_usage': psutil.disk_usage('/').percent
        }
    except ImportError:
        return {
            'platform': 'Unknown',
            'python_version': 'Unknown',
            'note': 'psutil not available for detailed system info'
        }
    except Exception as e:
        return {
            'error': str(e)
        } 
import os
import json
from typing import List, Dict, Optional
from datetime import datetime

class BasicStore:
    """Basic storage for trading strategy data without embeddings"""
    
    def __init__(self, storage_file: str = "storage/strategies.json"):
        self.storage_file = storage_file
        self.strategies = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load data from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.strategies = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            self.strategies = {}
    
    def _save_data(self):
        """Save data to storage file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.strategies, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def store_strategy(self, strategy_name: str, mq5_data: Dict, csv_data: Dict, 
                      summary: str, claude_response: str) -> str:
        """Store strategy data"""
        try:
            strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare metadata
            metadata = {
                "strategy_name": strategy_name,
                "timestamp": datetime.now().isoformat(),
                "total_trades": csv_data.get('stats', {}).get('total_trades', 0),
                "win_rate": csv_data.get('stats', {}).get('win_rate', 0),
                "total_pnl": csv_data.get('stats', {}).get('total_pnl', 0),
                "indicators": ", ".join(mq5_data.get('indicators', [])),
                "functions": ", ".join(mq5_data.get('functions', [])),
                "claude_response_length": len(claude_response)
            }
            
            # Store strategy
            self.strategies[strategy_id] = {
                'document': summary,
                'metadata': metadata,
                'mq5_data': mq5_data,
                'csv_data': csv_data,
                'claude_response': claude_response
            }
            
            self._save_data()
            return "Strategy stored successfully"
        except Exception as e:
            return f"Failed to store strategy: {str(e)}"
    
    def search_similar_strategies(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar strategies based on query (basic text search)"""
        try:
            if not self.strategies:
                return []
            
            # Simple text-based search
            query_lower = query.lower()
            matches = []
            
            for strategy_id, strategy_data in self.strategies.items():
                # Search in document and metadata
                document = strategy_data['document'].lower()
                strategy_name = strategy_data['metadata']['strategy_name'].lower()
                indicators = strategy_data['metadata']['indicators'].lower()
                
                # Calculate simple relevance score
                score = 0
                if query_lower in document:
                    score += 2
                if query_lower in strategy_name:
                    score += 3
                if query_lower in indicators:
                    score += 1
                
                if score > 0:
                    matches.append({
                        'id': strategy_id,
                        'similarity': score / 6.0,  # Normalize to 0-1
                        'metadata': strategy_data['metadata'],
                        'document': strategy_data['document']
                    })
            
            # Sort by score and return top results
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            return matches[:n_results]
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def get_all_strategies(self) -> List[Dict]:
        """Get all stored strategies"""
        try:
            strategies = []
            for strategy_id, strategy_data in self.strategies.items():
                strategies.append({
                    'id': strategy_id,
                    'metadata': strategy_data['metadata'],
                    'document': strategy_data['document']
                })
            return strategies
        except Exception as e:
            print(f"Get all strategies error: {str(e)}")
            return []
    
    def get_strategy_by_id(self, strategy_id: str) -> Optional[Dict]:
        """Get specific strategy by ID"""
        try:
            if strategy_id in self.strategies:
                strategy_data = self.strategies[strategy_id]
                return {
                    'id': strategy_id,
                    'metadata': strategy_data['metadata'],
                    'document': strategy_data['document'],
                    'mq5_data': strategy_data.get('mq5_data', {}),
                    'csv_data': strategy_data.get('csv_data', {}),
                    'claude_response': strategy_data.get('claude_response', '')
                }
            return None
        except Exception as e:
            print(f"Get strategy by ID error: {str(e)}")
            return None
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete strategy by ID"""
        try:
            if strategy_id in self.strategies:
                del self.strategies[strategy_id]
                self._save_data()
                return True
            return False
        except Exception as e:
            print(f"Delete strategy error: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get storage statistics"""
        try:
            return {
                'total_strategies': len(self.strategies),
                'storage_file': self.storage_file,
                'storage_type': 'BasicStore'
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_strategies': 0
            }
    
    def create_strategy_embedding(self, text: str) -> List[float]:
        """Create dummy embedding for compatibility"""
        try:
            # Return a dummy embedding (all zeros)
            return [0.0] * 384  # Standard embedding size
        except Exception as e:
            print(f"Embedding creation error: {str(e)}")
            return []
    
    def similarity_search(self, strategy_summary: str, n_results: int = 3) -> List[Dict]:
        """Find similar strategies based on summary (basic text search)"""
        try:
            if not self.strategies:
                return []
            
            # Use the same search logic as search_similar_strategies
            return self.search_similar_strategies(strategy_summary, n_results)
        except Exception as e:
            print(f"Similarity search error: {str(e)}")
            return [] 
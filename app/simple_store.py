import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np

class SimpleStore:
    """Simple in-memory storage for trading strategy data (alternative to ChromaDB)"""
    
    def __init__(self, storage_file: str = "storage/strategies.json"):
        self.storage_file = storage_file
        self.strategies = {}
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
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
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def store_strategy(self, strategy_name: str, mq5_data: Dict, csv_data: Dict, 
                      summary: str, claude_response: str) -> str:
        """Store strategy data"""
        try:
            strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create embedding from summary
            embedding = self.embedding_model.encode(summary).tolist()
            
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
                'embedding': embedding,
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
        """Search for similar strategies based on query"""
        try:
            if not self.strategies:
                return []
            
            # Create embedding for query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Calculate similarities
            similarities = []
            for strategy_id, strategy_data in self.strategies.items():
                similarity = self._cosine_similarity(query_embedding, strategy_data['embedding'])
                similarities.append({
                    'id': strategy_id,
                    'similarity': similarity,
                    'metadata': strategy_data['metadata'],
                    'document': strategy_data['document']
                })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:n_results]
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
                'storage_type': 'SimpleStore'
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_strategies': 0
            }
    
    def create_strategy_embedding(self, text: str) -> List[float]:
        """Create embedding for given text"""
        try:
            return self.embedding_model.encode(text).tolist()
        except Exception as e:
            print(f"Embedding creation error: {str(e)}")
            return []
    
    def similarity_search(self, strategy_summary: str, n_results: int = 3) -> List[Dict]:
        """Find similar strategies based on summary"""
        try:
            if not self.strategies:
                return []
            
            embedding = self.create_strategy_embedding(strategy_summary)
            if not embedding:
                return []
            
            # Calculate similarities
            similarities = []
            for strategy_id, strategy_data in self.strategies.items():
                similarity = self._cosine_similarity(embedding, strategy_data['embedding'])
                similarities.append({
                    'id': strategy_id,
                    'similarity': similarity,
                    'metadata': strategy_data['metadata']
                })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:n_results]
        except Exception as e:
            print(f"Similarity search error: {str(e)}")
            return [] 
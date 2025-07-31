import chromadb
import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime

class CustomEmbeddingFunction:
    """Custom embedding function to avoid onnxruntime issues"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

class ChromaStore:
    """ChromaDB vector storage for trading strategy embeddings"""
    
    def __init__(self, persist_directory: str = "storage/chromadb_store"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "trading_strategies"
        
        # Initialize custom embedding function
        self.embedding_function = CustomEmbeddingFunction()
        
        # Get or create collection with custom embedding function
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Trading strategy embeddings and metadata"}
            )
    
    def store_strategy(self, strategy_name: str, mq5_data: Dict, csv_data: Dict, 
                      summary: str, claude_response: str) -> str:
        """Store strategy data and embeddings in ChromaDB"""
        try:
            # Create embedding from summary
            embedding = self.embedding_function(summary)
            
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
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[summary],
                metadatas=[metadata],
                ids=[f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
            )
            
            return "Strategy stored successfully"
        except Exception as e:
            return f"Failed to store strategy: {str(e)}"
    
    def search_similar_strategies(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar strategies based on query"""
        try:
            # Create embedding for query
            query_embedding = self.embedding_function(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'distance': results['distances'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'document': results['documents'][0][i]
                    }
                    formatted_results.append(result)
            
            return formatted_results
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def get_all_strategies(self) -> List[Dict]:
        """Get all stored strategies"""
        try:
            results = self.collection.get()
            
            strategies = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    strategy = {
                        'id': results['ids'][i],
                        'metadata': results['metadatas'][i],
                        'document': results['documents'][i]
                    }
                    strategies.append(strategy)
            
            return strategies
        except Exception as e:
            print(f"Get all strategies error: {str(e)}")
            return []
    
    def get_strategy_by_id(self, strategy_id: str) -> Optional[Dict]:
        """Get specific strategy by ID"""
        try:
            results = self.collection.get(ids=[strategy_id])
            
            if results['ids']:
                return {
                    'id': results['ids'][0],
                    'metadata': results['metadatas'][0],
                    'document': results['documents'][0]
                }
            return None
        except Exception as e:
            print(f"Get strategy by ID error: {str(e)}")
            return None
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete strategy by ID"""
        try:
            self.collection.delete(ids=[strategy_id])
            return True
        except Exception as e:
            print(f"Delete strategy error: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get ChromaDB collection statistics"""
        try:
            count = self.collection.count()
            return {
                'total_strategies': count,
                'collection_name': self.collection_name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_strategies': 0
            }
    
    def create_strategy_embedding(self, text: str) -> List[float]:
        """Create embedding for given text"""
        try:
            return self.embedding_function(text)
        except Exception as e:
            print(f"Embedding creation error: {str(e)}")
            return []
    
    def similarity_search(self, strategy_summary: str, n_results: int = 3) -> List[Dict]:
        """Find similar strategies based on summary"""
        try:
            embedding = self.create_strategy_embedding(strategy_summary)
            if not embedding:
                return []
            
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results
            )
            
            similar_strategies = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    similar_strategies.append({
                        'id': results['ids'][0][i],
                        'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'metadata': results['metadatas'][0][i]
                    })
            
            return similar_strategies
        except Exception as e:
            print(f"Similarity search error: {str(e)}")
            return [] 
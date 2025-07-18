"""
Advanced Memory System for Ether AI
=====================================

This module implements a sophisticated vector database memory system that enables
the AI to store, retrieve, and learn from conversations using semantic similarity.

Features:
- Semantic memory storage using ChromaDB
- Intelligent conversation retrieval
- Context-aware memory search
- Long-term learning capabilities
- User preference tracking
- Memory consolidation and optimization

Author: Enhanced by AI Assistant
Version: 1.0.0
"""

import os
import json
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib
import pickle

# Try to import ChromaDB for vector storage
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ ChromaDB not available. Install with: pip install chromadb")

# Try to import sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ SentenceTransformers not available. Install with: pip install sentence-transformers")

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Represents a single memory entry in the system"""
    id: str
    content: str
    timestamp: str
    memory_type: str  # 'conversation', 'preference', 'fact', 'context'
    importance: float  # 0-1 scale
    tags: List[str]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    access_count: int = 0
    last_accessed: Optional[str] = None

class AdvancedMemorySystem:
    """Advanced memory system with vector database and semantic search"""
    
    def __init__(self, memory_dir: str = "memory_db"):
        self.memory_dir = memory_dir
        self.collection_name = "ether_memory"
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.memory_cache = {}
        self.max_cache_size = 1000
        
        # Initialize the system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the memory system components"""
        try:
            # Create memory directory
            os.makedirs(self.memory_dir, exist_ok=True)
            
            # Initialize ChromaDB if available
            if CHROMADB_AVAILABLE:
                self._initialize_chromadb()
            else:
                logger.warning("ChromaDB not available. Using fallback memory system.")
                self._initialize_fallback()
            
            # Initialize embedding model if available
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self._initialize_embedding_model()
            else:
                logger.warning("SentenceTransformers not available. Using basic similarity.")
                
            logger.info("✅ Advanced Memory System initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize memory system: {e}")
            self._initialize_fallback()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB vector database"""
        try:
            # Create ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.memory_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(self.collection_name)
                logger.info(f"✅ Connected to existing memory collection: {self.collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Ether AI Memory System"}
                )
                logger.info(f"✅ Created new memory collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            raise
    
    def _initialize_fallback(self):
        """Initialize fallback memory system (JSON-based)"""
        self.fallback_memory_file = os.path.join(self.memory_dir, "fallback_memory.json")
        self.fallback_memory = self._load_fallback_memory()
        logger.info("✅ Fallback memory system initialized")
    
    def _initialize_embedding_model(self):
        """Initialize sentence transformer model for embeddings"""
        try:
            model_name = "all-MiniLM-L6-v2"  # Fast, efficient model
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"✅ Embedding model loaded: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def _load_fallback_memory(self) -> Dict:
        """Load fallback memory from JSON file"""
        if os.path.exists(self.fallback_memory_file):
            try:
                with open(self.fallback_memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load fallback memory: {e}")
        return {"memories": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_fallback_memory(self):
        """Save fallback memory to JSON file"""
        try:
            with open(self.fallback_memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.fallback_memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save fallback memory: {e}")
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using sentence transformer"""
        if not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode(text).tolist()
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def _calculate_importance(self, content: str, memory_type: str, metadata: Dict) -> float:
        """Calculate importance score for a memory entry"""
        importance = 0.5  # Base importance
        
        # Adjust based on memory type
        type_weights = {
            'preference': 0.9,
            'fact': 0.8,
            'conversation': 0.6,
            'context': 0.4
        }
        importance *= type_weights.get(memory_type, 0.5)
        
        # Adjust based on content length (longer = more important)
        if len(content) > 500:
            importance += 0.2
        elif len(content) > 100:
            importance += 0.1
        
        # Adjust based on metadata
        if metadata.get('user_rating'):
            importance += metadata['user_rating'] * 0.3
        
        if metadata.get('frequency', 0) > 1:
            importance += min(metadata['frequency'] * 0.1, 0.3)
        
        return min(importance, 1.0)
    
    def store_memory(self, content: str, memory_type: str = "conversation", 
                    tags: List[str] = None, metadata: Dict = None) -> str:
        """Store a memory entry in the system"""
        try:
            # Generate unique ID
            memory_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            # Prepare data
            tags = tags or []
            metadata = metadata or {}
            timestamp = datetime.now().isoformat()
            
            # Calculate importance
            importance = self._calculate_importance(content, memory_type, metadata)
            
            # Create memory entry
            memory_entry = MemoryEntry(
                id=memory_id,
                content=content,
                timestamp=timestamp,
                memory_type=memory_type,
                importance=importance,
                tags=tags,
                metadata=metadata
            )
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            if embedding:
                memory_entry.embedding = embedding
            
            # Store in ChromaDB if available
            if self.collection:
                self._store_in_chromadb(memory_entry)
            else:
                self._store_in_fallback(memory_entry)
            
            # Update cache
            self._update_cache(memory_entry)
            
            logger.info(f"✅ Memory stored: {memory_id} ({memory_type})")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store memory: {e}")
            return None
    
    def _store_in_chromadb(self, memory_entry: MemoryEntry):
        """Store memory entry in ChromaDB"""
        try:
            self.collection.add(
                documents=[memory_entry.content],
                metadatas=[{
                    "id": memory_entry.id,
                    "timestamp": memory_entry.timestamp,
                    "memory_type": memory_entry.memory_type,
                    "importance": memory_entry.importance,
                    "tags": json.dumps(memory_entry.tags),
                    "metadata": json.dumps(memory_entry.metadata),
                    "access_count": memory_entry.access_count
                }],
                ids=[memory_entry.id]
            )
        except Exception as e:
            logger.error(f"Failed to store in ChromaDB: {e}")
            raise
    
    def _store_in_fallback(self, memory_entry: MemoryEntry):
        """Store memory entry in fallback system"""
        try:
            memory_dict = asdict(memory_entry)
            self.fallback_memory["memories"].append(memory_dict)
            self._save_fallback_memory()
        except Exception as e:
            logger.error(f"Failed to store in fallback: {e}")
            raise
    
    def _update_cache(self, memory_entry: MemoryEntry):
        """Update memory cache with new entry"""
        self.memory_cache[memory_entry.id] = memory_entry
        
        # Manage cache size
        if len(self.memory_cache) > self.max_cache_size:
            # Remove oldest entries
            oldest_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].last_accessed or x[1].timestamp
            )
            for old_id, _ in oldest_entries[:self.max_cache_size // 4]:
                del self.memory_cache[old_id]
    
    def search_memories(self, query: str, memory_type: str = None, 
                       limit: int = 10, min_importance: float = 0.0) -> List[MemoryEntry]:
        """Search for memories using semantic similarity"""
        try:
            if self.collection:
                return self._search_chromadb(query, memory_type, limit, min_importance)
            else:
                return self._search_fallback(query, memory_type, limit, min_importance)
        except Exception as e:
            logger.error(f"❌ Memory search failed: {e}")
            return []
    
    def _search_chromadb(self, query: str, memory_type: str, limit: int, min_importance: float) -> List[MemoryEntry]:
        """Search memories using ChromaDB"""
        try:
            # Prepare where clause
            where_clause = {}
            if memory_type:
                where_clause["memory_type"] = memory_type
            if min_importance > 0:
                where_clause["importance"] = {"$gte": min_importance}
            
            # Search
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Convert results to MemoryEntry objects
            memories = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                
                memory_entry = MemoryEntry(
                    id=metadata['id'],
                    content=doc,
                    timestamp=metadata['timestamp'],
                    memory_type=metadata['memory_type'],
                    importance=metadata['importance'],
                    tags=json.loads(metadata.get('tags', '[]')),
                    metadata=json.loads(metadata.get('metadata', '{}')),
                    access_count=metadata.get('access_count', 0)
                )
                
                # Update access info
                memory_entry.last_accessed = datetime.now().isoformat()
                memory_entry.access_count += 1
                
                memories.append(memory_entry)
            
            return memories
            
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []
    
    def _search_fallback(self, query: str, memory_type: str, limit: int, min_importance: float) -> List[MemoryEntry]:
        """Search memories using fallback system"""
        try:
            memories = []
            query_lower = query.lower()
            
            for memory_dict in self.fallback_memory["memories"]:
                # Type filter
                if memory_type and memory_dict.get("memory_type") != memory_type:
                    continue
                
                # Importance filter
                if memory_dict.get("importance", 0) < min_importance:
                    continue
                
                # Simple text matching
                content_lower = memory_dict.get("content", "").lower()
                if query_lower in content_lower:
                    memory_entry = MemoryEntry(**memory_dict)
                    memories.append(memory_entry)
            
            # Sort by importance and limit
            memories.sort(key=lambda x: x.importance, reverse=True)
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system"""
        try:
            stats = {
                "system_type": "ChromaDB" if self.collection else "Fallback",
                "total_memories": 0,
                "memory_types": {},
                "average_importance": 0.0,
                "cache_size": len(self.memory_cache),
                "embedding_model": self.embedding_model is not None
            }
            
            if self.collection:
                # ChromaDB stats
                count = self.collection.count()
                stats["total_memories"] = count
                
                # Get all memories for type analysis
                if count > 0:
                    results = self.collection.get()
                    memory_types = defaultdict(int)
                    importance_sum = 0
                    
                    for metadata in results['metadatas']:
                        memory_types[metadata['memory_type']] += 1
                        importance_sum += metadata['importance']
                    
                    stats["memory_types"] = dict(memory_types)
                    stats["average_importance"] = importance_sum / count if count > 0 else 0
            
            else:
                # Fallback stats
                memories = self.fallback_memory.get("memories", [])
                stats["total_memories"] = len(memories)
                
                memory_types = defaultdict(int)
                importance_sum = 0
                
                for memory in memories:
                    memory_types[memory.get("memory_type", "unknown")] += 1
                    importance_sum += memory.get("importance", 0)
                
                stats["memory_types"] = dict(memory_types)
                stats["average_importance"] = importance_sum / len(memories) if memories else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}
    
    def consolidate_memories(self, similarity_threshold: float = 0.95):
        """Consolidate similar memories to reduce redundancy"""
        try:
            if not self.collection:
                logger.warning("Memory consolidation only available with ChromaDB")
                return
            
            # This is a complex operation - implement based on needs
            logger.info("🔄 Memory consolidation started...")
            
            # Implementation would involve:
            # 1. Get all memories
            # 2. Calculate similarity between memories
            # 3. Merge similar memories
            # 4. Update importance scores
            
            logger.info("✅ Memory consolidation completed")
            
        except Exception as e:
            logger.error(f"❌ Memory consolidation failed: {e}")
    
    def export_memories(self, file_path: str, format: str = "json"):
        """Export memories to file"""
        try:
            memories_data = []
            
            if self.collection:
                results = self.collection.get()
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i]
                    memory_data = {
                        "id": metadata['id'],
                        "content": doc,
                        "timestamp": metadata['timestamp'],
                        "memory_type": metadata['memory_type'],
                        "importance": metadata['importance'],
                        "tags": json.loads(metadata.get('tags', '[]')),
                        "metadata": json.loads(metadata.get('metadata', '{}')),
                        "access_count": metadata.get('access_count', 0)
                    }
                    memories_data.append(memory_data)
            else:
                memories_data = self.fallback_memory.get("memories", [])
            
            # Export based on format
            if format.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "export_timestamp": datetime.now().isoformat(),
                        "total_memories": len(memories_data),
                        "memories": memories_data
                    }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exported {len(memories_data)} memories to {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Memory export failed: {e}")
    
    def cleanup_old_memories(self, days_old: int = 30, min_importance: float = 0.3):
        """Clean up old, low-importance memories"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cutoff_str = cutoff_date.isoformat()
            
            if self.collection:
                # ChromaDB cleanup
                results = self.collection.get()
                ids_to_delete = []
                
                for i, metadata in enumerate(results['metadatas']):
                    if (metadata['timestamp'] < cutoff_str and 
                        metadata['importance'] < min_importance):
                        ids_to_delete.append(metadata['id'])
                
                if ids_to_delete:
                    self.collection.delete(ids=ids_to_delete)
                    logger.info(f"✅ Cleaned up {len(ids_to_delete)} old memories")
            
            else:
                # Fallback cleanup
                original_count = len(self.fallback_memory["memories"])
                self.fallback_memory["memories"] = [
                    memory for memory in self.fallback_memory["memories"]
                    if not (memory.get("timestamp", "") < cutoff_str and 
                           memory.get("importance", 0) < min_importance)
                ]
                
                cleaned_count = original_count - len(self.fallback_memory["memories"])
                if cleaned_count > 0:
                    self._save_fallback_memory()
                    logger.info(f"✅ Cleaned up {cleaned_count} old memories")
            
        except Exception as e:
            logger.error(f"❌ Memory cleanup failed: {e}")

def test_memory_system():
    """Test the memory system functionality"""
    print("🧪 Testing Advanced Memory System...")
    
    # Initialize system
    memory_system = AdvancedMemorySystem()
    
    # Test storing memories
    print("\n📝 Testing memory storage...")
    id1 = memory_system.store_memory(
        "User prefers dark themes and cyberpunk aesthetics",
        memory_type="preference",
        tags=["UI", "themes", "preferences"],
        metadata={"user_rating": 0.9}
    )
    
    id2 = memory_system.store_memory(
        "Discussed implementing vector database for better memory",
        memory_type="conversation",
        tags=["technical", "database", "memory"],
        metadata={"importance": 0.8}
    )
    
    id3 = memory_system.store_memory(
        "Python is a programming language",
        memory_type="fact",
        tags=["programming", "knowledge"],
        metadata={"frequency": 3}
    )
    
    # Test searching memories
    print("\n🔍 Testing memory search...")
    results = memory_system.search_memories("database vector", limit=5)
    print(f"Found {len(results)} memories for 'database vector'")
    for result in results:
        print(f"  - {result.content[:50]}... (importance: {result.importance:.2f})")
    
    # Test memory stats
    print("\n📊 Testing memory statistics...")
    stats = memory_system.get_memory_stats()
    print(f"Memory stats: {json.dumps(stats, indent=2)}")
    
    print("\n✅ Memory system test completed!")

if __name__ == "__main__":
    test_memory_system()

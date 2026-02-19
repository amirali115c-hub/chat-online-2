"""
Elasticsearch Client for ClawForge Conversation Logging
Based on NVIDIA Data Flywheel implementation
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from elasticsearch import Elasticsearch

# Configuration
ES_URL = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
ES_INDEX = os.environ.get("ES_COLLECTION_NAME", "clawforge")
ES_TIMEOUT = 30


class ConversationLogger:
    """
    Logs ClawForge conversations to Elasticsearch.
    Based on NVIDIA Data Flywheel logging schema.
    """
    
    def __init__(self, es_url: str = None, index: str = None):
        self.es_url = es_url or ES_URL
        self.index = index or ES_INDEX
        self.client = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to Elasticsearch."""
        try:
            self.client = Elasticsearch(hosts=[self.es_url], timeout=ES_TIMEOUT)
            # Check connection
            if self.client.ping():
                self._connected = True
                # Ensure index exists
                self._ensure_index()
                return True
        except Exception as e:
            print(f"[Elasticsearch] Connection failed: {e}")
        return False
    
    def _ensure_index(self):
        """Create index if it doesn't exist."""
        try:
            if not self.client.indices.exists(index=self.index):
                mapping = {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "long"},
                            "conversation_id": {"type": "keyword"},
                            "workload_id": {"type": "keyword"},
                            "client_id": {"type": "keyword"},
                            "request": {"type": "object"},
                            "response": {"type": "object"},
                            "model": {"type": "keyword"},
                            "tokens": {"type": "integer"},
                            "duration_ms": {"type": "integer"},
                            "session_id": {"type": "keyword"},
                            "user_id": {"type": "keyword"}
                        }
                    }
                }
                self.client.indices.create(index=self.index, body=mapping)
                print(f"[Elasticsearch] Created index: {self.index}")
        except Exception as e:
            print(f"[Elasticsearch] Index creation: {e}")
    
    def log_conversation(
        self,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        model: str = "qwen2.5:3b",
        workload_id: str = "general_chat",
        client_id: str = "clawforge",
        session_id: str = None,
        user_id: str = "default",
        tokens: int = None,
        duration_ms: int = None,
        request_params: Dict = None,
        response_data: Dict = None
    ) -> Optional[str]:
        """
        Log a conversation to Elasticsearch.
        
        Args:
            conversation_id: Unique ID for this conversation
            user_message: The user's message
            assistant_response: The AI's response
            model: Model used
            workload_id: Type of workload (general_chat, coding, etc.)
            client_id: Client identifier
            session_id: Session ID
            user_id: User identifier
            tokens: Number of tokens used
            duration_ms: Response time in milliseconds
            request_params: Request parameters
            response_data: Full response data
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self._connected:
            if not self.connect():
                return None
        
        try:
            # Build document (following NVIDIA Data Flywheel schema)
            doc = {
                "timestamp": int(datetime.utcnow().timestamp()),
                "conversation_id": conversation_id,
                "workload_id": workload_id,
                "client_id": client_id,
                "session_id": session_id or "default",
                "user_id": user_id,
                "request": {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": user_message}
                    ],
                    **(request_params or {})
                },
                "response": {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": assistant_response
                            }
                        }
                    ],
                    **(response_data or {})
                },
                "model": model,
                "tokens": tokens or 0,
                "duration_ms": duration_ms or 0
            }
            
            # Index document
            result = self.client.index(
                index=self.index,
                document=doc,
                id=conversation_id
            )
            
            return result.get("_id")
            
        except Exception as e:
            print(f"[Elasticsearch] Log failed: {e}")
            return None
    
    def log_chat_message(
        self,
        conversation_id: str,
        role: str,  # "user" or "assistant"
        content: str,
        workload_id: str = "general_chat",
        client_id: str = "clawforge",
        session_id: str = None,
        model: str = "qwen2.5:3b"
    ) -> Optional[str]:
        """
        Log a single chat message.
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant)
            content: Message content
            workload_id: Type of workload
            client_id: Client identifier
            session_id: Session ID
            model: Model used
            
        Returns:
            Document ID if successful
        """
        if not self._connected:
            if not self.connect():
                return None
        
        try:
            doc = {
                "timestamp": int(datetime.utcnow().timestamp()),
                "conversation_id": conversation_id,
                "workload_id": workload_id,
                "client_id": client_id,
                "session_id": session_id or "default",
                "role": role,
                "content": content,
                "model": model
            }
            
            result = self.client.index(
                index=self.index,
                document=doc
            )
            
            return result.get("_id")
            
        except Exception as e:
            print(f"[Elasticsearch] Log message failed: {e}")
            return None
    
    def search_conversations(
        self,
        query: str = None,
        workload_id: str = None,
        client_id: str = None,
        session_id: str = None,
        start_time: int = None,
        end_time: int = None,
        size: int = 100
    ) -> List[Dict]:
        """
        Search conversations with filters.
        
        Args:
            query: Full-text search query
            workload_id: Filter by workload type
            client_id: Filter by client
            session_id: Filter by session
            start_time: Unix timestamp start
            end_time: Unix timestamp end
            size: Number of results
            
        Returns:
            List of matching documents
        """
        if not self._connected:
            if not self.connect():
                return []
        
        try:
            # Build query
            must = []
            should = []
            
            if query:
                must.append({"match": {"content": query}})
            if workload_id:
                must.append({"term": {"workload_id": workload_id}})
            if client_id:
                must.append({"term": {"client_id": client_id}})
            if session_id:
                must.append({"term": {"session_id": session_id}})
            if start_time or end_time:
                range_filter = {"range": {"timestamp": {}}}
                if start_time:
                    range_filter["range"]["timestamp"]["gte"] = start_time
                if end_time:
                    range_filter["range"]["timestamp"]["lte"] = end_time
                must.append(range_filter)
            
            body = {
                "query": {
                    "bool": {
                        "must": must if must else [{"match_all": {}}]
                    }
                },
                "size": size,
                "sort": [{"timestamp": "desc"}]
            }
            
            result = self.client.search(index=self.index, body=body)
            return [hit["_source"] for hit in result["hits"]["hits"]]
            
        except Exception as e:
            print(f"[Elasticsearch] Search failed: {e}")
            return []
    
    def get_conversation_stats(
        self,
        workload_id: str = None,
        client_id: str = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Get statistics about logged conversations.
        """
        if not self._connected:
            if not self.connect():
                return {}
        
        try:
            # Build aggregation query
            must = []
            if workload_id:
                must.append({"term": {"workload_id": workload_id}})
            if client_id:
                must.append({"term": {"client_id": client_id}})
            if session_id:
                must.append({"term": {"session_id": session_id}})
            
            body = {
                "query": {
                    "bool": {
                        "must": must if must else [{"match_all": {}}]
                    }
                },
                "size": 0,
                "aggs": {
                    "total_conversations": {"value_count": {"field": "conversation_id"}},
                    "total_messages": {"value_count": {"field": "timestamp"}},
                    "total_tokens": {"sum": {"field": "tokens"}},
                    "avg_duration": {"avg": {"field": "duration_ms"}},
                    "by_workload": {
                        "terms": {"field": "workload_id"},
                        "aggs": {
                            "count": {"value_count": {"field": "conversation_id"}}
                        }
                    },
                    "by_model": {
                        "terms": {"field": "model"},
                        "aggs": {
                            "count": {"value_count": {"field": "conversation_id"}}
                        }
                    }
                }
            }
            
            result = self.client.search(index=self.index, body=body)
            aggs = result["aggregations"]
            
            return {
                "total_conversations": aggs["total_conversations"]["value"],
                "total_messages": aggs["total_messages"]["value"],
                "total_tokens": aggs["total_tokens"]["value"],
                "avg_duration_ms": aggs["avg_duration"]["value"],
                "by_workload": [
                    {"workload": b["key"], "count": b["doc_count"]}
                    for b in aggs["by_workload"]["buckets"]
                ],
                "by_model": [
                    {"model": b["key"], "count": b["doc_count"]}
                    for b in aggs["by_model"]["buckets"]
                ]
            }
            
        except Exception as e:
            print(f"[Elasticsearch] Stats failed: {e}")
            return {}
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by ID."""
        if not self._connected:
            if not self.connect():
                return False
        
        try:
            self.client.delete(index=self.index, id=conversation_id)
            return True
        except Exception as e:
            print(f"[Elasticsearch] Delete failed: {e}")
            return False
    
    def close(self):
        """Close the Elasticsearch connection."""
        if self.client:
            self.client.close()
            self._connected = False


# Convenience function
def get_logger() -> ConversationLogger:
    """Get a conversation logger instance."""
    return ConversationLogger()

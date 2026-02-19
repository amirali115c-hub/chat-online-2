"""
MemoryManager - Persistent Memory for Personal AI Agent
=====================================================
Handles SQLite-based persistent memory with auto-summarization.
FREE: Uses SQLite (no paid database required)
"""

import os
import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List, Dict
import threading


class MemoryManager:
    """
    Persistent memory system using SQLite.
    
    Features:
    - Session management
    - Turn storage with auto-summarization
    - Long-term fact store
    - Keyword search over history
    - Thread-safe operations
    """
    
    DB_PATH: Path = Path("./data/memory.db")
    MAX_CONTEXT_TURNS: int = 20
    SUMMARY_TRIGGER: int = 15
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize MemoryManager with SQLite database."""
        if db_path:
            self.DB_PATH = db_path
        
        # Create data directory if needed
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread-safe connection
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(str(self.DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Initialize database
        self._init_db()
    
    def _init_db(self) -> None:
        """Create database tables if they don't exist."""
        with self._lock:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    created TEXT,
                    summary TEXT,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    tokens_est INTEGER,
                    metadata TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                );
                
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    updated TEXT,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT,
                    content TEXT,
                    category TEXT,
                    importance INTEGER DEFAULT 5,
                    created TEXT,
                    updated TEXT,
                    metadata TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id);
                CREATE INDEX IF NOT EXISTS idx_facts_key ON facts(key);
                CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
            """)
            self.conn.commit()
    
    # ==================== SESSION MANAGEMENT ====================
    
    def new_session(self, name: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
        """Create a new conversation session."""
        name = name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self._lock:
            cursor = self.conn.execute(
                "INSERT INTO sessions (name, created, summary, metadata) VALUES (?, ?, ?, ?)",
                (name, datetime.now().isoformat(), "", metadata_json)
            )
            self.conn.commit()
            return cursor.lastrowid
    
    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent sessions."""
        with self._lock:
            rows = self.conn.execute(
                "SELECT id, name, created, summary, metadata FROM sessions ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
            
            return [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "created": r["created"],
                    "summary": r["summary"] or "",
                    "metadata": json.loads(r["metadata"]) if r["metadata"] else None
                }
                for r in rows
            ]
    
    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific session."""
        with self._lock:
            row = self.conn.execute(
                "SELECT id, name, created, summary, metadata FROM sessions WHERE id = ?",
                (session_id,)
            ).fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "created": row["created"],
                    "summary": row["summary"] or "",
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None
                }
            return None
    
    # ==================== TURN STORAGE ====================
    
    def save_turn(
        self,
        session_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Save a conversation turn.
        
        Args:
            session_id: Session to save to
            role: 'user' or 'assistant'
            content: The message content
            metadata: Optional additional data
            
        Returns:
            Turn ID
        """
        # Rough token estimate (4 chars per token)
        est = len(content) // 4
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self._lock:
            cursor = self.conn.execute(
                """INSERT INTO turns (session_id, role, content, timestamp, tokens_est, metadata)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (session_id, role, content, datetime.now().isoformat(), est, metadata_json)
            )
            self.conn.commit()
            return cursor.lastrowid
    
    def load_context(
        self,
        session_id: int,
        summarizer: Optional[callable] = None
    ) -> List[Dict[str, str]]:
        """
        Load conversation context with auto-summarization.
        
        Args:
            session_id: Session to load
            summarizer: Optional function to summarize old turns
            
        Returns:
            List of turns with roles and content
        """
        with self._lock:
            rows = self.conn.execute(
                "SELECT role, content, timestamp FROM turns WHERE session_id = ? ORDER BY id",
                (session_id,)
            ).fetchall()
        
        turns = [{"role": r["role"], "content": r["content"]} for r in rows]
        
        # Auto-summarize if too long
        if len(turns) > self.MAX_CONTEXT_TURNS:
            old = turns[:-self.SUMMARY_TRIGGER]
            recent = turns[-self.SUMMARY_TRIGGER:]
            
            if summarizer:
                summary_text = summarizer(old)
            else:
                # Simple default summary
                summary_text = f"[Earlier conversation - {len(old)} turns omitted]"
            
            # Save summary to session
            with self._lock:
                self.conn.execute(
                    "UPDATE sessions SET summary = ? WHERE id = ?",
                    (summary_text, session_id)
                )
                self.conn.commit()
            
            system_summary = {
                "role": "system",
                "content": f"Summary of earlier conversation:\n{summary_text}"
            }
            return [system_summary] + recent
        
        return turns
    
    def get_turns_count(self, session_id: int) -> int:
        """Get number of turns in a session."""
        with self._lock:
            return self.conn.execute(
                "SELECT COUNT(*) FROM turns WHERE session_id = ?",
                (session_id,)
            ).fetchone()[0]
    
    # ==================== FACT STORE ====================
    
    def remember_fact(
        self,
        key: str,
        value: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Store a long-term fact."""
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self._lock:
            self.conn.execute(
                """INSERT OR REPLACE INTO facts (key, value, updated, metadata)
                   VALUES (?, ?, ?, ?)""",
                (key, value, datetime.now().isoformat(), metadata_json)
            )
            self.conn.commit()
    
    def recall_fact(self, key: str) -> Optional[str]:
        """Retrieve a stored fact."""
        with self._lock:
            row = self.conn.execute(
                "SELECT value FROM facts WHERE key = ?",
                (key,)
            ).fetchone()
        
        return row["value"] if row else None
    
    def get_all_facts(self) -> Dict[str, str]:
        """Get all stored facts."""
        with self._lock:
            rows = self.conn.execute(
                "SELECT key, value FROM facts"
            ).fetchall()
        
        return {r["key"]: r["value"] for r in rows}
    
    def delete_fact(self, key: str) -> bool:
        """Delete a fact."""
        with self._lock:
            cursor = self.conn.execute(
                "DELETE FROM facts WHERE key = ?",
                (key,)
            )
            self.conn.commit()
        return cursor.rowcount > 0
    
    # ==================== MEMORIES ====================
    
    def add_memory(
        self,
        key: str,
        content: str,
        category: str = "general",
        importance: int = 5,
        metadata: Optional[Dict] = None
    ) -> int:
        """Add a categorized memory."""
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self._lock:
            cursor = self.conn.execute(
                """INSERT INTO memories (key, content, category, importance, created, updated, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (key, content, category, importance, datetime.now().isoformat(), datetime.now().isoformat(), metadata_json)
            )
            self.conn.commit()
            return cursor.lastrowid
    
    def get_memories(
        self,
        category: Optional[str] = None,
        min_importance: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get memories by category and importance."""
        query = "SELECT * FROM memories WHERE importance >= ?"
        params = [min_importance]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY importance DESC, created DESC LIMIT ?"
        params.append(limit)
        
        with self._lock:
            rows = self.conn.execute(query, params).fetchall()
        
        return [
            {
                "id": r["id"],
                "key": r["key"],
                "content": r["content"],
                "category": r["category"],
                "importance": r["importance"],
                "created": r["created"],
                "metadata": json.loads(r["metadata"]) if r["metadata"] else None
            }
            for r in rows
        ]
    
    # ==================== SEARCH ====================
    
    def search_history(
        self,
        query: str,
        session_id: Optional[int] = None,
        limit: int = 10
    ) -> List[str]:
        """Keyword search over stored turns."""
        words = query.lower().split()[:5]  # Limit to 5 words
        pattern = "%" + "%".join(words) + "%"
        
        if session_id:
            with self._lock:
                rows = self.conn.execute(
                    """SELECT content FROM turns
                       WHERE lower(content) LIKE ? AND session_id = ?
                       ORDER BY id DESC LIMIT ?""",
                    (pattern, session_id, limit)
                ).fetchall()
        else:
            with self._lock:
                rows = self.conn.execute(
                    """SELECT content FROM turns
                       WHERE lower(content) LIKE ?
                       ORDER BY id DESC LIMIT ?""",
                    (pattern, limit)
                ).fetchall()
        
        return [r["content"] for r in rows]
    
    def semantic_search(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Basic semantic-like search using keyword matching.
        For true semantic search, integrate with sentence-transformers.
        """
        words = query.lower().split()
        results = []
        
        with self._lock:
            # Search in memories
            for row in self.conn.execute("SELECT * FROM memories ORDER BY importance DESC"):
                content_lower = row["content"].lower()
                matches = sum(1 for w in words if w in content_lower)
                if matches > 0:
                    results.append({
                        "source": "memory",
                        "key": row["key"],
                        "content": row["content"],
                        "category": row["category"],
                        "score": matches / len(words)
                    })
            
            # Search in facts
            for row in self.conn.execute("SELECT * FROM facts"):
                value_lower = row["value"].lower()
                matches = sum(1 for w in words if w in value_lower)
                if matches > 0:
                    results.append({
                        "source": "fact",
                        "key": row["key"],
                        "content": row["value"],
                        "score": matches / len(words)
                    })
        
        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    # ==================== UTILITIES ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        with self._lock:
            return {
                "total_sessions": self.conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
                "total_turns": self.conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0],
                "total_facts": self.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0],
                "total_memories": self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0],
                "db_size_mb": round(self.DB_PATH.stat().st_size / (1024 * 1024), 2) if self.DB_PATH.exists() else 0
            }
    
    def clear_session(self, session_id: int, keep_facts: bool = True) -> None:
        """Clear a session's turns."""
        with self._lock:
            self.conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
            self.conn.execute("UPDATE sessions SET summary = '' WHERE id = ?", (session_id,))
            self.conn.commit()
    
    def export_session(self, session_id: int) -> Dict[str, Any]:
        """Export a session to JSON."""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        with self._lock:
            turns = self.conn.execute(
                "SELECT role, content, timestamp FROM turns WHERE session_id = ? ORDER BY id",
                (session_id,)
            ).fetchall()
        
        return {
            "session": session,
            "turns": [
                {"role": t["role"], "content": t["content"], "timestamp": t["timestamp"]}
                for t in turns
            ],
            "facts": self.get_all_facts(),
            "exported_at": datetime.now().isoformat()
        }
    
    def import_session(self, data: Dict[str, Any]) -> int:
        """Import a session from JSON."""
        # Create session
        session_id = self.new_session(
            name=data.get("session", {}).get("name", "Imported Session"),
            metadata=data.get("session", {}).get("metadata")
        )
        
        # Import turns
        for turn in data.get("turns", []):
            self.save_turn(
                session_id,
                turn["role"],
                turn["content"],
                {"imported": True, "original_timestamp": turn.get("timestamp")}
            )
        
        # Import facts
        for key, value in data.get("facts", {}).items():
            self.remember_fact(key, value, {"imported": True})
        
        return session_id
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# Example usage
if __name__ == "__main__":
    # Initialize
    memory = MemoryManager()
    
    # Create session
    session_id = memory.new_session("Test Session")
    print(f"Created session: {session_id}")
    
    # Save turns
    memory.save_turn(session_id, "user", "Hello, I'm looking for SEO tips.")
    memory.save_turn(session_id, "assistant", "I'd be happy to help! What specific SEO challenges are you facing?")
    
    # Load context
    context = memory.load_context(session_id)
    print(f"Loaded {len(context)} turns")
    
    # Remember facts
    memory.remember_fact("user_name", "John")
    memory.remember_fact("user_industry", "E-commerce")
    
    # Recall facts
    print(f"User: {memory.recall_fact('user_name')}")
    print(f"Industry: {memory.recall_fact('user_industry')}")
    
    # Get stats
    stats = memory.get_stats()
    print(f"Stats: {stats}")
    
    # Close
    memory.close()

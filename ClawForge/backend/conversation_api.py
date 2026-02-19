"""
Conversation Logging API Endpoints for ClawForge
Based on NVIDIA Data Flywheel patterns
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# In-memory conversation storage (can be replaced with database)
_conversations = {}
_workloads = ["general_chat", "coding", "writing", "analysis", "qa", "creative"]


# ============================================================================
# Request/Response Models
# ============================================================================

class LogConversationRequest(BaseModel):
    """Request model for logging a conversation."""
    user_message: str
    assistant_response: str
    model: str = "qwen2.5:3b"
    workload_id: str = "general_chat"
    client_id: str = "clawforge"
    session_id: Optional[str] = None
    user_id: str = "default"
    tokens: Optional[int] = None
    duration_ms: Optional[int] = None
    metadata: Optional[dict] = None


class LogMessageRequest(BaseModel):
    """Request model for logging a single message."""
    conversation_id: str
    role: str  # "user" or "assistant"
    content: str
    workload_id: str = "general_chat"
    client_id: str = "clawforge"
    session_id: Optional[str] = None
    model: str = "qwen2.5:3b"


class ConversationResponse(BaseModel):
    """Response model for conversation operations."""
    status: str
    conversation_id: str
    message: str = ""


class ConversationsListResponse(BaseModel):
    """Response model for listing conversations."""
    status: str
    conversations: list
    total: int


class StatsResponse(BaseModel):
    """Response model for statistics."""
    status: str
    stats: dict


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/api/conversations/log")
async def log_conversation(request: LogConversationRequest):
    """
    Log a complete conversation (user message + assistant response).
    
    Creates a new conversation or appends to existing one.
    """
    from conversation_logger import get_logger
    
    try:
        logger = get_logger()
        
        # Generate conversation ID if not exists
        conversation_id = str(uuid.uuid4())
        
        # Log to Elasticsearch
        doc_id = logger.log_conversation(
            conversation_id=conversation_id,
            user_message=request.user_message,
            assistant_response=request.assistant_response,
            model=request.model,
            workload_id=request.workload_id,
            client_id=request.client_id,
            session_id=request.session_id,
            user_id=request.user_id,
            tokens=request.tokens,
            duration_ms=request.duration_ms,
            request_params=request.metadata,
            response_data=None
        )
        
        if doc_id:
            # Also store in local memory for quick access
            if conversation_id not in _conversations:
                _conversations[conversation_id] = {
                    "id": conversation_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "messages": [],
                    "workload_id": request.workload_id,
                    "client_id": request.client_id,
                    "model": request.model
                }
            
            _conversations[conversation_id]["messages"].append({
                "role": "user",
                "content": request.user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            _conversations[conversation_id]["messages"].append({
                "role": "assistant", 
                "content": request.assistant_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return ConversationResponse(
                status="success",
                conversation_id=conversation_id,
                message="Conversation logged successfully"
            )
        else:
            # Fallback to local storage
            conversation_id = str(uuid.uuid4())
            _conversations[conversation_id] = {
                "id": conversation_id,
                "created_at": datetime.utcnow().isoformat(),
                "messages": [
                    {
                        "role": "user",
                        "content": request.user_message,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    {
                        "role": "assistant",
                        "content": request.assistant_response,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ],
                "workload_id": request.workload_id,
                "client_id": request.client_id,
                "model": request.model
            }
            
            return ConversationResponse(
                status="success_local",
                conversation_id=conversation_id,
                message="Conversation logged (local storage)"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/conversations/message")
async def log_message(request: LogMessageRequest):
    """
    Log a single message to an existing conversation.
    """
    from conversation_logger import get_logger
    
    try:
        logger = get_logger()
        
        # Log to Elasticsearch
        doc_id = logger.log_chat_message(
            conversation_id=request.conversation_id,
            role=request.role,
            content=request.content,
            workload_id=request.workload_id,
            client_id=request.client_id,
            session_id=request.session_id,
            model=request.model
        )
        
        # Also update local storage
        if request.conversation_id in _conversations:
            _conversations[request.conversation_id]["messages"].append({
                "role": request.role,
                "content": request.content,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return ConversationResponse(
            status="success" if doc_id else "success_local",
            conversation_id=request.conversation_id,
            message="Message logged"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/conversations")
async def list_conversations(
    workload_id: str = None,
    client_id: str = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List all conversations with optional filters.
    """
    try:
        filtered = []
        
        for conv_id, conv in _conversations.items():
            if workload_id and conv.get("workload_id") != workload_id:
                continue
            if client_id and conv.get("client_id") != client_id:
                continue
            filtered.append(conv)
        
        # Sort by creation time (newest first)
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return ConversationsListResponse(
            status="success",
            conversations=filtered[offset:offset+limit],
            total=len(filtered)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation by ID.
    """
    try:
        if conversation_id not in _conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "status": "success",
            "conversation": _conversations[conversation_id]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation.
    """
    from conversation_logger import get_logger
    
    try:
        logger = get_logger()
        logger.delete_conversation(conversation_id)
        
        if conversation_id in _conversations:
            del _conversations[conversation_id]
        
        return {
            "status": "success",
            "message": f"Conversation {conversation_id} deleted"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/conversations/stats")
async def get_conversation_stats():
    """
    Get statistics about logged conversations.
    """
    from conversation_logger import get_logger
    
    try:
        logger = get_logger()
        es_stats = logger.get_conversation_stats()
        
        # Also calculate local stats
        local_stats = {
            "total_conversations": len(_conversations),
            "total_messages": sum(
                len(conv.get("messages", []))
                for conv in _conversations.values()
            ),
            "by_workload": {},
            "by_model": {}
        }
        
        for conv in _conversations.values():
            workload = conv.get("workload_id", "unknown")
            model = conv.get("model", "unknown")
            local_stats["by_workload"][workload] = local_stats["by_workload"].get(workload, 0) + 1
            local_stats["by_model"][model] = local_stats["by_model"].get(model, 0) + 1
        
        return StatsResponse(
            status="success",
            stats={
                "elasticsearch": es_stats,
                "local": local_stats,
                "workloads_available": _workloads
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/conversations/search")
async def search_conversations(
    query: str = None,
    workload_id: str = None,
    session_id: str = None,
    start_time: int = None,
    end_time: int = None,
    limit: int = 50
):
    """
    Search conversations with filters.
    """
    from conversation_logger import get_logger
    
    try:
        logger = get_logger()
        results = logger.search_conversations(
            query=query,
            workload_id=workload_id,
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            size=limit
        )
        
        return {
            "status": "success",
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/conversations/workloads")
async def get_available_workloads():
    """
    Get list of available workload types.
    """
    return {
        "status": "success",
        "workloads": _workloads
    }

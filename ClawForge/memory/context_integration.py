"""
ClawForge Context Integration
============================
Auto-integrates context manager into ClawForge API.
Loads conversation continuity on startup.
"""

import sys
from pathlib import Path

# Add memory module to path
MEMORY_DIR = Path(__file__).parent.parent / "memory"
if str(MEMORY_DIR) not in sys.path:
    sys.path.insert(0, str(MEMORY_DIR))


def init_context_system():
    """
    Initialize context system on ClawForge startup.
    Call this from your main.py or api.py startup.
    """
    try:
        from context_manager import get_context_manager
        
        # Get singleton instance (loads state from disk)
        ctx = get_context_manager()
        
        # Check if there's a previous session to resume
        context = ctx.get_context()
        
        if context.get("conversation_id"):
            print(f"\n📋 Found previous session: {context['conversation_id']}")
            print(ctx.get_resume_context())
        
        return ctx
        
    except Exception as e:
        print(f"Warning: Could not initialize context system: {e}")
        return None


def add_context_routes(app):
    """Add context API routes to FastAPI app."""
    try:
        from context_api import router as context_router
        
        # Include context routes
        app.include_router(context_router)
        
        print("   Context API routes: /context/*")
        
    except Exception as e:
        print(f"Warning: Could not add context routes: {e}")


# Auto-initialize when imported
_context_instance = None

def get_clawforge_context():
    """Get the initialized context instance."""
    global _context_instance
    if _context_instance is None:
        _context_instance = init_context_system()
    return _context_instance


# Example usage in api.py:
"""
# Add to your lifespan or startup:
from memory.context_integration import init_context_system, add_context_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    global task_manager
    
    # Initialize task manager
    from task_manager import TaskManager
    task_manager = TaskManager(broadcast_fn=broadcast)
    
    # Initialize context system
    init_context_system()
    add_context_routes(app)
    
    yield
    print("ClawForge API stopped")
"""

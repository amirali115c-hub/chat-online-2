"""
Ollama Integration for ClawForge
Supports local LLM inference using Ollama
"""

import os
import requests
from typing import Optional, Dict, Any

# Ollama configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")  # Using smaller model for low-memory systems

class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL
        self.api_url = f"{self.base_url}/api"
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Ollama is running and model is available."""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": "Ollama not responding properly",
                    "available": False
                }
            
            # Check if our model is available
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            model_available = any(self.model in name for name in model_names)
            
            return {
                "status": "healthy" if model_available else "warning",
                "model": self.model,
                "model_available": model_available,
                "available": True,
                "all_models": model_names[:5]  # Return first 5 models
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Cannot connect to Ollama. Is it running?",
                "available": False
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "available": False
            }
    
    def chat(self, message: str, system_prompt: str = None, 
             temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Send a chat message to Ollama.
        
        Args:
            message: User message
            system_prompt: System prompt (optional)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dict with response, usage stats, etc.
        """
        try:
            # Build messages array
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            # Make request
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=120  # 2 minute timeout for generation
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Ollama API error: {response.status_code}",
                    "response": None
                }
            
            data = response.json()
            
            # Extract response
            assistant_message = data.get("message", {}).get("content", "")
            
            # Extract usage stats if available
            eval_count = data.get("eval_count", 0)
            prompt_eval_count = data.get("prompt_eval_count", 0)
            
            return {
                "status": "success",
                "response": assistant_message,
                "model": self.model,
                "usage": {
                    "prompt_tokens": prompt_eval_count,
                    "completion_tokens": eval_count,
                    "total_tokens": prompt_eval_count + eval_count
                },
                "done": data.get("done", True)
            }
            
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "Request timed out. Try a shorter message.",
                "response": None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response": None
            }
    
    def generate(self, prompt: str, system_prompt: str = None,
                 temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Generate text using the completions API (non-chat format).
        
        Args:
            prompt: Prompt text
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dict with generated text and stats
        """
        try:
            # Build prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Ollama API error: {response.status_code}"
                }
            
            data = response.json()
            
            return {
                "status": "success",
                "response": data.get("response", ""),
                "model": self.model,
                "done": data.get("done", True)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def pull_model(self, model: str = None) -> Dict[str, Any]:
        """
        Pull a model from Ollama registry.
        
        Args:
            model: Model name to pull (default: configured model)
        
        Returns:
            Dict with status
        """
        target_model = model or self.model
        
        try:
            response = requests.post(
                f"{self.api_url}/pull",
                json={"name": target_model},
                stream=True,
                timeout=600  # 10 minutes for download
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Failed to pull model: {response.status_code}"
                }
            
            # Stream the response for progress
            status = "pulling"
            total = None
            completed = 0
            
            for line in response.iter_lines():
                if line:
                    data = line.decode('utf-8')
                    # Parse status updates would go here
                    
            return {
                "status": "success",
                "message": f"Model {target_model} downloaded successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_models(self) -> list:
        """List all available models."""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=10)
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except Exception:
            return []
    
    def delete_model(self, model: str) -> Dict[str, Any]:
        """Delete a model from local storage."""
        try:
            response = requests.delete(
                f"{self.api_url}/delete",
                json={"name": model},
                timeout=30
            )
            
            if response.status_code == 200:
                return {"status": "success", "message": f"Model {model} deleted"}
            else:
                return {"status": "error", "error": "Failed to delete model"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Convenience function for quick health check
def check_ollama_status() -> Dict[str, Any]:
    """Quick check if Ollama is available."""
    client = OllamaClient()
    return client.health_check()


# Quick chat function
def ollama_chat(message: str, system_prompt: str = None) -> str:
    """
    Simple chat function for quick testing.
    
    Args:
        message: User message
        system_prompt: Optional system prompt
    
    Returns:
        AI response string or error message
    """
    client = OllamaClient()
    result = client.chat(message=message, system_prompt=system_prompt)
    
    if result["status"] == "success":
        return result["response"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"

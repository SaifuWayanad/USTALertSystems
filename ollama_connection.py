"""
Ollama Connection Module
Handles connection to Ollama and provides agent setup with Gemma model
"""

import requests
import json
from typing import Optional, Dict, Any


class OllamaConnection:
    """Manages connection to Ollama service and model interactions"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama connection
        
        Args:
            base_url: The base URL for Ollama service (default: localhost:11434)
        """
        self.base_url = base_url
        self.model = "gemma"
        self.is_connected = False
        
    def check_connection(self) -> bool:
        """
        Check if Ollama service is running
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            self.is_connected = response.status_code == 200
            return self.is_connected
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            self.is_connected = False
            return False
    
    def pull_model(self, model_name: str = "gemma") -> Dict[str, Any]:
        """
        Pull a model from Ollama repository
        
        Args:
            model_name: Name of the model to pull (default: gemma)
            
        Returns:
            dict: Response from Ollama API
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=300
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    print(f"Pulling {model_name}: {data.get('status', '')}")
            
            return {"success": True, "model": model_name}
        except Exception as e:
            print(f"Error pulling model: {e}")
            return {"success": False, "error": str(e)}
    
    def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Generate response from Ollama model
        
        Args:
            prompt: Input prompt for the model
            model: Model to use (default: self.model)
            **kwargs: Additional parameters for the model
            
        Returns:
            str: Generated response
        """
        model = model or self.model
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error generating response: {e}"
    
    def chat(self, messages: list, model: Optional[str] = None, **kwargs) -> str:
        """
        Chat with Ollama model using conversation format
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (default: self.model)
            **kwargs: Additional parameters for the model
            
        Returns:
            str: Generated response
        """
        model = model or self.model
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    **kwargs
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error in chat: {e}"
    
    def list_models(self) -> Dict[str, Any]:
        """
        List all available models in Ollama
        
        Returns:
            dict: Available models information
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}


class OllamaAgent:
    """Agent that uses Ollama with Gemma model for intelligent interactions"""
    
    def __init__(self, ollama_connection: OllamaConnection, model: str = "gemma"):
        """
        Initialize Ollama Agent
        
        Args:
            ollama_connection: OllamaConnection instance
            model: Model to use for the agent
        """
        self.connection = ollama_connection
        self.model = model
        self.conversation_history = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
    
    def process(self, user_input: str, system_prompt: Optional[str] = None) -> str:
        """
        Process user input and generate response
        
        Args:
            user_input: User's input message
            system_prompt: Optional system prompt for context
            
        Returns:
            str: Agent's response
        """
        self.add_message("user", user_input)
        
        messages = self.conversation_history.copy()
        
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        response = self.connection.chat(messages, model=self.model)
        
        self.add_message("assistant", response)
        
        return response
    
    def reset_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []


# Example usage
if __name__ == "__main__":
    # Initialize connection
    ollama = OllamaConnection()
    
    # Check connection
    if ollama.check_connection():
        print("✓ Connected to Ollama")
    else:
        print("✗ Failed to connect to Ollama. Make sure Ollama is running.")
        exit(1)
    
    # List available models
    models = ollama.list_models()
    print(f"Available models: {models}")
    
    # Ensure Gemma is available
    print("\nPulling Gemma model...")
    pull_result = ollama.pull_model("gemma")
    print(f"Pull result: {pull_result}")
    
    # Create agent
    agent = OllamaAgent(ollama)
    
    # Simple interaction
    print("\n--- Agent Interaction ---")
    response = agent.process("Hello! What can you help me with?")
    print(f"Agent: {response}")

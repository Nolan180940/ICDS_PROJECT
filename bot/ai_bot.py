"""
AI Chat Bot with LLM Integration.

Features:
- Context-aware conversations using message history
- Configurable persona via system prompts
- Ollama integration (phi3-mini model)
- OpenAI-compatible API fallback
- Image generation simulation (/aipic command)
"""

import json
import requests
from typing import Optional, List, Dict

import config.settings as cfg


class AIBot:
    """AI-powered chatbot with context memory and persona support."""
    
    def __init__(
        self,
        name: str = "Bot",
        model: str = cfg.OLLAMA_MODEL,
        host: str = cfg.OLLAMA_HOST,
        persona: str = "helpful"
    ):
        self.name = name
        self.model = model
        self.host = host
        self.persona = persona
        
        # Message history for context
        self.message_history: List[Dict[str, str]] = []
        self.max_history_length = 20  # Keep last 20 messages for context
        
        # Persona definitions
        self.personas = {
            "helpful": "You are a helpful, friendly assistant. Be concise and warm in your responses.",
            "humorous": "You are a witty, humorous assistant. Add jokes and light-hearted comments to your responses.",
            "serious": "You are a professional, serious assistant. Be formal and precise in your responses.",
            "creative": "You are a creative, imaginative assistant. Think outside the box and provide unique perspectives.",
            "advisor": "You are an academic advisor at NYU Shanghai. Provide guidance on courses and programming."
        }
        
        # Check Ollama availability
        self.ollama_available = self._check_ollama()
        
        if not self.ollama_available:
            print(f"[BOT] Warning: Ollama not available at {host}. Using fallback responses.")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def set_persona(self, persona: str):
        """Set bot persona."""
        if persona in self.personas:
            self.persona = persona
            # Clear history when changing persona
            self.message_history = []
            return True
        return False
    
    def get_system_prompt(self) -> str:
        """Get system prompt based on current persona."""
        return self.personas.get(self.persona, self.personas["helpful"])
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and generate response.
        
        Args:
            user_message: User's input message
        
        Returns:
            Bot's response
        """
        # Handle special commands
        if user_message.startswith("/aipic"):
            return self._handle_image_generation(user_message)
        
        # Add user message to history
        self.message_history.append({"role": "user", "content": user_message})
        
        # Trim history if too long
        if len(self.message_history) > self.max_history_length:
            self.message_history = self.message_history[-self.max_history_length:]
        
        # Generate response
        if self.ollama_available:
            response = self._chat_with_ollama(user_message)
        else:
            response = self._fallback_response(user_message)
        
        # Add bot response to history
        self.message_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _chat_with_ollama(self, user_message: str) -> str:
        """Send message to Ollama and get response."""
        try:
            # Build messages with system prompt
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ] + self.message_history
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "I'm not sure how to respond.")
            else:
                return f"Error: API returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "Response timed out. Please try again."
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"
    
    def _fallback_response(self, user_message: str) -> str:
        """Generate simple fallback response when Ollama is unavailable."""
        msg_lower = user_message.lower()
        
        # Simple pattern matching
        if any(word in msg_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! I'm {self.name}, your {self.persona} assistant. How can I help?"
        elif any(word in msg_lower for word in ["how are you", "how're you"]):
            return "I'm doing well, thank you for asking! How about you?"
        elif any(word in msg_lower for word in ["name", "who are you"]):
            return f"I'm {self.name}, a chatbot with a {self.persona} personality."
        elif any(word in msg_lower for word in ["bye", "goodbye", "see you"]):
            return "Goodbye! Feel free to come back anytime!"
        elif "?" in user_message:
            return "That's an interesting question! When Ollama is running, I'll be able to give you a better answer."
        else:
            return f"I received your message: '{user_message}'. Start Ollama for more intelligent responses!"
    
    def _handle_image_generation(self, command: str) -> str:
        """
        Handle /aipic command for AI image generation.
        
        Since we may not have a real image generation API,
        this simulates the functionality with a placeholder.
        """
        # Extract description from command
        if ":" in command:
            description = command.split(":", 1)[1].strip()
        else:
            description = "a beautiful scene"
        
        # Log the request
        print(f"[BOT] Image generation requested: '{description}'")
        
        # Simulate image generation (placeholder)
        # In production, this would call DALL-E, Stable Diffusion, etc.
        response = (
            f"🎨 AI Image Generation Request:\n"
            f"Description: '{description}'\n\n"
            f"[Image would be generated here]\n\n"
            f"Note: To enable real image generation, configure an API key for:\n"
            f"- DALL-E API\n"
            f"- Stable Diffusion API\n"
            f"- Midjourney API\n\n"
            f"For now, imagine: A wonderful visualization of '{description}' ✨"
        )
        
        return response
    
    def clear_history(self):
        """Clear conversation history."""
        self.message_history = []
    
    def get_context_summary(self) -> str:
        """Get a brief summary of conversation context."""
        if not self.message_history:
            return "No conversation history."
        
        user_msgs = [m for m in self.message_history if m["role"] == "user"]
        return f"Context: {len(user_msgs)} user messages in history."


# Singleton instance
_bot_instance: Optional[AIBot] = None


def get_bot(persona: str = "helpful") -> AIBot:
    """Get singleton AIBot instance."""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = AIBot(persona=persona)
    return _bot_instance


def reset_bot():
    """Reset bot instance (useful for testing)."""
    global _bot_instance
    _bot_instance = None


if __name__ == "__main__":
    # Test the bot
    bot = AIBot(persona="humorous")
    
    print(f"Ollama Available: {bot.ollama_available}")
    print(f"Persona: {bot.persona}")
    print("-" * 50)
    
    test_messages = [
        "Hello!",
        "What's your name?",
        "Tell me a joke",
        "/aipic: a sunset over mountains"
    ]
    
    for msg in test_messages:
        print(f"\nUser: {msg}")
        response = bot.chat(msg)
        print(f"Bot: {response}")

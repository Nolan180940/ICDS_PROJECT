"""
Chat Summary Generator.

Provides functionality to summarize recent chat history using:
- LLM-based summarization (when Ollama is available)
- Fallback to simple extractive summarization
"""

import config.settings as cfg


class SummaryGenerator:
    """Generate summaries of chat history."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.max_history_for_summary = 10
    
    def generate(self, chat_history: list) -> str:
        """
        Generate summary of recent chat messages.
        
        Args:
            chat_history: List of message strings
        
        Returns:
            Summary text
        """
        if not chat_history:
            return "No chat history to summarize."
        
        # Get recent messages
        recent = chat_history[-self.max_history_for_summary:]
        
        if self.llm_client:
            try:
                return self._summarize_with_llm(recent)
            except Exception as e:
                print(f"[WARNING] LLM summarization failed: {e}, using fallback")
        
        return self._summarize_basic(recent)
    
    def _summarize_with_llm(self, messages: list) -> str:
        """Use LLM to generate intelligent summary."""
        chat_text = "\n".join(messages)
        
        prompt = f"""Please summarize the following chat conversation in 2-3 sentences. 
Focus on the main topics discussed and any important decisions or conclusions.

Chat History:
{chat_text}

Summary:"""
        
        if hasattr(self.llm_client, 'chat'):
            response = self.llm_client.chat(prompt)
            return f"📝 Chat Summary:\n{response}"
        elif hasattr(self.llm_client, 'generate_summary'):
            return self.llm_client.generate_summary(chat_text)
        else:
            raise ValueError("LLM client doesn't support chat method")
    
    def _summarize_basic(self, messages: list) -> str:
        """
        Basic extractive summarization (fallback).
        Returns first and last messages with count.
        """
        if len(messages) == 0:
            return "No messages to summarize."
        
        if len(messages) == 1:
            return f"📝 Recent activity:\n{messages[0]}"
        
        # Extract key info
        total_messages = len(messages)
        first_msg = messages[0][:100] + ("..." if len(messages[0]) > 100 else "")
        last_msg = messages[-1][:100] + ("..." if len(messages[-1]) > 100 else "")
        
        # Find unique participants
        participants = set()
        for msg in messages:
            if ':' in msg:
                parts = msg.split(':')
                if len(parts) > 0:
                    # Extract username from format like "(timestamp) username : message"
                    name_part = parts[0]
                    if ')' in name_part:
                        name = name_part.split(')')[-1].strip()
                        participants.add(name)
        
        summary_lines = [
            "📝 Chat Summary",
            f"• Total messages: {total_messages}",
            f"• Participants: {', '.join(participants) if participants else 'Unknown'}",
            f"• Started with: {first_msg}",
            f"• Latest: {last_msg}"
        ]
        
        return "\n".join(summary_lines)


def create_summary_from_list(messages: list, max_msgs: int = 10) -> str:
    """
    Convenience function to create summary from message list.
    
    Args:
        messages: List of message strings
        max_msgs: Maximum number of recent messages to include
    
    Returns:
        Summary string
    """
    generator = SummaryGenerator()
    generator.max_history_for_summary = max_msgs
    return generator.generate(messages)


if __name__ == "__main__":
    # Test the summary generator
    test_history = [
        "(12.04.25,10:00) Alice : Hello everyone!",
        "(12.04.25,10:01) Bob : Hi Alice! How are you?",
        "(12.04.25,10:02) Alice : I'm doing great, thanks for asking.",
        "(12.04.25,10:03) Charlie : Hey team! What's up?",
        "(12.04.25,10:04) Bob : Just working on the project.",
        "(12.04.25,10:05) Alice : Same here. The deadline is approaching.",
        "(12.04.25,10:06) Charlie : Let me know if you need help.",
        "(12.04.25,10:07) Alice : Thanks Charlie! That would be great.",
    ]
    
    generator = SummaryGenerator()
    summary = generator.generate(test_history)
    print("Generated Summary:")
    print("-" * 50)
    print(summary)

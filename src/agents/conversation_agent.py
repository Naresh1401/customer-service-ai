"""
Conversation Agent — Multi-turn RAG-powered conversation handler that maintains
context, retrieves from the knowledge base, follows company tone guidelines,
handles clarification, and knows when to say "I don't know".
"""

import os
import uuid
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

from src.knowledge.kb_loader import get_vectorstore, query_kb

load_dotenv()

SYSTEM_PROMPT = """You are a friendly, professional customer service agent for CloudSync Pro, \
a cloud collaboration and file synchronization platform.

## Tone & Style Guidelines
- Be warm, empathetic, and professional
- Use clear, concise language — avoid jargon unless the customer uses it first
- Address the customer by name if known
- Acknowledge their issue before providing a solution
- Be proactive: suggest related resources or next steps
- If you're unsure, say so honestly rather than guessing

## Response Rules
1. ALWAYS base your answers on the provided knowledge base context. If the context \
doesn't contain relevant information, say: "I don't have specific information about that \
in our documentation. Let me connect you with a specialist who can help."
2. For billing/account questions requiring access to the customer's account, tell them \
you'll need to verify their identity.
3. NEVER make up pricing, policies, or technical details not in the knowledge base.
4. If the customer seems frustrated, lead with empathy before the solution.
5. When providing multi-step instructions, use numbered lists.
6. End responses with a helpful follow-up question or confirmation.

## Knowledge Base Context
{context}
"""

# In-memory conversation store (replace with Redis/DB in production)
_conversations: dict[str, dict] = {}


class ConversationAgent:
    """Multi-turn conversation agent with RAG-powered responses."""

    def __init__(self, model_name: str | None = None):
        self.llm = ChatOpenAI(
            model=model_name or os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0.3,
        )

    def _get_or_create_conversation(self, conversation_id: str | None = None) -> tuple[str, dict]:
        """Get existing conversation or create a new one."""
        if conversation_id and conversation_id in _conversations:
            return conversation_id, _conversations[conversation_id]

        new_id = conversation_id or str(uuid.uuid4())
        _conversations[new_id] = {
            "id": new_id,
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "metadata": {},
        }
        return new_id, _conversations[new_id]

    def _retrieve_context(self, query: str, category: str | None = None) -> str:
        """Retrieve relevant context from the knowledge base."""
        results = query_kb(query, k=4, category=category)
        if not results:
            return "No relevant knowledge base articles found."

        context_parts = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("category", "General")
            context_parts.append(f"[Source: {source}]\n{doc.page_content}")

        return "\n\n---\n\n".join(context_parts)

    def _build_messages(self, conversation: dict, context: str) -> list:
        """Build the message list for the LLM call."""
        messages = [SystemMessage(content=SYSTEM_PROMPT.format(context=context))]

        for msg in conversation["messages"]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        return messages

    def chat(
        self,
        message: str,
        conversation_id: str | None = None,
        customer_name: str | None = None,
        category: str | None = None,
    ) -> dict:
        """Process a customer message and return a response with conversation context."""
        conv_id, conversation = self._get_or_create_conversation(conversation_id)

        if customer_name:
            conversation["metadata"]["customer_name"] = customer_name

        context = self._retrieve_context(message, category=category)

        conversation["messages"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
        })

        messages = self._build_messages(conversation, context)

        response = self.llm.invoke(messages)
        response_text = response.content

        conversation["messages"].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "conversation_id": conv_id,
            "response": response_text,
            "turn_count": len(conversation["messages"]) // 2,
            "sources_used": len(context.split("---")),
        }

    def get_conversation(self, conversation_id: str) -> dict | None:
        """Retrieve a conversation by ID."""
        return _conversations.get(conversation_id)

    def list_conversations(self) -> list[dict]:
        """List all conversations with summary info."""
        return [
            {
                "id": conv["id"],
                "created_at": conv["created_at"],
                "turn_count": len(conv["messages"]) // 2,
                "last_message": conv["messages"][-1]["content"][:100] if conv["messages"] else "",
            }
            for conv in _conversations.values()
        ]

    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation from memory."""
        if conversation_id in _conversations:
            del _conversations[conversation_id]
            return True
        return False

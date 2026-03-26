"""
Sentiment Analyzer — Real-time sentiment analysis that detects customer emotion,
adjusts response tone, triggers empathy responses, and tracks sentiment
trajectory across the conversation.
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

EMOTIONS = ["angry", "frustrated", "neutral", "satisfied", "happy"]

TONE_ADJUSTMENTS = {
    "angry": {
        "tone": "deeply empathetic and apologetic",
        "prefix": "I completely understand your frustration, and I sincerely apologize for this experience.",
        "approach": "acknowledge, apologize, resolve, follow-up",
    },
    "frustrated": {
        "tone": "warm, patient, and understanding",
        "prefix": "I understand this has been difficult, and I'm here to help resolve this for you.",
        "approach": "acknowledge, provide clear steps, offer alternatives",
    },
    "neutral": {
        "tone": "professional and helpful",
        "prefix": "",
        "approach": "direct, informative, efficient",
    },
    "satisfied": {
        "tone": "friendly and enthusiastic",
        "prefix": "",
        "approach": "maintain positive experience, suggest additional value",
    },
    "happy": {
        "tone": "warm and celebratory",
        "prefix": "",
        "approach": "reinforce positive feelings, thank them, suggest sharing feedback",
    },
}


class SentimentResult(BaseModel):
    """Structured sentiment analysis result."""
    emotion: str = Field(description="Detected emotion: angry, frustrated, neutral, satisfied, happy")
    sentiment_score: float = Field(description="Sentiment score from -1.0 (very negative) to 1.0 (very positive)")
    intensity: str = Field(description="Emotion intensity: low, medium, high")
    key_phrases: list[str] = Field(description="Key phrases that indicate the sentiment")
    needs_empathy: bool = Field(description="Whether the response should lead with empathy")
    suggested_tone: str = Field(description="Suggested response tone adjustment")


class SentimentAnalyzer:
    """Analyzes customer sentiment in real-time and provides tone adjustment guidance."""

    def __init__(self, model_name: str | None = None):
        self.llm = ChatOpenAI(
            model=model_name or os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0,
        )
        self.parser = JsonOutputParser(pydantic_object=SentimentResult)
        self.chain = self._build_chain()
        self._conversation_trajectories: dict[str, list[dict]] = {}

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a sentiment analysis expert for customer service interactions.\n\n"
                "Analyze the customer's message and determine:\n"
                "1. The primary emotion (angry, frustrated, neutral, satisfied, happy)\n"
                "2. A sentiment score from -1.0 (very negative) to 1.0 (very positive)\n"
                "3. The intensity of the emotion (low, medium, high)\n"
                "4. Key phrases that reveal the sentiment\n"
                "5. Whether the response should lead with empathy\n"
                "6. The suggested tone for the response\n\n"
                "Consider context clues like:\n"
                "- ALL CAPS = shouting/frustration\n"
                "- Exclamation marks = strong emotion\n"
                "- Polite language = neutral or positive\n"
                "- Threat words (cancel, lawyer, etc.) = high frustration\n"
                "- Gratitude words = satisfied/happy\n\n"
                "Return a JSON object with the fields: emotion, sentiment_score, intensity, "
                "key_phrases, needs_empathy, suggested_tone."
            )),
            ("human", "Customer message: {message}\n\nConversation context (if any): {context}"),
        ])

        return prompt | self.llm | self.parser

    def analyze(self, message: str, conversation_id: str | None = None, context: str = "") -> dict:
        """Analyze sentiment of a customer message."""
        result = self.chain.invoke({"message": message, "context": context})

        emotion = result.get("emotion", "neutral")
        if emotion not in EMOTIONS:
            emotion = "neutral"
        result["emotion"] = emotion

        tone_info = TONE_ADJUSTMENTS.get(emotion, TONE_ADJUSTMENTS["neutral"])
        result["tone_adjustment"] = tone_info

        if conversation_id:
            self._track_trajectory(conversation_id, result)

        return result

    def _track_trajectory(self, conversation_id: str, result: dict):
        """Track sentiment trajectory for a conversation."""
        if conversation_id not in self._conversation_trajectories:
            self._conversation_trajectories[conversation_id] = []

        self._conversation_trajectories[conversation_id].append({
            "emotion": result["emotion"],
            "score": result["sentiment_score"],
            "intensity": result["intensity"],
        })

    def get_trajectory(self, conversation_id: str) -> dict:
        """Get the sentiment trajectory for a conversation."""
        trajectory = self._conversation_trajectories.get(conversation_id, [])

        if not trajectory:
            return {"conversation_id": conversation_id, "trajectory": [], "trend": "no_data"}

        scores = [t["score"] for t in trajectory]
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / len(scores[-3:])
            early_avg = sum(scores[:3]) / len(scores[:3])
            diff = recent_avg - early_avg
            if diff > 0.2:
                trend = "improving"
            elif diff < -0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "conversation_id": conversation_id,
            "trajectory": trajectory,
            "current_emotion": trajectory[-1]["emotion"],
            "average_score": sum(scores) / len(scores),
            "trend": trend,
            "message_count": len(trajectory),
        }

    def needs_escalation(self, conversation_id: str, threshold: float = -0.5) -> bool:
        """Check if the sentiment warrants escalation."""
        trajectory = self._conversation_trajectories.get(conversation_id, [])
        if not trajectory:
            return False

        current_score = trajectory[-1]["score"]
        if current_score <= threshold:
            return True

        if len(trajectory) >= 3:
            recent = trajectory[-3:]
            if all(t["score"] < -0.3 for t in recent):
                return True

        return False

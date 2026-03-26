"""
Intent Classifier Agent — Classifies customer messages into intent categories
using few-shot prompting with confidence scores and sub-categories.
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

INTENTS = [
    "billing_inquiry",
    "technical_support",
    "account_management",
    "feature_request",
    "complaint",
    "general_inquiry",
]

SUB_CATEGORIES = {
    "billing_inquiry": [
        "pricing_question", "invoice_issue", "payment_failure",
        "refund_request", "plan_change", "discount_inquiry",
    ],
    "technical_support": [
        "sync_issue", "login_problem", "app_crash", "performance",
        "integration_issue", "data_loss", "connectivity",
    ],
    "account_management": [
        "password_reset", "2fa_setup", "profile_update",
        "team_management", "data_export", "account_deletion",
    ],
    "feature_request": [
        "new_feature", "improvement", "integration_request", "ui_change",
    ],
    "complaint": [
        "service_quality", "billing_dispute", "support_experience",
        "downtime", "data_concern",
    ],
    "general_inquiry": [
        "product_info", "compatibility", "security", "compliance", "other",
    ],
}

FEW_SHOT_EXAMPLES = [
    {
        "message": "I was charged twice this month, can you look into it?",
        "output": '{"intent": "billing_inquiry", "sub_category": "invoice_issue", "confidence": 0.95}',
    },
    {
        "message": "My files aren't syncing to my laptop since the last update",
        "output": '{"intent": "technical_support", "sub_category": "sync_issue", "confidence": 0.92}',
    },
    {
        "message": "How do I add new team members to our organization?",
        "output": '{"intent": "account_management", "sub_category": "team_management", "confidence": 0.93}',
    },
    {
        "message": "It would be great if you could add dark mode to the mobile app",
        "output": '{"intent": "feature_request", "sub_category": "ui_change", "confidence": 0.88}',
    },
    {
        "message": "I've been trying to get help for 3 days and nobody responds. This is unacceptable!",
        "output": '{"intent": "complaint", "sub_category": "support_experience", "confidence": 0.96}',
    },
    {
        "message": "Does CloudSync Pro work with Linux?",
        "output": '{"intent": "general_inquiry", "sub_category": "compatibility", "confidence": 0.90}',
    },
    {
        "message": "I want a refund, your product has been down 3 times this week",
        "output": '{"intent": "billing_inquiry", "sub_category": "refund_request", "confidence": 0.85}',
    },
    {
        "message": "I forgot my password and the reset email isn't arriving",
        "output": '{"intent": "account_management", "sub_category": "password_reset", "confidence": 0.91}',
    },
]


class IntentResult(BaseModel):
    """Structured intent classification result."""
    intent: str = Field(description="Primary intent category")
    sub_category: str = Field(description="Sub-category within the intent")
    confidence: float = Field(description="Confidence score between 0 and 1")


class IntentClassifier:
    """Classifies customer messages into intent categories using few-shot LLM prompting."""

    def __init__(self, model_name: str | None = None):
        self.llm = ChatOpenAI(
            model=model_name or os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0,
        )
        self.parser = JsonOutputParser(pydantic_object=IntentResult)
        self.chain = self._build_chain()

    def _build_chain(self):
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{message}"),
            ("ai", "{output}"),
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=FEW_SHOT_EXAMPLES,
        )

        system_message = (
            "You are an expert customer service intent classifier for CloudSync Pro, "
            "a cloud collaboration platform.\n\n"
            "Classify the customer's message into exactly one intent category and sub-category.\n\n"
            f"Intent categories: {', '.join(INTENTS)}\n\n"
            "Return a JSON object with:\n"
            '- "intent": one of the categories above\n'
            '- "sub_category": a specific sub-category\n'
            '- "confidence": a float between 0 and 1\n\n'
            "If the message is ambiguous, pick the most likely intent and lower the confidence score."
        )

        final_prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            few_shot_prompt,
            ("human", "{message}"),
        ])

        return final_prompt | self.llm | self.parser

    def classify(self, message: str) -> dict:
        """Classify a customer message and return intent, sub-category, and confidence."""
        result = self.chain.invoke({"message": message})

        if result.get("intent") not in INTENTS:
            result["intent"] = "general_inquiry"
            result["confidence"] = min(result.get("confidence", 0.5), 0.5)

        return result

    def classify_batch(self, messages: list[str]) -> list[dict]:
        """Classify a batch of messages."""
        return [self.classify(msg) for msg in messages]

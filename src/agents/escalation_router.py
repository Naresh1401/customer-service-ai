"""
Escalation Router — Smart escalation logic that evaluates escalation triggers,
routes to appropriate departments, generates summaries for human agents,
and assigns priority scores (P1-P4).
"""

import os
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

DEPARTMENTS = {
    "billing": {
        "name": "Billing & Payments",
        "handles": ["billing_inquiry", "refund_request", "billing_dispute", "payment_failure"],
        "sla_hours": {"P1": 1, "P2": 4, "P3": 12, "P4": 24},
    },
    "technical_l2": {
        "name": "Technical Support L2",
        "handles": ["technical_support", "data_loss", "integration_issue", "app_crash"],
        "sla_hours": {"P1": 0.5, "P2": 2, "P3": 8, "P4": 24},
    },
    "account": {
        "name": "Account Management",
        "handles": ["account_management", "account_deletion", "team_management"],
        "sla_hours": {"P1": 2, "P2": 8, "P3": 24, "P4": 48},
    },
    "management": {
        "name": "Customer Success Management",
        "handles": ["complaint", "escalation_request", "churn_risk"],
        "sla_hours": {"P1": 1, "P2": 4, "P3": 12, "P4": 48},
    },
}

ESCALATION_TRIGGERS = [
    "Customer has repeated the same issue 3+ times",
    "Customer sentiment is highly negative (angry/frustrated at high intensity)",
    "Customer has threatened to cancel or mentioned a competitor",
    "Issue involves data loss or security concern",
    "Billing dispute exceeds $500 or involves unauthorized charges",
    "Customer has been waiting for resolution over 48 hours",
    "Technical issue requires backend/infrastructure investigation",
    "Customer explicitly requests to speak with a manager/supervisor",
]


class EscalationResult(BaseModel):
    """Structured escalation evaluation result."""
    should_escalate: bool = Field(description="Whether the conversation should be escalated")
    priority: str = Field(description="Priority level: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)")
    department: str = Field(description="Target department for escalation")
    triggers_matched: list[str] = Field(description="Which escalation triggers were matched")
    summary: str = Field(description="Concise summary for the human agent")
    recommended_action: str = Field(description="Recommended next action for the human agent")


class EscalationRouter:
    """Evaluates conversations for escalation and routes to appropriate departments."""

    def __init__(self, model_name: str | None = None):
        self.llm = ChatOpenAI(
            model=model_name or os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0,
        )
        self.parser = JsonOutputParser(pydantic_object=EscalationResult)
        self.chain = self._build_chain()
        self._escalation_queue: list[dict] = []

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an escalation evaluation expert for CloudSync Pro customer service.\n\n"
                "Evaluate whether a customer conversation needs to be escalated to a human agent.\n\n"
                "## Escalation Triggers\n"
                + "\n".join(f"- {t}" for t in ESCALATION_TRIGGERS) +
                "\n\n## Available Departments\n"
                + "\n".join(
                    f"- {d['name']}: handles {', '.join(d['handles'])}"
                    for d in DEPARTMENTS.values()
                ) +
                "\n\n## Priority Levels\n"
                "- P1 (Critical): Service down, data loss, security breach, very angry customer\n"
                "- P2 (High): Major feature broken, billing dispute, customer threatening to leave\n"
                "- P3 (Medium): Non-critical issue needing specialist, repeated minor issue\n"
                "- P4 (Low): Feature request, general feedback, low-urgency questions\n\n"
                "Return a JSON object with: should_escalate, priority, department, "
                "triggers_matched, summary, recommended_action.\n\n"
                "For the summary, write a concise 2-3 sentence brief that a human agent can "
                "quickly read to understand the situation."
            )),
            ("human", (
                "Conversation history:\n{conversation_history}\n\n"
                "Current intent: {intent}\n"
                "Current sentiment: {sentiment}\n"
                "Sentiment score: {sentiment_score}\n"
                "Turn count: {turn_count}"
            )),
        ])

        return prompt | self.llm | self.parser

    def evaluate(
        self,
        conversation_history: str,
        intent: str = "unknown",
        sentiment: str = "neutral",
        sentiment_score: float = 0.0,
        turn_count: int = 1,
    ) -> dict:
        """Evaluate whether a conversation needs escalation."""
        result = self.chain.invoke({
            "conversation_history": conversation_history,
            "intent": intent,
            "sentiment": sentiment,
            "sentiment_score": str(sentiment_score),
            "turn_count": str(turn_count),
        })

        valid_priorities = {"P1", "P2", "P3", "P4"}
        if result.get("priority") not in valid_priorities:
            result["priority"] = "P3"

        valid_departments = set(DEPARTMENTS.keys())
        if result.get("department") not in valid_departments:
            result["department"] = "management"

        dept_info = DEPARTMENTS[result["department"]]
        result["department_name"] = dept_info["name"]
        result["sla_hours"] = dept_info["sla_hours"].get(result["priority"], 24)

        if result.get("should_escalate"):
            self._add_to_queue(result, conversation_history)

        return result

    def _add_to_queue(self, result: dict, conversation_history: str):
        """Add an escalation to the queue."""
        escalation = {
            **result,
            "id": f"ESC-{len(self._escalation_queue) + 1:04d}",
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "conversation_snippet": conversation_history[:500],
        }
        self._escalation_queue.append(escalation)

    def get_queue(self, department: str | None = None, priority: str | None = None) -> list[dict]:
        """Get the escalation queue, optionally filtered."""
        queue = self._escalation_queue

        if department:
            queue = [e for e in queue if e.get("department") == department]
        if priority:
            queue = [e for e in queue if e.get("priority") == priority]

        priority_order = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}
        queue.sort(key=lambda e: priority_order.get(e.get("priority", "P4"), 4))

        return queue

    def resolve_escalation(self, escalation_id: str, resolution: str) -> bool:
        """Mark an escalation as resolved."""
        for esc in self._escalation_queue:
            if esc["id"] == escalation_id:
                esc["status"] = "resolved"
                esc["resolution"] = resolution
                esc["resolved_at"] = datetime.utcnow().isoformat()
                return True
        return False

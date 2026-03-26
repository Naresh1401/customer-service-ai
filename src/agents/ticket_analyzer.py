"""
Ticket Analyzer — Analyzes support tickets for insights including
auto-categorization, root cause clustering, resolution time prediction,
trend detection, and analytics report generation.
"""

import os
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class TicketAnalysis(BaseModel):
    """Analysis result for a single ticket."""
    category: str = Field(description="Auto-assigned category")
    sub_category: str = Field(description="Specific sub-category")
    root_cause: str = Field(description="Identified root cause")
    severity: str = Field(description="Severity: critical, high, medium, low")
    estimated_resolution_hours: float = Field(description="Predicted resolution time in hours")
    tags: list[str] = Field(description="Relevant tags for the ticket")
    similar_issues: str = Field(description="Pattern match to known issue clusters")


class BatchAnalytics(BaseModel):
    """Analytics result for a batch of tickets."""
    total_tickets: int = Field(description="Total tickets analyzed")
    category_distribution: dict[str, int] = Field(description="Tickets per category")
    severity_distribution: dict[str, int] = Field(description="Tickets per severity")
    top_root_causes: list[str] = Field(description="Most common root causes")
    avg_estimated_resolution_hours: float = Field(description="Average predicted resolution time")
    trends: list[str] = Field(description="Detected trends or patterns")
    recommendations: list[str] = Field(description="Actionable recommendations")


class TicketAnalyzer:
    """Analyzes support tickets for categorization, root causes, and trends."""

    def __init__(self, model_name: str | None = None):
        self.llm = ChatOpenAI(
            model=model_name or os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0,
        )
        self.single_parser = JsonOutputParser(pydantic_object=TicketAnalysis)
        self.batch_parser = JsonOutputParser(pydantic_object=BatchAnalytics)
        self.single_chain = self._build_single_chain()
        self.batch_chain = self._build_batch_chain()
        self._analyzed_tickets: list[dict] = []

    def _build_single_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a support ticket analysis expert for CloudSync Pro.\n\n"
                "Analyze the support ticket and determine:\n"
                "1. Category (billing, technical, account, feature_request, complaint, general)\n"
                "2. Sub-category (be specific)\n"
                "3. Root cause (identify the underlying issue)\n"
                "4. Severity (critical, high, medium, low)\n"
                "5. Estimated resolution time in hours\n"
                "6. Relevant tags\n"
                "7. Whether this matches known issue patterns\n\n"
                "## Severity Guidelines\n"
                "- Critical: Service outage, data loss, security breach\n"
                "- High: Major feature broken, accounts locked out, billing errors\n"
                "- Medium: Non-critical bugs, performance issues, feature questions\n"
                "- Low: Feature requests, general inquiries, cosmetic issues\n\n"
                "## Resolution Time Estimation\n"
                "- Consider: complexity, department routing, historical averages\n"
                "- Critical: 1-4h, High: 4-12h, Medium: 12-48h, Low: 48-96h\n\n"
                "Return a JSON object with: category, sub_category, root_cause, severity, "
                "estimated_resolution_hours, tags, similar_issues."
            )),
            ("human", "Ticket Subject: {subject}\n\nTicket Body:\n{body}"),
        ])

        return prompt | self.llm | self.single_parser

    def _build_batch_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a support analytics expert for CloudSync Pro.\n\n"
                "Analyze this batch of categorized support tickets and provide:\n"
                "1. Distribution across categories and severities\n"
                "2. The top 5 most common root causes\n"
                "3. Average estimated resolution time\n"
                "4. Emerging trends or patterns\n"
                "5. Actionable recommendations for the support team\n\n"
                "Focus on insights that would help reduce ticket volume or improve resolution times.\n\n"
                "Return a JSON object with: total_tickets, category_distribution, "
                "severity_distribution, top_root_causes, avg_estimated_resolution_hours, "
                "trends, recommendations."
            )),
            ("human", "Analyzed tickets:\n{ticket_summaries}"),
        ])

        return prompt | self.llm | self.batch_parser

    def analyze_ticket(self, subject: str, body: str) -> dict:
        """Analyze a single support ticket."""
        result = self.single_chain.invoke({"subject": subject, "body": body})

        ticket_record = {
            **result,
            "subject": subject,
            "analyzed_at": datetime.utcnow().isoformat(),
        }
        self._analyzed_tickets.append(ticket_record)

        return result

    def analyze_batch(self, tickets: list[dict]) -> dict:
        """Analyze a batch of tickets and generate aggregate analytics.

        Args:
            tickets: List of dicts with 'subject' and 'body' keys.
        """
        individual_results = []
        for ticket in tickets:
            result = self.analyze_ticket(ticket["subject"], ticket["body"])
            individual_results.append(result)

        summaries = []
        for i, result in enumerate(individual_results):
            summaries.append(
                f"Ticket {i + 1}: category={result['category']}, "
                f"severity={result['severity']}, "
                f"root_cause={result['root_cause']}, "
                f"est_hours={result['estimated_resolution_hours']}"
            )

        batch_analytics = self.batch_chain.invoke({
            "ticket_summaries": "\n".join(summaries)
        })

        return {
            "individual_analyses": individual_results,
            "aggregate_analytics": batch_analytics,
        }

    def generate_report(self, period: str = "weekly") -> dict:
        """Generate an analytics report from analyzed tickets."""
        if not self._analyzed_tickets:
            return {"error": "No tickets have been analyzed yet."}

        tickets = self._analyzed_tickets

        categories = {}
        severities = {}
        root_causes = {}
        resolution_times = []

        for t in tickets:
            cat = t.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

            sev = t.get("severity", "unknown")
            severities[sev] = severities.get(sev, 0) + 1

            rc = t.get("root_cause", "unknown")
            root_causes[rc] = root_causes.get(rc, 0) + 1

            rt = t.get("estimated_resolution_hours", 0)
            if rt:
                resolution_times.append(rt)

        sorted_root_causes = sorted(root_causes.items(), key=lambda x: x[1], reverse=True)

        return {
            "report_type": period,
            "generated_at": datetime.utcnow().isoformat(),
            "total_tickets": len(tickets),
            "category_distribution": categories,
            "severity_distribution": severities,
            "top_root_causes": [
                {"cause": rc, "count": count}
                for rc, count in sorted_root_causes[:10]
            ],
            "avg_resolution_hours": (
                sum(resolution_times) / len(resolution_times) if resolution_times else 0
            ),
            "tickets_by_severity": {
                "critical": severities.get("critical", 0),
                "high": severities.get("high", 0),
                "medium": severities.get("medium", 0),
                "low": severities.get("low", 0),
            },
        }

"""
FastAPI Application — REST API for the AI Customer Service Platform.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Customer Service Platform",
    description="Intelligent customer service automation with LLM agents",
    version="1.0.0",
)

# ── Request / Response Models ──────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    customer_name: str | None = None
    category: str | None = None

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    turn_count: int
    sources_used: int

class ClassifyRequest(BaseModel):
    message: str

class SentimentRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    context: str = ""

class EscalationRequest(BaseModel):
    conversation_history: str
    intent: str = "unknown"
    sentiment: str = "neutral"
    sentiment_score: float = 0.0
    turn_count: int = 1

class TicketInput(BaseModel):
    subject: str
    body: str

class TicketBatchRequest(BaseModel):
    tickets: list[TicketInput]

# ── Lazy Agent Initialization ──────────────────────────────────────

_intent_classifier = None
_conversation_agent = None
_sentiment_analyzer = None
_escalation_router = None
_ticket_analyzer = None


def get_intent_classifier():
    global _intent_classifier
    if _intent_classifier is None:
        from src.agents.intent_classifier import IntentClassifier
        _intent_classifier = IntentClassifier()
    return _intent_classifier


def get_conversation_agent():
    global _conversation_agent
    if _conversation_agent is None:
        from src.agents.conversation_agent import ConversationAgent
        _conversation_agent = ConversationAgent()
    return _conversation_agent


def get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        from src.agents.sentiment_analyzer import SentimentAnalyzer
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer


def get_escalation_router():
    global _escalation_router
    if _escalation_router is None:
        from src.agents.escalation_router import EscalationRouter
        _escalation_router = EscalationRouter()
    return _escalation_router


def get_ticket_analyzer():
    global _ticket_analyzer
    if _ticket_analyzer is None:
        from src.agents.ticket_analyzer import TicketAnalyzer
        _ticket_analyzer = TicketAnalyzer()
    return _ticket_analyzer


# ── Endpoints ──────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Customer Service Platform"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Handle a customer message in a multi-turn conversation."""
    agent = get_conversation_agent()
    result = agent.chat(
        message=request.message,
        conversation_id=request.conversation_id,
        customer_name=request.customer_name,
        category=request.category,
    )
    return ChatResponse(**result)


@app.post("/classify")
def classify_intent(request: ClassifyRequest):
    """Classify the intent of a customer message."""
    classifier = get_intent_classifier()
    return classifier.classify(request.message)


@app.post("/sentiment")
def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment of a customer message."""
    analyzer = get_sentiment_analyzer()
    return analyzer.analyze(
        message=request.message,
        conversation_id=request.conversation_id,
        context=request.context,
    )


@app.post("/escalate")
def evaluate_escalation(request: EscalationRequest):
    """Evaluate whether a conversation needs escalation."""
    router = get_escalation_router()
    return router.evaluate(
        conversation_history=request.conversation_history,
        intent=request.intent,
        sentiment=request.sentiment,
        sentiment_score=request.sentiment_score,
        turn_count=request.turn_count,
    )


@app.post("/tickets/analyze")
def analyze_tickets(request: TicketBatchRequest):
    """Analyze a batch of support tickets."""
    analyzer = get_ticket_analyzer()
    tickets = [{"subject": t.subject, "body": t.body} for t in request.tickets]
    return analyzer.analyze_batch(tickets)


@app.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: str):
    """Get the full history of a conversation."""
    agent = get_conversation_agent()
    conversation = agent.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.get("/escalation-queue")
def get_escalation_queue(department: str | None = None, priority: str | None = None):
    """Get the current escalation queue."""
    router = get_escalation_router()
    return router.get_queue(department=department, priority=priority)


@app.get("/tickets/report")
def get_ticket_report(period: str = "weekly"):
    """Generate a ticket analytics report."""
    analyzer = get_ticket_analyzer()
    return analyzer.generate_report(period=period)

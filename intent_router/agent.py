import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext

# --- Setup Logging and Environment ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")

# --- Fixed responses for each intent ---
INTENT_RESPONSES = {
    "order_status": (
        "To check your order status, please visit your account at "
        "https://shop.example.com/orders or contact us at orders@example.com "
        "with your order ID."
    ),
    "return_request": (
        "We accept returns within 30 days of purchase. To start a return, "
        "visit https://shop.example.com/returns or email returns@example.com "
        "with your order ID and reason for return."
    ),
    "shipping_info": (
        "Standard shipping takes 5-7 business days. Express shipping (2-3 days) "
        "is available at checkout. Free shipping on orders above $50."
    ),
    "payment_issue": (
        "For payment issues, please contact our billing team at "
        "billing@example.com or call 1-800-123-4567 (Mon-Fri, 9am-5pm EST)."
    ),
    "general_inquiry": (
        "Thanks for reaching out! For general inquiries, please email "
        "support@example.com or visit our FAQ at https://shop.example.com/faq."
    ),
}


# --- Tool ---
def route_intent(tool_context: ToolContext, intent: str) -> dict:
    """
    Takes a classified intent label and returns the fixed response for it.

    Args:
        tool_context: ADK tool context for state management.
        intent: One of: order_status, return_request, shipping_info,
                payment_issue, general_inquiry.

    Returns:
        A dict with the intent and its fixed response.
    """
    intent = intent.strip().lower()
    response = INTENT_RESPONSES.get(intent, INTENT_RESPONSES["general_inquiry"])

    # Save to state 
    tool_context.state["LAST_INTENT"] = intent
    tool_context.state["LAST_RESPONSE"] = response

    logging.info(f"[State updated] Intent: {intent}")

    return {
        "intent": intent,
        "response": response,
    }


# --- Agent ---
root_agent = Agent(
    name="intent_router",
    model=model_name,
    description="An e-commerce support agent that classifies user messages and routes them to the correct fixed response.",
    instruction="""You are an e-commerce customer support routing agent.

Your ONLY job is to:
1. Read the user's message carefully.
2. Classify it into EXACTLY one of these intents:
   - order_status     → user asking about their order location or status
   - return_request   → user wants to return or exchange an item
   - shipping_info    → user asking about delivery times or shipping options
   - payment_issue    → user has a payment, billing, or charge problem
   - general_inquiry  → anything else

3. Call the route_intent tool with the classified intent label.
4. Return the tool's response to the user. Do not modify or add to it.

Always call route_intent. Never answer from your own knowledge.""",
    tools=[route_intent],
)
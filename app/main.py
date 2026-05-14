import uuid

from fastapi import FastAPI

from app.database.init_db import init_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.guardrail_service import guardrail_service
from app.services.llm_service import llm_service
from app.services.missing_request_service import missing_request_service
from app.services.product_service import product_service
from app.services.recommendation_service import recommendation_service
from app.services.session_service import session_service

app = FastAPI(
    title="Actually Fair Chatbot API",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {
        "message": "Actually Fair Chatbot API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    if guardrail_service.is_blocked(request.message):
        reply = guardrail_service.get_blocked_response()

        session_service.save_message(
            session_id=session_id,
            role="user",
            content=request.message
        )

        session_service.save_message(
            session_id=session_id,
            role="assistant",
            content=reply
        )

        return ChatResponse(
            session_id=session_id,
            reply=reply,
            products=[]
        )

    products = product_service.search_products(request.message)

    if not products:
        products = recommendation_service.recommend_products(
            request.message
        )

    if not products:
        missing_request_service.save_request(
            session_id=session_id,
            query=request.message
        )

    if products:
        product_context = "\n\n".join(
            [
                f"""
Title: {product.title}
Price: {product.price} {product.currency}
Description: {product.description}
Material: {product.material}
Fit: {product.fit_description}
Markup: 14%
                """.strip()
                for product in products
            ]
        )
    else:
        product_context = ""

    conversation_history = session_service.get_messages(session_id)

    if products:
        reply = llm_service.generate_reply(
            user_message=request.message,
            product_context=product_context,
            conversation_history=conversation_history
        )
    else:
        reply = (
            f"We don't currently offer {request.message.lower()}. "
            "I've noted your request for future consideration. "
            "I can also help you explore our activewear, backpacks, sunglasses, and accessories."
        )

    session_service.save_message(
        session_id=session_id,
        role="user",
        content=request.message
    )

    session_service.save_message(
        session_id=session_id,
        role="assistant",
        content=reply
    )

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        products=products
    )
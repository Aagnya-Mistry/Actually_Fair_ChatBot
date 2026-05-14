from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class MarkupBreakdown(BaseModel):
    estimated_base_cost: float
    markup_percentage: float
    markup_amount: float
    final_price: float


class ProductSuggestion(BaseModel):
    title: str
    handle: str
    price: float
    currency: str
    description: str
    material: str
    fit_description: str
    image_url: str
    markup: MarkupBreakdown


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    products: List[ProductSuggestion] = []
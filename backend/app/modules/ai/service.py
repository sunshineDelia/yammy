from app.modules.ai.context_builder import ContextBuilder
from app.modules.ai.deepseek_client import DeepSeekClient
from app.modules.ai.schema import ConsultReferences, ConsultResponse
from app.modules.attraction.schema import AttractionBrief
from app.modules.food.schema import FoodBrief


class AIService:
    def __init__(self, context_builder: ContextBuilder, client: DeepSeekClient):
        self.context_builder = context_builder
        self.client = client

    def consult(self, question: str) -> ConsultResponse:
        context = self.context_builder.retrieve(question)
        messages = self.context_builder.build_messages(question, context)
        answer = self.client.chat(messages)
        return ConsultResponse(
            answer=answer,
            references=ConsultReferences(
                foods=[FoodBrief.model_validate(f) for f in context["foods"]],
                attractions=[AttractionBrief.model_validate(a) for a in context["attractions"]],
            ),
        )

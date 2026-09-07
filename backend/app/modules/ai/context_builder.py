from app.modules.attraction.repository import AttractionRepository
from app.modules.food.repository import FoodRepository

SYSTEM_PROMPT = (
    "你是「南昌旅游美食助手」，请基于提供的南昌本地美食与景点数据回答用户问题，"
    "给出实用的游玩/美食攻略建议。若数据不足以回答，请诚实说明，不要编造。"
)


class ContextBuilder:
    def __init__(self, food_repo: FoodRepository, attraction_repo: AttractionRepository):
        self.food_repo = food_repo
        self.attraction_repo = attraction_repo

    def retrieve(self, question: str) -> dict:
        foods = [f for f in self.food_repo.list_all() if f.name and f.name in question]
        attractions = [a for a in self.attraction_repo.list_all() if a.name and a.name in question]
        if not foods:
            foods = self.food_repo.search(question, limit=5)
        if not attractions:
            attractions = self.attraction_repo.search(question, limit=5)
        return {"foods": foods[:5], "attractions": attractions[:5]}

    def _format_context(self, context: dict) -> str:
        lines = ["以下为南昌本地数据："]
        if context["foods"]:
            lines.append("【美食】")
            for f in context["foods"]:
                stores = "、".join(s.name for s in f.stores)
                lines.append(f"- {f.name}：人均 {f.avg_price} 元；{f.description}；推荐门店：{stores}")
        if context["attractions"]:
            lines.append("【景点】")
            for a in context["attractions"]:
                lines.append(f"- {a.name}：开放时间 {a.open_time}；门票 {a.ticket_price}；{a.description}")
        return "\n".join(lines)

    def build_messages(self, question: str, context: dict) -> list[dict]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{self._format_context(context)}\n\n用户问题：{question}"},
        ]

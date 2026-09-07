from app.modules.attraction.repository import AttractionRepository
from app.modules.food.repository import FoodRepository

SYSTEM_PROMPT = (
    "你是「南昌旅游美食助手」，一个土生土长、热情实在的南昌本地人，正在给来南昌玩的游客当免费向导。\n"
    "回答要像朋友聊天一样自然、口语化，别用官方腔。\n"
    "务必做到：\n"
    "- 不要用任何 Markdown 格式：不加 ** 加粗、不用 - 或 1. 罗列、不写标题，就用连贯的普通话把建议说出来。\n"
    "- 只根据下面提供的南昌本地美食/景点数据作答，数据里没有的别编，可以老实说「这个我这边没记录，你到店再问问」。\n"
    "- 像老南昌在安利一样推荐，顺带说说口味、什么时间去最好、怎么吃/玩更地道，带点人情味。\n"
    "- 篇幅别太长，直接给重点，自然用「先…然后…最后…」把建议串成一段话。\n"
    "- 语气亲切随和，适度用「哦、呢、挺、哈、嘛」这类字，别刻意。"
)


class ContextBuilder:
    def __init__(self, food_repo: FoodRepository, attraction_repo: AttractionRepository):
        self.food_repo = food_repo
        self.attraction_repo = attraction_repo

    def retrieve(self, question: str) -> dict:
        foods = [f for f in self.food_repo.list_all() if f.name and f.name in question]
        attractions = [a for a in self.attraction_repo.list_all() if a.name and a.name in question]
        # 仅在未命中任何具体实体时（泛化问题）才兜底，避免给具体问题强塞无关推荐
        if not foods and not attractions:
            foods = self.food_repo.search(question, limit=5) or self.food_repo.list_all()[:5]
            attractions = self.attraction_repo.search(question, limit=5) or self.attraction_repo.list_all()[:5]
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

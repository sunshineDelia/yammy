"""预置种子数据。运行：cd backend && python -m seed.seed"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select

from app.core.database import Base, SessionLocal, engine
from app.modules.attraction.model import Attraction
from app.modules.favorite.model import Favorite  # noqa: F401  确保 create_all 创建 favorite 表
from app.modules.food.model import Food, Store


def seed() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        food_count = db.scalar(select(func.count()).select_from(Food)) or 0
        attraction_count = db.scalar(select(func.count()).select_from(Attraction)) or 0
        if food_count > 0 or attraction_count > 0:
            print("检测到已有数据，跳过种子。")
            return

        foods = [
            Food(
                name="南昌拌粉", description="南昌最具代表性的小吃，米粉爽滑筋道，配花生米、萝卜干、辣椒油拌匀，酸辣开胃。",
                avg_price=12.0, image_url="/static/images/foods/nanchang_banfen.jpg",
                stores=[Store(name="黄记瓦罐拌粉", address="中山路"), Store(name="老南昌拌粉店", address="胜利路")],
            ),
            Food(
                name="瓦罐汤", description="用瓦罐煨制数小时的传统汤品，汤鲜味浓、滋补养胃，是南昌人早餐的经典搭配。",
                avg_price=20.0, image_url="/static/images/foods/waguan_tang.jpg",
                stores=[Store(name="民间瓦罐煨汤", address="八一广场")],
            ),
            Food(
                name="藜蒿炒腊肉", description="南昌名菜，藜蒿清香脆嫩，与腊肉同炒咸香下饭，是鄱阳湖一带的特色风味。",
                avg_price=35.0, image_url="/static/images/foods/lihao_chaolarou.jpg",
                stores=[Store(name="豫章人家", address="绳金塔")],
            ),
            Food(
                name="南昌白糖糕", description="传统甜点，糯米外裹糖霜，软糯香甜，是南昌人记忆里的童年味道。",
                avg_price=8.0, image_url="/static/images/foods/baitang_gao.jpg",
                stores=[Store(name="老字号白糖糕", address="孺子路")],
            ),
            Food(
                name="牛杂粉", description="粉滑汤浓，牛杂软烂入味，是南昌街头巷尾广受欢迎的平价美食。",
                avg_price=15.0, image_url="/static/images/foods/niuza_fen.jpg",
                stores=[Store(name="孺子路牛杂粉", address="孺子路")],
            ),
            Food(
                name="豫章酥鸭", description="南昌传统名菜，鸭肉酥烂脱骨，皮脆肉嫩，风味独特。",
                avg_price=55.0, image_url="/static/images/foods/yuzhang_suya.jpg",
                stores=[Store(name="豫章酒家", address="东湖区")],
            ),
        ]

        attractions = [
            Attraction(name="滕王阁", description="江南三大名楼之一，因王勃《滕王阁序》名扬天下，登楼可眺赣江风光。", open_time="08:00-18:00", ticket_price="50 元", image_url="/static/images/attractions/tengwangge.jpg"),
            Attraction(name="八一广场", description="南昌城市中心广场，江西重要的纪念性地标，夜景灯光尤为壮观。", open_time="全天开放", ticket_price="免费", image_url="/static/images/attractions/bayi_guangchang.jpg"),
            Attraction(name="绳金塔", description="南昌古塔之一，始建于唐代，周边汇聚地道南昌小吃，是美食爱好者的必去之地。", open_time="08:30-17:30", ticket_price="免费（登塔另收费）", image_url="/static/images/attractions/shengjin_ta.jpg"),
            Attraction(name="南昌之星摩天轮", description="世界较高的摩天轮之一，可俯瞰南昌城市与赣江全景，夜晚灯光璀璨。", open_time="09:30-22:00", ticket_price="50 元", image_url="/static/images/attractions/nanchang_zhixing.jpg"),
            Attraction(name="梅岭国家森林公园", description="南昌近郊的天然氧吧，四季景色各异，适合登山徒步与休闲度假。", open_time="全天开放", ticket_price="免费", image_url="/static/images/attractions/meiling.jpg"),
            Attraction(name="南昌汉代海昏侯国遗址公园", description="西汉海昏侯刘贺墓所在地，出土大量珍贵文物，是了解汉代历史的重要遗址。", open_time="09:00-17:00", ticket_price="60 元", image_url="/static/images/attractions/haihunhou.jpg"),
        ]

        db.add_all(foods + attractions)
        db.commit()
        print(f"种子数据完成：{len(foods)} 条美食，{len(attractions)} 条景点。")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

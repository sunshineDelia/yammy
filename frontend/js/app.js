const routes = {
  foods: () => FoodView.list(),
  attractions: () => AttractionView.list(),
  ranking: () => RankingView.render(),
  ai: () => AIView.render(),
  favorites: () => FavoriteView.list(),
};

function renderHome() {
  const view = document.getElementById("view");
  view.innerHTML = `
    <div class="hero">
      <h1>探索南昌 · 寻味赣鄱</h1>
      <p>60+ 特色美食 · 60+ 旅游景点 · AI 智能攻略，一站式规划你的南昌之旅</p>
    </div>
    <div class="card-grid">
      <div class="card" style="cursor:pointer" onclick="location.hash='#/foods'">
        <div class="card-body">
          <h3>🍜 特色美食</h3>
          <p class="desc">南昌拌粉、瓦罐汤、藜蒿炒腊肉…… 60+ 道地道风味</p>
        </div>
      </div>
      <div class="card" style="cursor:pointer" onclick="location.hash='#/attractions'">
        <div class="card-body">
          <h3>🏞️ 旅游景点</h3>
          <p class="desc">滕王阁、海昏侯、梅岭…… 60+ 处游玩好去处</p>
        </div>
      </div>
      <div class="card" style="cursor:pointer" onclick="location.hash='#/ranking'">
        <div class="card-body">
          <h3>🏆 好评榜</h3>
          <p class="desc">按真实评分排行的美食/景点榜单，帮你快速做选择</p>
        </div>
      </div>
      <div class="card" style="cursor:pointer" onclick="location.hash='#/ai'">
        <div class="card-body">
          <h3>🤖 AI 攻略</h3>
          <p class="desc">输入问题，一键生成专属南昌游玩攻略</p>
        </div>
      </div>
    </div>`;
}

function setActiveNav(view) {
  document.querySelectorAll(".nav a").forEach((a) => {
    a.classList.toggle("active", a.dataset.view === view);
  });
}

function router() {
  const hash = location.hash || "#/";
  const view = document.getElementById("view");
  if (hash === "#/" || hash === "#/home") {
    setActiveNav("home");
    return renderHome();
  }
  const parts = hash.slice(2).split("/").filter(Boolean);
  const name = parts[0];
  const id = parts[1];
  if (name === "foods" && id) { setActiveNav("foods"); return FoodView.detail(id); }
  if (name === "attractions" && id) { setActiveNav("attractions"); return AttractionView.detail(id); }
  const handler = routes[name];
  if (handler) {
    setActiveNav(name);
    handler();
  } else {
    setActiveNav("");
    view.innerHTML = `<div class="empty">页面不存在</div>`;
  }
}

window.addEventListener("hashchange", router);
router();

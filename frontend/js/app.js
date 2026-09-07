const routes = {
  foods: () => FoodView.list(),
  attractions: () => AttractionView.list(),
  ai: () => AIView.render(),
  favorites: () => FavoriteView.list(),
};

function renderHome() {
  const view = document.getElementById("view");
  view.innerHTML = `
    <div class="detail">
      <h2>欢迎来到南昌</h2>
      <p>探索南昌特色美食与旅游景点，还能用 AI 帮你规划游玩攻略。</p>
      <div class="card-grid" style="margin-top:16px">
        <div class="card"><div class="card-body"><h3>🍜 美食</h3><p class="desc">南昌拌粉、瓦罐汤、藜蒿炒腊肉……</p></div></div>
        <div class="card"><div class="card-body"><h3>🏞️ 景点</h3><p class="desc">滕王阁、八一广场、绳金塔……</p></div></div>
        <div class="card"><div class="card-body"><h3>🤖 AI 攻略</h3><p class="desc">输入问题，一键生成南昌游玩攻略。</p></div></div>
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
  setActiveNav("");
  if (hash === "#/" || hash === "#/home") return renderHome();
  const [name, id] = hash.slice(2).split("/");
  if (name === "foods" && id) return FoodView.detail(id);
  if (name === "attractions" && id) return AttractionView.detail(id);
  const handler = routes[name];
  if (handler) {
    setActiveNav(name);
    handler();
  } else {
    view.innerHTML = `<div class="empty">页面不存在</div>`;
  }
}

window.addEventListener("hashchange", router);
router();

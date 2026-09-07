const RankingView = {
  type: "food",

  render() {
    const view = document.getElementById("view");
    view.innerHTML = `
      <div class="ranking-tabs">
        <button id="rk-food" class="active">美食好评榜</button>
        <button id="rk-attr">景点好评榜</button>
      </div>
      <div id="rank-list" class="rank-list"><div class="loading">加载中…</div></div>`;
    document.getElementById("rk-food").onclick = () => this.switch("food");
    document.getElementById("rk-attr").onclick = () => this.switch("attraction");
    this.load("food");
  },

  switch(type) {
    this.type = type;
    document.getElementById("rk-food").classList.toggle("active", type === "food");
    document.getElementById("rk-attr").classList.toggle("active", type === "attraction");
    this.load(type);
  },

  async load(type) {
    const box = document.getElementById("rank-list");
    box.innerHTML = `<div class="loading">加载中…</div>`;
    let data;
    try {
      data = await api.get(type === "food" ? "/foods?sort=rating&page_size=50" : "/attractions?sort=rating&page_size=50");
    } catch (e) {
      box.innerHTML = `<div class="empty">加载失败：${escapeHtml(e.message)}</div>`;
      return;
    }
    if (data.items.length === 0) {
      box.innerHTML = `<div class="empty">暂无数据</div>`;
      return;
    }
    box.innerHTML = data.items.map((it, i) => {
      const cls = i === 0 ? "top1" : i === 1 ? "top2" : i === 2 ? "top3" : "";
      const sub = type === "food" ? `${it.category} · 人均 ¥${it.avg_price}` : `${it.level || "无等级"} · ${it.ticket_price}`;
      const href = type === "food" ? "foods" : "attractions";
      return `
        <div class="rank-item ${cls}" onclick="location.hash='#/${href}/${it.id}'">
          <div class="rank-no">${i + 1}</div>
          ${it.image_url ? `<img src="${escapeHtml(it.image_url)}" onerror="this.style.display='none'" alt="${escapeHtml(it.name)}">` : ""}
          <div class="info">
            <h3>${escapeHtml(it.name)}</h3>
            <div class="sub">${escapeHtml(sub)}</div>
            <div class="rating">${renderStars(it.rating)}<span class="score">${it.rating}</span><span class="count">${it.rating_count}条</span></div>
          </div>
          <div class="score">${it.rating} 分</div>
        </div>`;
    }).join("");
  },
};

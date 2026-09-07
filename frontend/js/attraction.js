const AttractionView = {
  async list() {
    const view = document.getElementById("view");
    view.innerHTML = `
      <div class="searchbar">
        <input id="att-kw" placeholder="搜索景点（名称/简介）">
        <button class="btn" id="att-search">搜索</button>
      </div>
      <div id="att-grid" class="card-grid"><div class="loading">加载中…</div></div>
      <div id="att-pager" class="pager"></div>`;
    await this._load(1);
    document.getElementById("att-search").onclick = () => this._load(1, document.getElementById("att-kw").value);
  },

  async _load(page, keyword = "") {
    const grid = document.getElementById("att-grid");
    const pager = document.getElementById("att-pager");
    const q = `page=${page}&page_size=9&keyword=${encodeURIComponent(keyword)}`;
    const data = await api.get(`/attractions?${q}`);
    if (data.items.length === 0) {
      grid.innerHTML = `<div class="empty">暂无景点数据</div>`;
      pager.innerHTML = "";
      return;
    }
    grid.innerHTML = data.items.map((a) => `
      <div class="card">
        <img src="${a.image_url || ""}" onerror="this.style.display='none'" alt="${a.name}">
        <div class="card-body">
          <h3>${a.name}</h3>
          <div class="meta">${a.ticket_price} · ${a.open_time}</div>
          <p class="desc">${a.description}</p>
          <div class="actions">
            <button class="btn" onclick="location.hash='#/attractions/${a.id}'">查看详情</button>
            <button class="btn ${FavoriteView.isFaved("attraction", a.id) ? "faved" : ""}" onclick="FavoriteView.toggle('attraction', ${a.id}, this)">${FavoriteView.isFaved("attraction", a.id) ? "已收藏" : "收藏"}</button>
          </div>
        </div>
      </div>`).join("");
    pager.innerHTML = `第 ${data.page} / ${Math.ceil(data.total / data.page_size) || 1} 页`;
  },

  async detail(id) {
    const view = document.getElementById("view");
    const a = await api.get(`/attractions/${id}`);
    view.innerHTML = `
      <div class="detail">
        <h2>${a.name}</h2>
        <div class="meta">开放时间 ${a.open_time} · 门票 ${a.ticket_price}</div>
        <img src="${a.image_url || ""}" onerror="this.style.display='none'" alt="${a.name}">
        <p>${a.description}</p>
      </div>`;
  },
};

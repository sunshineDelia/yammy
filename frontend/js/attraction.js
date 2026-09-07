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
    await FavoriteView.sync();
    await this._load(1);
    document.getElementById("att-search").onclick = () => this._load(1, document.getElementById("att-kw").value);
  },

  async _load(page, keyword = "") {
    const grid = document.getElementById("att-grid");
    const pager = document.getElementById("att-pager");
    const q = `page=${page}&page_size=9&keyword=${encodeURIComponent(keyword)}`;
    let data;
    try {
      data = await api.get(`/attractions?${q}`);
    } catch (e) {
      grid.innerHTML = `<div class="empty">加载失败：${escapeHtml(e.message)}</div>`;
      pager.innerHTML = "";
      return;
    }
    if (data.items.length === 0) {
      grid.innerHTML = `<div class="empty">暂无景点数据</div>`;
      pager.innerHTML = "";
      return;
    }
    grid.innerHTML = data.items.map((a) => `
      <div class="card">
        <img src="${escapeHtml(a.image_url || "")}" onerror="this.style.display='none'" alt="${escapeHtml(a.name)}">
        <div class="card-body">
          <h3>${escapeHtml(a.name)}</h3>
          <div class="meta">${escapeHtml(a.ticket_price)} · ${escapeHtml(a.open_time)}</div>
          <p class="desc">${escapeHtml(a.description)}</p>
          <div class="actions">
            <button class="btn" onclick="location.hash='#/attractions/${a.id}'">查看详情</button>
            <button class="btn ${FavoriteView.isFaved("attraction", a.id) ? "faved" : ""}" onclick="FavoriteView.toggle('attraction', ${a.id}, this)">${FavoriteView.isFaved("attraction", a.id) ? "已收藏" : "收藏"}</button>
          </div>
        </div>
      </div>`).join("");
    const totalPages = Math.ceil(data.total / data.page_size) || 1;
    pager.innerHTML = `<button class="btn-gray" id="pg-prev" ${page <= 1 ? "disabled" : ""}>上一页</button><span>第 ${page} / ${totalPages} 页</span><button class="btn-gray" id="pg-next" ${page >= totalPages ? "disabled" : ""}>下一页</button>`;
    if (page > 1) pager.querySelector("#pg-prev").onclick = () => this._load(page - 1, keyword);
    if (page < totalPages) pager.querySelector("#pg-next").onclick = () => this._load(page + 1, keyword);
  },

  async detail(id) {
    const view = document.getElementById("view");
    await FavoriteView.sync();
    let a;
    try {
      a = await api.get(`/attractions/${id}`);
    } catch (e) {
      view.innerHTML = `<div class="empty">加载失败：${escapeHtml(e.message)}</div>`;
      return;
    }
    view.innerHTML = `
      <div class="detail">
        <h2>${escapeHtml(a.name)}</h2>
        <div class="meta">开放时间 ${escapeHtml(a.open_time)} · 门票 ${escapeHtml(a.ticket_price)}</div>
        <img src="${escapeHtml(a.image_url || "")}" onerror="this.style.display='none'" alt="${escapeHtml(a.name)}">
        <p>${escapeHtml(a.description)}</p>
        <div class="actions">
          <button class="btn ${FavoriteView.isFaved("attraction", a.id) ? "faved" : ""}" id="fav-btn">${FavoriteView.isFaved("attraction", a.id) ? "已收藏" : "收藏"}</button>
        </div>
      </div>`;
    document.getElementById("fav-btn").onclick = (ev) => FavoriteView.toggle("attraction", a.id, ev.currentTarget);
  },
};

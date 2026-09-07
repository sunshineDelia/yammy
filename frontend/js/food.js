const FoodView = {
  async list() {
    const view = document.getElementById("view");
    view.innerHTML = `
      <div class="searchbar">
        <input id="food-kw" placeholder="搜索美食（名称/简介）">
        <button class="btn" id="food-search">搜索</button>
      </div>
      <div id="food-grid" class="card-grid"><div class="loading">加载中…</div></div>
      <div id="food-pager" class="pager"></div>`;
    await FavoriteView.sync();
    await this._load(1);
    document.getElementById("food-search").onclick = () => this._load(1, document.getElementById("food-kw").value);
  },

  async _load(page, keyword = "") {
    const grid = document.getElementById("food-grid");
    const pager = document.getElementById("food-pager");
    const q = `page=${page}&page_size=9&keyword=${encodeURIComponent(keyword)}`;
    let data;
    try {
      data = await api.get(`/foods?${q}`);
    } catch (e) {
      grid.innerHTML = `<div class="empty">加载失败：${escapeHtml(e.message)}</div>`;
      pager.innerHTML = "";
      return;
    }
    if (data.items.length === 0) {
      grid.innerHTML = `<div class="empty">暂无美食数据</div>`;
      pager.innerHTML = "";
      return;
    }
    grid.innerHTML = data.items.map((f) => `
      <div class="card">
        <img src="${escapeHtml(f.image_url || "")}" onerror="this.style.display='none'" alt="${escapeHtml(f.name)}">
        <div class="card-body">
          <h3>${escapeHtml(f.name)}</h3>
          <div class="meta">人均 ¥${escapeHtml(f.avg_price)}</div>
          <p class="desc">${escapeHtml(f.description)}</p>
          <div class="actions">
            <button class="btn" onclick="location.hash='#/foods/${f.id}'">查看详情</button>
            <button class="btn ${FavoriteView.isFaved("food", f.id) ? "faved" : ""}" onclick="FavoriteView.toggle('food', ${f.id}, this)">${FavoriteView.isFaved("food", f.id) ? "已收藏" : "收藏"}</button>
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
    let f;
    try {
      f = await api.get(`/foods/${id}`);
    } catch (e) {
      view.innerHTML = `<div class="empty">加载失败：${escapeHtml(e.message)}</div>`;
      return;
    }
    view.innerHTML = `
      <div class="detail">
        <h2>${escapeHtml(f.name)}</h2>
        <div class="meta">人均 ¥${escapeHtml(f.avg_price)}</div>
        <img src="${escapeHtml(f.image_url || "")}" onerror="this.style.display='none'" alt="${escapeHtml(f.name)}">
        <p>${escapeHtml(f.description)}</p>
        <div class="stores"><strong>推荐门店：</strong><ul>${f.stores.map((s) => `<li>${escapeHtml(s.name)}${s.address ? "（" + escapeHtml(s.address) + "）" : ""}</li>`).join("") || "<li>暂无</li>"}</ul></div>
        <div class="actions">
          <button class="btn ${FavoriteView.isFaved("food", f.id) ? "faved" : ""}" id="fav-btn">${FavoriteView.isFaved("food", f.id) ? "已收藏" : "收藏"}</button>
        </div>
      </div>`;
    document.getElementById("fav-btn").onclick = (ev) => FavoriteView.toggle("food", f.id, ev.currentTarget);
  },
};

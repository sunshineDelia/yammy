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
    document.getElementById("att-kw").addEventListener("keydown", (e) => {
      if (e.key === "Enter") this._load(1, e.target.value);
    });
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
        ${a.image_url ? `<img src="${escapeHtml(a.image_url)}" onerror="this.style.display='none'" alt="${escapeHtml(a.name)}">` : ""}
        <div class="card-body">
          <div class="badges">${a.level ? `<span class="badge category">${escapeHtml(a.level)}</span>` : ""}</div>
          <h3>${escapeHtml(a.name)}</h3>
          <div class="rating">${renderStars(a.rating)}<span class="score">${a.rating}</span><span class="count">${a.rating_count}条</span></div>
          <div class="meta">${escapeHtml(a.ticket_price)} · ${escapeHtml(a.open_time)}</div>
          <p class="desc">${escapeHtml(a.description)}</p>
          <div class="badges">${(a.tags || []).map((t) => `<span class="badge">${escapeHtml(t)}</span>`).join("")}</div>
          <div class="actions">
            <button class="btn" onclick="location.hash='#/attractions/${a.id}'">查看详情</button>
            <button class="btn ${FavoriteView.isFaved("attraction", a.id) ? "faved" : ""}" onclick="FavoriteView.toggle('attraction', ${a.id}, this)">${FavoriteView.isFaved("attraction", a.id) ? "已收藏" : "收藏"}</button>
          </div>
        </div>
      </div>`).join("");
    const totalPages = Math.ceil(data.total / data.page_size) || 1;
    pager.innerHTML = `<button class="btn-gray" id="pg-prev" ${page <= 1 ? "disabled" : ""}>上一页</button><span>第 ${page} / ${totalPages} 页 · 共 ${data.total} 条</span><button class="btn-gray" id="pg-next" ${page >= totalPages ? "disabled" : ""}>下一页</button>`;
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
        <div class="rating-row">${renderStars(a.rating)}<span class="score">${a.rating} 分</span><span>${a.rating_count} 条评价</span></div>
        ${a.image_url ? `<img class="hero-img" src="${escapeHtml(a.image_url)}" onerror="this.style.display='none'" alt="${escapeHtml(a.name)}">` : ""}
        <div class="info-grid">
          <div class="info-item"><div class="label">开放时间</div><div class="value">${escapeHtml(a.open_time)}</div></div>
          <div class="info-item"><div class="label">门票</div><div class="value">${escapeHtml(a.ticket_price)}</div></div>
          <div class="info-item"><div class="label">景区等级</div><div class="value">${escapeHtml(a.level || "暂无")}</div></div>
          <div class="info-item"><div class="label">建议时长</div><div class="value">${escapeHtml(a.duration || "暂无")}</div></div>
          <div class="info-item"><div class="label">地址</div><div class="value">${escapeHtml(a.address || "暂无")}</div></div>
        </div>
        <p>${escapeHtml(a.description)}</p>
        <div class="badges" style="margin-top:12px">${(a.tags || []).map((t) => `<span class="badge">${escapeHtml(t)}</span>`).join("")}</div>
        <div class="actions" style="margin-top:20px">
          <button class="btn ${FavoriteView.isFaved("attraction", a.id) ? "faved" : ""}" id="fav-btn">${FavoriteView.isFaved("attraction", a.id) ? "已收藏" : "收藏"}</button>
        </div>
      </div>`;
    document.getElementById("fav-btn").onclick = (ev) => FavoriteView.toggle("attraction", a.id, ev.currentTarget);
  },
};

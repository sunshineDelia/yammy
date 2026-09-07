const FavoriteView = {
  _cache: { food: new Set(), attraction: new Set() },

  isFaved(type, id) {
    return this._cache[type] && this._cache[type].has(String(id));
  },

  async toggle(type, id, btn) {
    const key = type === "food" ? "food" : "attraction";
    try {
      if (this.isFaved(key, id)) {
        await api.del(`/favorites/${type}/${id}`);
        this._cache[key].delete(String(id));
        if (btn) { btn.textContent = "收藏"; btn.classList.remove("faved"); }
      } else {
        await api.post("/favorites", { target_type: type, target_id: id });
        this._cache[key].add(String(id));
        if (btn) { btn.textContent = "已收藏"; btn.classList.add("faved"); }
      }
    } catch (e) {
      alert(e.message);
    }
  },

  async list() {
    const view = document.getElementById("view");
    view.innerHTML = `<div class="card-grid" id="fav-grid"><div class="loading">加载中…</div></div>`;
    const data = await api.get("/favorites?page=1&page_size=100");
    const grid = document.getElementById("fav-grid");
    if (data.items.length === 0) {
      grid.innerHTML = `<div class="empty">暂无收藏</div>`;
      return;
    }
    grid.innerHTML = data.items.map((it) => {
      const obj = it.food || it.attraction;
      const isFood = !!it.food;
      return `
        <div class="card">
          <div class="card-body">
            <h3>${obj.name}</h3>
            <div class="meta">${isFood ? "人均 ¥" + obj.avg_price : obj.ticket_price}</div>
            <div class="actions">
              <button class="btn" onclick="location.hash='#/${isFood ? "foods" : "attractions"}/${obj.id}'">查看</button>
              <button class="btn faved" onclick="FavoriteView.toggle('${isFood ? "food" : "attraction"}', ${obj.id}, this)">取消收藏</button>
            </div>
          </div>
        </div>`;
    }).join("");
  },
};

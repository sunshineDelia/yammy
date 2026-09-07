const AIView = {
  render() {
    const view = document.getElementById("view");
    view.innerHTML = `
      <div class="chat-box">
        <h2 style="margin-bottom:12px">AI 游玩咨询</h2>
        <textarea id="ai-question" placeholder="例如：帮我规划一天南昌美食行程"></textarea>
        <div style="margin-top:10px"><button class="btn" id="ai-ask">提问</button></div>
        <div id="ai-answer"></div>
      </div>`;
    document.getElementById("ai-ask").onclick = () => this.ask();
  },

  async ask() {
    const q = document.getElementById("ai-question").value.trim();
    const box = document.getElementById("ai-answer");
    if (!q) { box.innerHTML = `<div class="empty">请输入问题</div>`; return; }
    box.innerHTML = `<div class="loading">正在思考…</div>`;
    try {
      const data = await api.post("/ai/consult", { question: q });
      const refs = [
        ...(data.references?.foods || []).map((f) => `<button class="btn-gray" onclick="location.hash='#/foods/${f.id}'">🍜 ${escapeHtml(f.name)}</button>`),
        ...(data.references?.attractions || []).map((a) => `<button class="btn-gray" onclick="location.hash='#/attractions/${a.id}'">🏞️ ${escapeHtml(a.name)}</button>`),
      ].join(" ");
      box.innerHTML = `<div class="chat-answer">${escapeHtml(data.answer)}</div>${refs ? `<div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">相关推荐：${refs}</div>` : ""}`;
    } catch (e) {
      box.innerHTML = `<div class="empty">加载失败：${escapeHtml(e.message)}</div>`;
    }
  },
};

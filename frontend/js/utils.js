function getDeviceId() {
  let id = localStorage.getItem("device_id");
  if (!id) {
    id = (crypto.randomUUID && crypto.randomUUID())
      || ("dev-" + Date.now() + "-" + Math.random().toString(16).slice(2));
    localStorage.setItem("device_id", id);
  }
  return id;
}

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function showToast(msg) {
  let t = document.getElementById("toast");
  if (!t) {
    t = document.createElement("div");
    t.id = "toast";
    t.style.cssText = "position:fixed;top:16px;left:50%;transform:translateX(-50%);background:#c0392b;color:#fff;padding:10px 18px;border-radius:6px;z-index:999;box-shadow:0 2px 8px rgba(0,0,0,.2);";
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.display = "block";
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.display = "none"; }, 3000);
}

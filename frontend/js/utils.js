function getDeviceId() {
  let id = localStorage.getItem("device_id");
  if (!id) {
    id = (crypto.randomUUID && crypto.randomUUID())
      || ("dev-" + Date.now() + "-" + Math.random().toString(16).slice(2));
    localStorage.setItem("device_id", id);
  }
  return id;
}

function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

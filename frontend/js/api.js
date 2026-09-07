const API_BASE = "http://localhost:8000/api";

async function request(method, path, body) {
  const headers = { "X-Device-Id": getDeviceId() };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const resp = await fetch(API_BASE + path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (resp.status === 204) return null;
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.detail || "请求失败");
  return data;
}

const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  del: (path) => request("DELETE", path),
};

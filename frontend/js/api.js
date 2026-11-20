const SESSION_KEY = "session_id";

function setSession(sessionId) {
  if (sessionId) {
    sessionStorage.setItem(SESSION_KEY, sessionId);
  } else {
    sessionStorage.removeItem(SESSION_KEY);
  }

  document.dispatchEvent(new Event("sessionchange"));
}

async function apiRequest(path, method = "GET", body) {
  const url = new URL(path, location.origin);
  if (url.origin !== location.origin) {
    throw new Error("API requests must use the same origin.");
  }

  const sessionId = sessionStorage.getItem(SESSION_KEY);
  const headers = {};

  if (sessionId) headers.Authorization = `Bearer ${sessionId}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const response = await fetch(url, {
    method,
    headers,
    body: JSON.stringify(body),
  });

  if (
    response.status === 401 &&
    sessionId &&
    sessionStorage.getItem(SESSION_KEY) === sessionId
  ) {
    setSession(null);
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map(({ loc, msg }) => `${loc.slice(1).join(".")}: ${msg}`).join(" ")
      : detail || response.statusText;
    const error = new Error(`${response.status}: ${message}`);
    error.status = response.status;
    throw error;
  }

  return data;
}

function apiGet(path) {
  return apiRequest(path);
}

function apiPost(path, body) {
  return apiRequest(path, "POST", body);
}

function apiPatch(path, body) {
  return apiRequest(path, "PATCH", body);
}

function apiDelete(path) {
  return apiRequest(path, "DELETE");
}
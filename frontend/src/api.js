import axios from "axios";

const API_ROOT = "/api";
const api = axios.create({
  baseURL: API_ROOT,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

let refreshPromise = null;

api.interceptors.request.use((config) => {
  const access = sessionStorage.getItem("erp.access");
  if (access) {
    config.headers = config.headers || {};
    config.headers.Authorization = "Bearer " + access;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config || {};
    const isAuthCall = String(original.url || "").includes("/auth/token");
    if (error.response?.status !== 401 || original._retry || isAuthCall) {
      return Promise.reject(error);
    }

    original._retry = true;
    const refresh = sessionStorage.getItem("erp.refresh");
    if (!refresh) {
      sessionStorage.removeItem("erp.access");
      sessionStorage.removeItem("erp.refresh");
      window.dispatchEvent(new Event("erp:unauthorized"));
      return Promise.reject(error);
    }

    try {
      if (!refreshPromise) {
        refreshPromise = axios
          .post(API_ROOT + "/auth/token/refresh/", { refresh }, { timeout: 15000 })
          .then(({ data }) => {
            sessionStorage.setItem("erp.access", data.access);
            if (data.refresh) sessionStorage.setItem("erp.refresh", data.refresh);
            return data.access;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }
      const access = await refreshPromise;
      original.headers = original.headers || {};
      original.headers.Authorization = "Bearer " + access;
      return api(original);
    } catch (refreshError) {
      sessionStorage.removeItem("erp.access");
      sessionStorage.removeItem("erp.refresh");
      window.dispatchEvent(new Event("erp:unauthorized"));
      return Promise.reject(refreshError);
    }
  }
);

export function listData(payload) {
  if (Array.isArray(payload)) return payload;
  return Array.isArray(payload?.results) ? payload.results : [];
}

export async function fetchAll(url, maxPages = 100) {
  const rows = [];
  const visited = new Set();
  let next = url;

  while (next && visited.size < maxPages && !visited.has(next)) {
    visited.add(next);
    const { data } = await api.get(next);
    rows.push(...listData(data));
    next = Array.isArray(data) ? null : data?.next || null;
  }

  if (next && visited.size >= maxPages) {
    throw new Error("Result set exceeded the safe pagination limit.");
  }
  return rows;
}

const financeApi = axios.create({
  baseURL: "/platform/finance",
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

function attachInterceptors(client) {
  client.interceptors.request.use((config) => {
    const access = sessionStorage.getItem("erp.access");
    if (access) {
      config.headers = config.headers || {};
      config.headers.Authorization = "Bearer " + access;
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const original = error.config || {};
      const isAuthCall = String(original.url || "").includes("/auth/token");
      if (error.response?.status !== 401 || original._retry || isAuthCall) {
        return Promise.reject(error);
      }

      original._retry = true;
      const refresh = sessionStorage.getItem("erp.refresh");
      if (!refresh) {
        sessionStorage.removeItem("erp.access");
        sessionStorage.removeItem("erp.refresh");
        window.dispatchEvent(new Event("erp:unauthorized"));
        return Promise.reject(error);
      }

      try {
        if (!refreshPromise) {
          refreshPromise = axios
            .post(API_ROOT + "/auth/token/refresh/", { refresh }, { timeout: 15000 })
            .then(({ data }) => {
              sessionStorage.setItem("erp.access", data.access);
              if (data.refresh) sessionStorage.setItem("erp.refresh", data.refresh);
              return data.access;
            })
            .finally(() => {
              refreshPromise = null;
            });
        }
        const access = await refreshPromise;
        original.headers = original.headers || {};
        original.headers.Authorization = "Bearer " + access;
        return client(original);
      } catch (refreshError) {
        sessionStorage.removeItem("erp.access");
        sessionStorage.removeItem("erp.refresh");
        window.dispatchEvent(new Event("erp:unauthorized"));
        return Promise.reject(refreshError);
      }
    }
  );
}

attachInterceptors(financeApi);

export { financeApi };
export default api;

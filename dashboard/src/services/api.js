const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function safeFetch(path, opts) {
  const res = await fetch(`${BASE}${path}`, opts)
  const text = await res.text()
  const data = text ? JSON.parse(text) : null
  if (!res.ok) {
    const msg = (data && data.detail) ? data.detail : (data && data.error) ? data.error : `HTTP ${res.status}`
    throw new Error(msg)
  }
  return data
}

export function getHealth() {
  return safeFetch('/health')
}

export function getProvinces() {
  return safeFetch('/provinces')
}

export function forecast(payload) {
  return safeFetch('/forecast', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
}

export function predict(payload) {
  return safeFetch('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
}

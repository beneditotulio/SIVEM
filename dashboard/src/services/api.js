const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function getHealth() {
  const r = await fetch(`${BASE_URL}/health`)
  if (!r.ok) throw new Error('Falha no health')
  return r.json()
}

export async function predict(payload) {
  const r = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!r.ok) throw new Error('Falha no predict')
  return r.json()
}

export async function getProvinces() {
  const r = await fetch(`${BASE_URL}/provinces`)
  if (!r.ok) throw new Error('Falha em provinces')
  return r.json()
}

export async function forecast(payload) {
  const r = await fetch(`${BASE_URL}/forecast`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!r.ok) throw new Error('Falha no forecast')
  return r.json()
}

export { BASE_URL }

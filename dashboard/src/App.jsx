import React, { useEffect, useState } from 'react'
import { getHealth, predict } from './services/api.js'

export default function App() {
  const [status, setStatus] = useState('...')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getHealth()
      .then(d => setStatus(d.status))
      .catch(() => setStatus('erro'))
  }, [])

  const onPredict = async () => {
    setError(null)
    setResult(null)
    try {
      const r = await predict({ registered_cases: 5, baleamentos: 1, detencoes: 0, mortes: 0, province: 'Maputo' })
      setResult(r)
    } catch (e) {
      setError(String(e))
    }
  }

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h1>SIVEM Dashboard</h1>
      <p>API status: {status}</p>
      <button onClick={onPredict}>Testar previsão</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
      {error && <div>Erro: {error}</div>}
    </div>
  )
}


import React, { useEffect, useState } from 'react'
import { getHealth, getProvinces, forecast } from './services/api.js'

export default function App() {
  const [status, setStatus] = useState('...')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [provinces, setProvinces] = useState([])
  const [province, setProvince] = useState('')
  const [year, setYear] = useState(new Date().getFullYear())

  useEffect(() => {
    getHealth()
      .then(d => setStatus(d.status))
      .catch(() => setStatus('erro'))
    getProvinces()
      .then(d => setProvinces(d.provinces || []))
      .catch(() => setProvinces([]))
  }, [])

  const onForecast = async () => {
    setError(null)
    setResult(null)
    try {
      if (!province) throw new Error('Selecione a provincia')
      const r = await forecast({ province, year: Number(year) })
      setResult(r)
    } catch (e) {
      setError(String(e))
    }
  }

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif', display: 'grid', gap: 12 }}>
      <h1>SIVEM Dashboard</h1>
      <p>API status: {status}</p>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <label>
          Província
          <select value={province} onChange={e => setProvince(e.target.value)} style={{ marginLeft: 8 }}>
            <option value="">Selecione</option>
            {provinces.map(p => (<option key={p} value={p}>{p}</option>))}
          </select>
        </label>
        <label>
          Ano
          <input type="number" value={year} onChange={e => setYear(e.target.value)} style={{ marginLeft: 8, width: 100 }} />
        </label>
        <button onClick={onForecast}>Gerar previsão</button>
      </div>
      {result && (
        <div>
          <h2>Resultado</h2>
          <div>Província: {result.province}</div>
          <div>Ano: {result.year}</div>
          <div>Probabilidade (modelo): {result.probability !== null && result.probability !== undefined ? result.probability.toFixed(3) : 'N/A'}</div>
          <div>Previsão binária: {result.prediction === null || result.prediction === undefined ? 'N/A' : result.prediction}</div>
          <div>Casos médios registados: {result.registered_cases_mean?.toFixed ? result.registered_cases_mean.toFixed(2) : result.registered_cases_mean}</div>
          <h3>Contagens esperadas</h3>
          <ul>
            <li>Baleamentos: {result.expected_counts?.baleamentos}</li>
            <li>Detenções: {result.expected_counts?.detencoes}</li>
            <li>Mortes: {result.expected_counts?.mortes}</li>
          </ul>
        </div>
      )}
      {error && <div>Erro: {error}</div>}
    </div>
  )
}

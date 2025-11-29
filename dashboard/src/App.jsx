import React, { useEffect, useState } from 'react'
import { BASE, getHealth, getProvinces, forecast, predict } from './services/api.js'
import BarChart from './components/BarChart.jsx'
import RiskBadge from './components/RiskBadge.jsx'
import './styles.css'

export default function App() {
  const defaultProvinces = ['Cabo Delgado','Gaza','Inhambane','Manica','Maputo','Maputo Provincia','Nampula','Niassa','Sofala','Tete','Zambezia']
  const [status, setStatus] = useState('...')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [provinces, setProvinces] = useState([])
  const [province, setProvince] = useState('')
  const [year, setYear] = useState(new Date().getFullYear())
  const [loadingProv, setLoadingProv] = useState(false)
  const [loadingForecast, setLoadingForecast] = useState(false)
  const [loadingPredict, setLoadingPredict] = useState(false)
  const [scenario, setScenario] = useState({ registered_cases: 5, baleamentos: 1, detencoes: 0, mortes: 0 })

  useEffect(() => {
    getHealth()
      .then(d => setStatus(d.status))
      .catch(() => setStatus('erro'))
    setLoadingProv(true)
    getProvinces()
      .then(d => setProvinces((d.provinces && d.provinces.length > 0) ? d.provinces : defaultProvinces))
      .catch(() => setProvinces(defaultProvinces))
      .finally(() => setLoadingProv(false))
  }, [])

  const onForecast = async () => {
    setError(null)
    setResult(null)
    try {
      if (!province) throw new Error('Selecione a provincia')
      setLoadingForecast(true)
      const r = await forecast({ province, year: Number(year) })
      setResult(r)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoadingForecast(false)
    }
  }

  const onPredict = async () => {
    setError(null)
    try {
      if (!province) throw new Error('Selecione a provincia')
      setLoadingPredict(true)
      const r = await predict({ ...scenario, province })
      setResult({ province, year: Number(year), probability: r.probability, prediction: r.prediction })
    } catch (e) {
      setError(String(e))
    } finally {
      setLoadingPredict(false)
    }
  }

  // moved inside component so it can access state setters
  const onReload = async () => {
    setStatus('...')
    try {
      const d = await getHealth()
      setStatus(d.status)
    } catch {
      setStatus('erro')
    }
    setLoadingProv(true)
    try {
      const d = await getProvinces()
      setProvinces((d.provinces && d.provinces.length > 0) ? d.provinces : defaultProvinces)
    } catch {
      setProvinces(defaultProvinces)
    } finally {
      setLoadingProv(false)
    }
  }

  const openReport = () => {
    const url = `${BASE}/incidentes_report.html`
    window.open(url, '_blank', 'noopener')
  }

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif', display: 'grid', gap: 16 }}>
      <h1>SIVEM Dashboard</h1>
      <p>
        API status: {status}
        <button onClick={onReload} style={{ marginLeft: 8 }}>Recarregar</button>
        <button onClick={openReport} style={{ marginLeft: 8 }}>Relatório pré-processamento</button>
      </p>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <label>
          Província
          <select value={province} onChange={e => setProvince(e.target.value)} style={{ marginLeft: 8 }} disabled={loadingProv || (status !== 'ok' && provinces.length === 0)}>
            <option value="">Selecione</option>
            {provinces.map(p => (<option key={p} value={p}>{p}</option>))}
          </select>
        </label>
        <label>
          Ano
          <input type="number" value={year} onChange={e => setYear(e.target.value)} style={{ marginLeft: 8, width: 100 }} />
        </label>
        <button onClick={onForecast} disabled={loadingForecast || status !== 'ok'}>{loadingForecast ? 'A gerar...' : 'Gerar previsão'}</button>
      </div>
      <div style={{ display: 'grid', gap: 8, gridTemplateColumns: '1fr 1fr' }}>
        <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
          <h2>Previsão por histórico</h2>
          {result && (
            <div style={{ display: 'grid', gap: 8 }}>
              <div>Província: {result.province}</div>
              <div>Ano: {result.year}</div>
              <div>Risco: <RiskBadge probability={result.probability} /></div>
              <div>Casos médios registados: {result.registered_cases_mean?.toFixed ? result.registered_cases_mean.toFixed(2) : (result.registered_cases_mean ?? 'N/A')}</div>
              {result.expected_counts && (
                <div>
                  <h3>Contagens esperadas</h3>
                  <BarChart data={[
                    { label: 'Baleamentos', value: result.expected_counts.baleamentos || 0 },
                    { label: 'Detenções', value: result.expected_counts.detencoes || 0 },
                    { label: 'Mortes', value: result.expected_counts.mortes || 0 },
                  ]} />
                </div>
              )}
            </div>
          )}
        </div>
        <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
          <h2>Análise de cenário</h2>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            <label>Casos <input type="number" value={scenario.registered_cases} onChange={e => setScenario(s => ({ ...s, registered_cases: Number(e.target.value) }))} style={{ width: 100 }} /></label>
            <label>Baleamentos <input type="checkbox" checked={!!scenario.baleamentos} onChange={e => setScenario(s => ({ ...s, baleamentos: e.target.checked ? 1 : 0 }))} /></label>
            <label>Detenções <input type="checkbox" checked={!!scenario.detencoes} onChange={e => setScenario(s => ({ ...s, detencoes: e.target.checked ? 1 : 0 }))} /></label>
            <label>Mortes <input type="checkbox" checked={!!scenario.mortes} onChange={e => setScenario(s => ({ ...s, mortes: e.target.checked ? 1 : 0 }))} /></label>
            <button onClick={onPredict} disabled={loadingPredict || status !== 'ok'}>{loadingPredict ? 'A calcular...' : 'Calcular risco'}</button>
          </div>
        </div>
      </div>
      {result && (
        <div>
          <h2>Detalhes</h2>
          <div>Probabilidade (modelo): {typeof result.probability === 'number' ? result.probability.toFixed(3) : 'N/A'}</div>
          <div>Previsão binária: {result.prediction === null || result.prediction === undefined ? 'N/A' : result.prediction}</div>
        </div>
      )}
      {error && <div>Erro: {error}</div>}
    </div>
  )
}

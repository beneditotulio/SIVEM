import React from 'react'

export default function BarChart({ data }) {
  const max = Math.max(...data.map(d => d.value), 1)
  return (
    <div style={{ display: 'grid', gap: 8 }}>
      {data.map(d => (
        <div key={d.label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 140 }}>{d.label}</div>
          <div style={{ flex: 1, background: '#eee', height: 16, position: 'relative' }}>
            <div style={{ width: `${(d.value / max) * 100}%`, background: '#2a7', height: '100%' }} />
          </div>
          <div style={{ width: 48, textAlign: 'right' }}>{d.value}</div>
        </div>
      ))}
    </div>
  )
}

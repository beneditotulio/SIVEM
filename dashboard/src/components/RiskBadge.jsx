import React from 'react'

export default function RiskBadge({ probability }) {
  let label = 'Indisponível'
  let bg = '#bbb'
  if (typeof probability === 'number') {
    if (probability < 0.33) { label = 'Baixo'; bg = '#2a7' }
    else if (probability < 0.66) { label = 'Médio'; bg = '#e6b800' }
    else { label = 'Alto'; bg = '#d33' }
  }
  return (
    <span style={{ padding: '4px 8px', background: bg, color: '#fff', borderRadius: 6 }}>{label}</span>
  )
}

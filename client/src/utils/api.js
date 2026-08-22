const API_BASE = import.meta.env.VITE_API_URL || ''

export async function submitImage(file, basePrice, stockEntryDate) {
  const form = new FormData()
  form.append('image', file)
  form.append('base_price', String(basePrice))
  form.append('stock_entry_date', stockEntryDate)

  const res = await fetch(`${API_BASE}/api/v1/price-recommendation`, {
    method: 'POST',
    body: form,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const message = body?.detail || `Request failed (${res.status})`
    throw new Error(message)
  }

  return res.json()
}

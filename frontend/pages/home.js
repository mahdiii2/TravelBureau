import { useState, useEffect } from 'react'

export default function HomePage() {
  const [contracts, setContracts] = useState([])
  const [showUpload, setShowUpload] = useState(false)
  const [country, setCountry] = useState('')
  const [hotel, setHotel] = useState('')
  const [file, setFile] = useState(null)

  useEffect(() => {
    fetch('/get-hotel-contracts').then(r => r.json()).then(setContracts)
  }, [])

  const handleUpload = async () => {
    if (!file) return
    const form = new FormData()
    form.append('country', country)
    form.append('hotel', hotel)
    form.append('file', file)
    await fetch('/upload-file', { method: 'POST', body: form })
    setShowUpload(false)
  }

  return (
    <div>
      <button onClick={() => setShowUpload(v => !v)}>Upload Data</button>
      {showUpload && (
        <div className="popover">
          <input placeholder="Country" value={country} onChange={e => setCountry(e.target.value)} />
          <input placeholder="Hotel" value={hotel} onChange={e => setHotel(e.target.value)} />
          <input type="file" onChange={e => setFile(e.target.files[0])} />
          <button onClick={handleUpload}>Submit</button>
        </div>
      )}
      <table>
        <thead>
          <tr>
            <th>Hotel</th>
            <th>Category</th>
            <th>Currency</th>
          </tr>
        </thead>
        <tbody>
          {contracts.map(c => (
            <tr key={c.id}>
              <td>{c.hotelName}</td>
              <td>{c.category}</td>
              <td>{c.currency}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

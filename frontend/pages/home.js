import { useState, useEffect } from 'react'
import * as Popover from '@radix-ui/react-popover'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'

export default function HomePage() {
  const [contracts, setContracts] = useState([])
  const [open, setOpen] = useState(false)
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
    setOpen(false)
    setCountry('')
    setHotel('')
    setFile(null)
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-end">
        <Popover.Root open={open} onOpenChange={setOpen}>
          <Popover.Trigger asChild>
            <Button>Upload Data</Button>
          </Popover.Trigger>
          <Popover.Portal>
            <Popover.Content className="rounded-md border bg-white p-4 shadow-md space-y-2 w-72">
              <Input placeholder="Country" value={country} onChange={e => setCountry(e.target.value)} />
              <Input placeholder="Hotel" value={hotel} onChange={e => setHotel(e.target.value)} />
              <Input type="file" onChange={e => setFile(e.target.files[0])} />
              <Button className="w-full" onClick={handleUpload}>Submit</Button>
            </Popover.Content>
          </Popover.Portal>
        </Popover.Root>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hotel</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Currency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {contracts.map(c => (
              <tr key={c.id} className="bg-white">
                <td className="px-6 py-4 whitespace-nowrap">{c.hotelName}</td>
                <td className="px-6 py-4 whitespace-nowrap">{c.category}</td>
                <td className="px-6 py-4 whitespace-nowrap">{c.currency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

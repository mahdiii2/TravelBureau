import { useState, useEffect } from 'react'
import * as Popover from '@radix-ui/react-popover'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'

export default function HomePage() {
  const [contracts, setContracts] = useState([])
  const [open, setOpen] = useState(false)
  const [country, setCountry] = useState('')
  const [countryInfo, setCountryInfo] = useState(null)
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
            <Popover.Content sideOffset={8} className="rounded-md border bg-white p-4 shadow-md space-y-2 w-72">
              <Input
                placeholder="Country"
                value={country}
                onChange={async e => {
                  const val = e.target.value
                  setCountry(val)
                  if (val.trim()) {
                    const res = await fetch(`/search-countries?query=${encodeURIComponent(val)}`)
                    setCountryInfo(await res.json())
                  }
                }}
              />
              <Input
                placeholder="Hotel"
                value={hotel}
                onChange={async e => {
                  const val = e.target.value
                  setHotel(val)
                  if (val.trim()) {
                    const params = new URLSearchParams({
                      query: val,
                      cityCountry: countryInfo?.name || '',
                      cityCode: countryInfo?.code || ''
                    })
                    await fetch(`/search-hotels?${params.toString()}`)
                  }
                }}
              />
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Room Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Adults</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Children</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Meal Plan</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Base Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Adults for Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Adult Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Children for Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Child Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {contracts.map(c => (
              <tr key={c.id} className="bg-white">
                <td className="px-6 py-4 break-words">{c.hotelName}</td>
                <td className="px-6 py-4 break-words">{c.category}</td>
                <td className="px-6 py-4 break-words">{c.currency}</td>
                <td className="px-6 py-4 break-words">{c.roomName}</td>
                <td className="px-6 py-4 break-words">{c.numAdults}</td>
                <td className="px-6 py-4 break-words">{c.numChildren}</td>
                <td className="px-6 py-4 break-words">{c.mealPlan}</td>
                <td className="px-6 py-4 break-words">{c.name}</td>
                <td className="px-6 py-4 break-words">{c.basePrice}</td>
                <td className="px-6 py-4 break-words">{c.numAdultsForPrice}</td>
                <td className="px-6 py-4 break-words">{c.adultPrice}</td>
                <td className="px-6 py-4 break-words">{c.numChildrenForPrice}</td>
                <td className="px-6 py-4 break-words">{c.childPrice}</td>
                <td className="px-6 py-4 break-words">{new Date(c.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

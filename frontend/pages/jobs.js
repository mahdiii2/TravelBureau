import { useEffect, useState } from 'react'

export default function JobsPage() {
  const [jobs, setJobs] = useState([])

  useEffect(() => {
    fetch('/get-hotel-contract-jobs').then(r => r.json()).then(setJobs)
  }, [])

  return (
    <div className="container mx-auto p-6">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">State</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {jobs.map(j => (
              <tr key={j.id} className="bg-white">
                <td className="px-6 py-4 whitespace-nowrap">{j.fileName}</td>
                <td className="px-6 py-4 whitespace-nowrap">{j.state}</td>
                <td className="px-6 py-4 whitespace-nowrap">{new Date(j.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

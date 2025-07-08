import { useEffect, useState } from 'react'

export default function JobsPage() {
  const [jobs, setJobs] = useState([])

  useEffect(() => {
    fetch('/get-hotel-contract-jobs').then(r => r.json()).then(setJobs)
  }, [])

  return (
    <table>
      <thead>
        <tr>
          <th>File</th>
          <th>State</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        {jobs.map(j => (
          <tr key={j.id}>
            <td>{j.fileName}</td>
            <td>{j.state}</td>
            <td>{new Date(j.createdAt).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

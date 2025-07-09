// pages/index.tsx
"use client"

import { useState, useEffect } from "react"
import Head from "next/head"
import * as Popover from "@radix-ui/react-popover"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableHeader,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
} from "@/components/ui/table"
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"

type Contract = {
  id: string | number
  hotelName: string
  category: string
  currency: string
  roomName: string
  numAdults: number
  numChildren: number
  mealPlan: string
  name: string
  basePrice: number
  numAdultsForPrice: number
  adultPrice: number
  numChildrenForPrice: number
  childPrice: number
  createdAt: string
}

const columns: ColumnDef<Contract>[] = [
  { accessorKey: "hotelName", header: "Hotel" },
  { accessorKey: "category", header: "Category" },
  { accessorKey: "currency", header: "Currency" },
  { accessorKey: "roomName", header: "Room Name" },
  { accessorKey: "numAdults", header: "Adults" },
  { accessorKey: "numChildren", header: "Children" },
  { accessorKey: "mealPlan", header: "Meal Plan" },
  { accessorKey: "name", header: "Name" },
  { accessorKey: "basePrice", header: "Base Price" },
  { accessorKey: "numAdultsForPrice", header: "Adults for Price" },
  { accessorKey: "adultPrice", header: "Adult Price" },
  { accessorKey: "numChildrenForPrice", header: "Children for Price" },
  { accessorKey: "childPrice", header: "Child Price" },
  {
    accessorKey: "createdAt",
    header: "Created",
    cell: info => new Date(info.getValue() as string).toLocaleString(),
  },
]

export default function HomePage() {
  const [contracts, setContracts] = useState<Contract[]>([])
  const [open, setOpen] = useState(false)
  const [country, setCountry] = useState("")
  const [countryInfo, setCountryInfo] = useState<any>(null)
  const [hotel, setHotel] = useState("")
  const [file, setFile] = useState<File | null>(null)

  useEffect(() => {
    fetch("/get-hotel-contracts")
      .then(r => r.json())
      .then(setContracts)
  }, [])

  const handleUpload = async () => {
    if (!file) return
    const form = new FormData()
    form.append("country", country)
    form.append("hotel", hotel)
    form.append("file", file)
    await fetch("/upload-file", { method: "POST", body: form })
    setOpen(false)
    setCountry("")
    setHotel("")
    setFile(null)
    const refreshed = await fetch("/get-hotel-contracts").then(r => r.json())
    setContracts(refreshed)
  }

  const table = useReactTable({
    data: contracts,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <>
      <Head>
        <title key="title">Hotel Contracts</title>
        <meta key="description" name="description" content="View and upload hotel contracts" />
      </Head>
      <div className="container mx-auto p-8 space-y-8">
        <div className="flex justify-end">
          <Popover.Root open={open} onOpenChange={setOpen}>
            <Popover.Trigger asChild>
              <Button>Upload Data</Button>
            </Popover.Trigger>
            <Popover.Portal>
              <Popover.Content sideOffset={8} className="w-80 rounded-lg border bg-white p-6 shadow-lg space-y-4">
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
                        cityCountry: countryInfo?.name || "",
                        cityCode: countryInfo?.code || "",
                      })
                      await fetch(`/search-hotels?${params.toString()}`)
                    }
                  }}
                />
                <Input type="file" onChange={e => setFile(e.target.files?.[0] ?? null)} />
                <Button className="w-full" onClick={handleUpload}>Submit</Button>
              </Popover.Content>
            </Popover.Portal>
          </Popover.Root>
        </div>
        <div className="rounded-lg border shadow overflow-x-auto">
          <Table className="w-full min-w-[800px]">
            <TableHeader className="bg-gray-100 sticky top-0">
              {table.getHeaderGroups().map(headerGroup => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map(header => (
                    <TableHead key={header.id} className="text-left py-2">
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows.length ? (
                table.getRowModel().rows.map(row => (
                  <TableRow key={row.id} className="hover:bg-gray-50">
                    {row.getVisibleCells().map(cell => (
                      <TableCell key={cell.id} className="py-3.5">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center">
                    No contracts.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </>
  )
}

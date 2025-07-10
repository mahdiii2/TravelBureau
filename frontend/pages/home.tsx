// pages/index.tsx
"use client"

import { useState, useEffect, useRef } from "react"
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
  const [countryOptions, setCountryOptions] = useState<
    { name: string; code: string; score: number }[]
  >([])
  const [countryInfo, setCountryInfo] = useState<{ name: string; code: string } | null>(null)
  const [hotel, setHotel] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState("")

  const countryInputRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetch("/get-hotel-contracts")
      .then(r => r.json())
      .then(setContracts)
  }, [])

  // close suggestions on click outside
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (
        countryInputRef.current &&
        !countryInputRef.current.contains(e.target as Node)
      ) {
        setCountryOptions([])
      }
    }
    document.addEventListener("click", handleClick)
    return () => document.removeEventListener("click", handleClick)
  }, [])

  const handleUpload = async () => {
    if (!country.trim() || !hotel.trim() || !file) {
      setError("⚠️ Please provide Country, Hotel and select a File.")
      return
    }
    setError("")

    const form = new FormData()
    form.append("country", country)
    form.append("hotel", hotel)
    form.append("file", file)

    await fetch("/upload-file", { method: "POST", body: form })

    setOpen(false)
    setCountry("")
    setCountryInfo(null)
    setCountryOptions([])
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

  const isReady = country.trim() && hotel.trim() && file

  return (
    <>
      <Head>
        <title key="title">Hotel Contracts</title>
        <meta
          key="description"
          name="description"
          content="View and upload hotel contracts"
        />
      </Head>
      <div className="container mx-auto p-8 space-y-8">
        <div className="flex justify-end">
          <Popover.Root open={open} onOpenChange={setOpen}>
            <Popover.Trigger asChild>
              <Button>Upload Data</Button>
            </Popover.Trigger>
            <Popover.Portal>
              <Popover.Content
                sideOffset={8}
                className="w-80 rounded-lg border bg-white p-6 shadow-lg space-y-4"
              >
                {/* Country input + suggestions */}
                <div className="relative" ref={countryInputRef}>
                  <Input
                    placeholder="Country"
                    value={country}
                    onChange={async e => {
                      const val = e.target.value
                      setCountry(val)
                      setCountryInfo(null)
                      setError("")

                      if (val.trim()) {
                        const res = await fetch(
                          `/search-countries?query=${encodeURIComponent(val)}`
                        )
                        const opts = await res.json()
                        setCountryOptions(opts)
                      } else {
                        setCountryOptions([])
                      }
                    }}
                  />
                  {countryOptions.length > 0 && (
                    <ul className="absolute z-10 w-full bg-white border rounded mt-1 max-h-40 overflow-auto">
                      {countryOptions.map(opt => (
                        <li
                          key={opt.code}
                          className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                          onClick={() => {
                            setCountry(opt.name)
                            setCountryInfo({ name: opt.name, code: opt.code })
                            setCountryOptions([])
                          }}
                        >
                          {opt.name}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Hotel text input */}
                <Input
                  placeholder="Hotel"
                  value={hotel}
                  onChange={e => {
                    setHotel(e.target.value)
                    setError("")
                  }}
                />

                {/* File picker */}
                <Input
                  type="file"
                  onChange={e => {
                    setFile(e.target.files?.[0] ?? null)
                    setError("")
                  }}
                />

                {error && (
                  <p className="text-sm text-red-600 font-medium">{error}</p>
                )}

                <Button
                  className={`
                    w-full
                    ${isReady
                      ? "bg-blue-600 hover:bg-blue-700 text-white"
                      : "bg-red-600 text-white opacity-75 cursor-not-allowed"}
                  `}
                  onClick={handleUpload}
                >
                  Submit
                </Button>
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
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows.length > 0 ? (
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

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { ScraperTable } from "./ScraperTable"
import { ScraperConfig } from "@/config/scraperConfig"
import { Download, Play, Search } from "lucide-react"

function downloadCSV(data: any[], columns: { key: string; label: string }[], filename: string) {
    if (!data.length) return

    // Use columns config to determine headers and order
    const headers = columns.map(col => col.label)
    const keys = columns.map(col => col.key)

    const csvRows = [
        headers.join(","), // Header row
        ...data.map(row =>
            keys.map(key => {
                const val = row[key] !== undefined && row[key] !== null ? row[key] : ""
                // Escape quotes and wrap in quotes if necessary. Replace newlines with space.
                const stringVal = String(val).replace(/"/g, '""').replace(/\n/g, ' ')
                return `"${stringVal}"`
            }).join(",")
        )
    ]

    const csvContent = csvRows.join("\n")
    // Add BOM for Excel UTF-8 support
    const BOM = "\uFEFF"
    const blob = new Blob([BOM + csvContent], { type: "text/csv;charset=utf-8;" })

    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.setAttribute("href", url)
    link.setAttribute("download", `${filename}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
}

interface GenericScraperProps {
    config: ScraperConfig
}

export function GenericScraper({ config }: GenericScraperProps) {
    const [query, setQuery] = useState("")
    const [limit, setLimit] = useState(10)
    const [results, setResults] = useState<any[]>([])
    const [loading, setLoading] = useState(false)

    const [error, setError] = useState<string | null>(null)

    // Reset state when scraper changes to prevent data leakage
    useEffect(() => {
        setResults([])
        setQuery("")
        setError(null)
    }, [config.id])

    const handleScrape = async () => {
        if (!query) return
        setLoading(true)
        setError(null)
        setResults([])

        if (!config.backendId) {
            // Fallback for demo if no backend id
            setTimeout(() => {
                const dummyData = Array.from({ length: limit }).map((_, i) => {
                    const row: any = {}
                    config.columns.forEach((col) => {
                        row[col.key] = `${col.label} ${i + 1} (${query}) - Mock Only`
                    })
                    return row
                })
                setResults(dummyData)
                setLoading(false)
            }, 2000)
            return
        }

        try {
            // Get userId from storage
            const savedUser = localStorage.getItem("user")
            const userId = savedUser ? JSON.parse(savedUser).userId : null

            const response = await fetch(`/api/live_scrape?platform=${config.backendId}&query=${encodeURIComponent(query)}&limit=${limit}&userId=${userId || ""}`)
            const data = await response.json()

            if (data.success && data.data) {
                setResults(data.data)
            } else {
                setError(data.error || "Scraping failed")
                setResults([])
            }
        } catch (err) {
            console.error("Scrape error:", err)
            setError("Failed to connect to backend. Ensure backend is running.")
            setResults([])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight text-primary">{config.name}</h1>
                <p className="text-muted-foreground">{config.description}</p>
            </div>

            <Card className="border-border bg-card shadow-sm">
                <CardHeader>
                    <CardTitle className="text-primary">Search Parameters</CardTitle>
                    <CardDescription>Enter your search query and limits to start scraping.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col md:flex-row gap-4 items-end">
                        <div className="grid w-full gap-2">
                            <label className="text-sm font-medium text-foreground">Search Query</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    className="pl-9 bg-input text-foreground border-input focus:ring-primary"
                                    placeholder="Enter keyword, company, topic..."
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="w-full md:w-32 gap-2">
                            <label className="text-sm font-medium text-foreground">Limit</label>
                            <Input
                                type="number"
                                min={1}
                                max={100}
                                value={limit}
                                onChange={(e) => setLimit(Number(e.target.value))}
                                className="bg-input text-foreground border-input focus:ring-primary"
                            />
                        </div>
                        <Button
                            onClick={handleScrape}
                            className="w-full md:w-auto min-w-[140px]"
                            disabled={loading || !query}
                            loading={loading}
                        >
                            {!loading && <Play className="mr-2 h-4 w-4" />}
                            Start Scraping
                        </Button>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-border bg-card shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                    <div>
                        <CardTitle className="text-primary">Results</CardTitle>
                        <CardDescription className="pt-1">
                            {error ? (
                                <span className="text-destructive font-medium">{error}</span>
                            ) : (
                                results.length > 0 ? <span className="text-primary font-medium">Found {results.length} items</span> : "No results yet"
                            )}
                        </CardDescription>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={results.length === 0}
                        onClick={() => downloadCSV(results, config.columns, `${config.id}-results`)}
                    >
                        <Download className="mr-2 h-4 w-4" />
                        Download CSV
                    </Button>
                </CardHeader>
                <CardContent>
                    <ScraperTable columns={config.columns} data={results} loading={loading} />
                </CardContent>
            </Card>
        </div>
    )
}

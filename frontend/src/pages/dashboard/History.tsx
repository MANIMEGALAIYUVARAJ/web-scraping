import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"

export default function History() {
    const [historyData, setHistoryData] = React.useState<any[]>([])
    const [loading, setLoading] = React.useState(true)

    React.useEffect(() => {
        fetchHistory()
    }, [])

    const fetchHistory = async () => {
        try {
            const res = await fetch("/api/history")
            const data = await res.json()
            setHistoryData(data)
        } catch (err) {
            console.error("Failed to fetch history", err)
        } finally {
            setLoading(false)
        }
    }

    const clearHistory = async () => {
        if (!confirm("Are you sure you want to clear history?")) return
        try {
            await fetch("/api/history", { method: "DELETE" })
            setHistoryData([])
        } catch (err) {
            console.error("Failed to clear history", err)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold tracking-tight text-primary">History</h1>
                    <button
                        onClick={clearHistory}
                        className="text-sm text-destructive hover:text-destructive/80 px-3 py-1 rounded bg-destructive/10 border border-destructive/20 transition-colors"
                    >
                        Clear History
                    </button>
                </div>
                <p className="text-muted-foreground">View and manage your past scraping sessions.</p>
            </div>

            <Card className="border-border bg-card shadow-sm">
                <CardHeader>
                    <CardTitle className="text-primary">Recent Activity</CardTitle>
                    <CardDescription>Your last 30 days of scraping history.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="rounded-md border border-border">
                        <table className="w-full text-sm text-left">
                            <thead className="text-muted-foreground font-medium border-b border-border bg-muted/30">
                                <tr>
                                    <th className="p-4">Scraper</th>
                                    <th className="p-4">Query</th>
                                    <th className="p-4">Date</th>
                                    <th className="p-4">Items</th>
                                    <th className="p-4">Status</th>
                                    <th className="p-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                {historyData.map((row) => (
                                    <tr key={row.id} className="hover:bg-muted/30 transition-colors">
                                        <td className="p-4 font-medium text-foreground capitalize">{row.scraper.replace("-", " ")}</td>
                                        <td className="p-4 text-muted-foreground">{row.query || "-"}</td>
                                        <td className="p-4 text-muted-foreground">{row.date}</td>
                                        <td className="p-4 text-foreground">{row.items} items</td>
                                        <td className="p-4">
                                            <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary ring-1 ring-inset ring-primary/20">
                                                {row.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right">
                                            {row.csv_path && (
                                                <a
                                                    href={row.csv_path}
                                                    download
                                                    className="text-primary hover:text-primary/80 font-medium text-xs hover:underline"
                                                >
                                                    Download
                                                </a>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                                {historyData.length === 0 && !loading && (
                                    <tr>
                                        <td colSpan={6} className="p-8 text-center text-muted-foreground">
                                            No history found. Start scraping to see results here.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

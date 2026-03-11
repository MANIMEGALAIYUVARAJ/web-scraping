// Imports removed
import { cn } from "@/lib/utils"

// Defining Table Base components here for simplicity of task unit
// Defining Table Base components here for simplicity of task unit
const TableRoot = ({ className, ...props }: React.HTMLAttributes<HTMLTableElement>) => (
    <div className="w-full overflow-auto rounded-lg border border-border bg-card shadow-sm">
        <table className={cn("w-full caption-bottom text-sm text-left", className)} {...props} />
    </div>
)

const TableHeaderRoot = ({ className, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) => (
    <thead className={cn("[&_tr]:border-b [&_tr]:border-border bg-primary/5", className)} {...props} />
)

const TableBodyRoot = ({ className, ...props }: React.HTMLAttributes<HTMLTableSectionElement>) => (
    <tbody className={cn("[&_tr:last-child]:border-0", className)} {...props} />
)

const TableRowRoot = ({ className, ...props }: React.HTMLAttributes<HTMLTableRowElement>) => (
    <tr
        className={cn(
            "border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted",
            className
        )}
        {...props}
    />
)

const TableHeadRoot = ({ className, ...props }: React.ThHTMLAttributes<HTMLTableCellElement>) => (
    <th
        className={cn(
            "h-12 px-4 text-left align-middle font-bold text-primary [&:has([role=checkbox])]:pr-0",
            className
        )}
        {...props}
    />
)

const TableCellRoot = ({ className, ...props }: React.TdHTMLAttributes<HTMLTableCellElement>) => (
    <td
        className={cn(
            "p-4 align-middle [&:has([role=checkbox])]:pr-0 text-foreground",
            className
        )}
        {...props}
    />
)

interface ScraperTableProps {
    columns: { key: string; label: string }[]
    data: any[]
    loading?: boolean
}

export function ScraperTable({ columns, data, loading }: ScraperTableProps) {
    if (loading) {
        return (
            <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-12 w-full animate-pulse rounded-md bg-muted" />
                ))}
            </div>
        )
    }

    if (!data || data.length === 0) {
        return (
            <div className="flex h-64 w-full flex-col items-center justify-center rounded-lg border border-dashed border-border bg-card text-muted-foreground">
                <p className="text-lg font-medium">No results yet</p>
                <p className="text-sm">Scraped data will appear here</p>
            </div>
        )
    }

    return (
        <TableRoot>
            <TableHeaderRoot>
                <TableRowRoot>
                    {columns.map((col) => (
                        <TableHeadRoot key={col.key}>{col.label}</TableHeadRoot>
                    ))}
                </TableRowRoot>
            </TableHeaderRoot>
            <TableBodyRoot>
                {data.map((row, i) => (
                    <TableRowRoot key={i}>
                        {columns.map((col) => (
                            <TableCellRoot key={col.key}>
                                {(col.key.toLowerCase().includes("url") || (typeof row[col.key] === 'string' && row[col.key]?.trim().match(/^https?:\/\//i))) && row[col.key] ? (
                                    <a
                                        href={row[col.key].trim()}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:underline break-all block"
                                        onClick={(e) => e.stopPropagation()}
                                    >
                                        {row[col.key]}
                                    </a>
                                ) : (
                                    row[col.key] || "-"
                                )}
                            </TableCellRoot>
                        ))}
                    </TableRowRoot>
                ))}
            </TableBodyRoot>
        </TableRoot>
    )
}

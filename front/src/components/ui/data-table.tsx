import type { LucideIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { EmptyState } from "./empty-state"
import { Spinner } from "./spinner"

export interface Column<T> {
  key: string
  header: string
  // Rendering personalizado
  render?: (row: T) => React.ReactNode
  // Ocultar columna en viewports < sm (responsive)
  hiddenOnMobile?: boolean
  className?: string
  headerClassName?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  emptyTitle?: string
  emptyDescription?: string
  emptyIcon?: LucideIcon
  keyExtractor: (row: T) => string
  onRowClick?: (row: T) => void
  className?: string
}

export function DataTable<T>({
  columns,
  data,
  loading,
  emptyTitle = "Sin datos",
  emptyDescription = "No hay registros para mostrar.",
  emptyIcon,
  keyExtractor,
  onRowClick,
  className,
}: DataTableProps<T>) {
  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!data.length) {
    return (
      <EmptyState
        icon={emptyIcon}
        title={emptyTitle}
        description={emptyDescription}
      />
    )
  }

  return (
    <div
      className={cn(
        "overflow-x-auto rounded-xl border border-slate-200 bg-white",
        className,
      )}
    >
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                className={cn(
                  "px-4 py-3 text-left font-semibold text-slate-600",
                  col.headerClassName,
                  col.hiddenOnMobile && "hidden sm:table-cell",
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {data.map((row) => (
            <tr
              key={keyExtractor(row)}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              className={cn(
                "transition-colors hover:bg-slate-50",
                onRowClick && "cursor-pointer",
              )}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={cn(
                    "px-4 py-3 text-slate-700",
                    col.hiddenOnMobile && "hidden sm:table-cell",
                    col.className,
                  )}
                >
                  {col.render ? col.render(row) : String((row as Record<string, unknown>)[col.key] ?? "-")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

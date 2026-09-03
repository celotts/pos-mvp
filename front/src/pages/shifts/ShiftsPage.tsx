import { useQuery } from "@tanstack/react-query"
import { Clock } from "lucide-react"

import { PageHeader, DataTable, Alert, Badge, type Column } from "@/components/ui"
import { listShifts } from "@/services/pos.service"
import { formatDate } from "@/lib/utils"
import type { Shift } from "@/types"

export function ShiftsPage() {
  const shiftsQ = useQuery({ queryKey: ["shifts"], queryFn: listShifts })

  const columns: Column<Shift>[] = [
    {
      key: "start_time",
      header: "Inicio",
      render: (s) => <span className="font-medium text-slate-800">{formatDate(s.start_time)}</span>,
    },
    {
      key: "end_time",
      header: "Cierre",
      hiddenOnMobile: true,
      render: (s) => <span>{s.end_time ? formatDate(s.end_time) : "—"}</span>,
    },
    {
      key: "starting_cash",
      header: "Fondo inicial",
      hiddenOnMobile: true,
      render: (s) => <span>${Number(s.starting_cash).toFixed(2)}</span>,
    },
    {
      key: "ending_cash",
      header: "Cierre de caja",
      render: (s) => <span>${Number(s.ending_cash ?? 0).toFixed(2)}</span>,
    },
    {
      key: "status",
      header: "Estado",
      render: (s) =>
        s.status === "open" ? (
          <Badge variant="success">Abierto</Badge>
        ) : (
          <Badge variant="outline">Cerrado</Badge>
        ),
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Turnos / Cierres de caja"
        description="Historial de apertura y cierre de turnos de caja"
      />

      {shiftsQ.isError && <Alert variant="error">{shiftsQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={shiftsQ.data ?? []}
        loading={shiftsQ.isLoading}
        keyExtractor={(s) => s.id}
        emptyTitle="Sin turnos"
        emptyDescription="Aún no hay turnos registrados desde el punto de venta."
        emptyIcon={Clock}
      />
    </div>
  )
}
import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Pencil, Trash2, HandCoins } from "lucide-react"

import {
  Button,
  Input,
  Modal,
  PageHeader,
  DataTable,
  Alert,
  Badge,
  Select,
  type Column,
} from "@/components/ui"
import {
  listAccountsReceivable,
  updateAccountReceivable,
  deleteAccountReceivable,
} from "@/services/accounting.service"
import { getErrorMessage } from "@/lib/api"
import { formatDate } from "@/lib/utils"
import type { AccountsReceivable } from "@/types"

const receivableSchema = z.object({
  outstanding_amount: z.string().min(0),
  due_date: z.string().optional(),
  status: z.enum(["OPEN", "CLOSED"]),
})

type ReceivableForm = z.infer<typeof receivableSchema>

export function AccountsReceivablePage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<AccountsReceivable | null>(null)

  const arQ = useQuery({
    queryKey: ["accounts-receivable"],
    queryFn: listAccountsReceivable,
  })

  const form = useForm<ReceivableForm>({
    resolver: zodResolver(receivableSchema),
    defaultValues: { outstanding_amount: "", due_date: "", status: "OPEN" },
  })

  const openEdit = (a: AccountsReceivable) => {
    setEditing(a)
    form.reset({
      outstanding_amount: String(a.outstanding_amount ?? ""),
      due_date: a.due_date ?? "",
      status: a.status,
    })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: ReceivableForm) =>
      updateAccountReceivable(editing!.id, {
        outstanding_amount: Number(values.outstanding_amount),
        due_date: values.due_date || null,
        status: values.status,
      }),
    onSuccess: () => {
      toast.success("Cuenta por cobrar actualizada")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["accounts-receivable"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteAccountReceivable,
    onSuccess: () => {
      toast.success("Cuenta por cobrar eliminada")
      queryClient.invalidateQueries({ queryKey: ["accounts-receivable"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<AccountsReceivable>[] = [
    {
      key: "customer_id",
      header: "Cliente",
      render: (a) => (
        <span className="font-medium text-slate-800">{a.customer_id.slice(0, 8)}…</span>
      ),
    },
    {
      key: "original_amount",
      header: "Original",
      hiddenOnMobile: true,
      render: (a) => <span>${Number(a.original_amount).toFixed(2)}</span>,
    },
    {
      key: "outstanding_amount",
      header: "Pendiente",
      render: (a) => (
        <span className="font-semibold text-slate-800">${Number(a.outstanding_amount).toFixed(2)}</span>
      ),
    },
    {
      key: "due_date",
      header: "Vence",
      hiddenOnMobile: true,
      render: (a) => <span>{formatDate(a.due_date, { dateStyle: "medium" })}</span>,
    },
    {
      key: "status",
      header: "Estado",
      render: (a) =>
        a.status === "OPEN" ? (
          <Badge variant="warning">Abierta</Badge>
        ) : (
          <Badge variant="success">Cerrada</Badge>
        ),
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (a) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(a)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-red-600 hover:bg-red-50"
            onClick={() => {
              if (confirm("¿Eliminar esta cuenta por cobrar?")) remove.mutate(a.id)
            }}
            title="Eliminar"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cuentas por cobrar"
        description="Deudas de clientes contigo por ventas al crédito"
      />

      {arQ.isError && <Alert variant="error">{arQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={arQ.data ?? []}
        loading={arQ.isLoading}
        keyExtractor={(a) => a.id}
        emptyTitle="Sin cuentas por cobrar"
        emptyDescription="Las cuentas por cobrar se generan automáticamente con cada venta al crédito."
        emptyIcon={HandCoins}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Editar cuenta por cobrar"
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              Guardar cambios
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Monto pendiente"
            type="number"
            step="0.01"
            min={0}
            error={form.formState.errors.outstanding_amount?.message}
            {...form.register("outstanding_amount")}
          />
          <Input
            label="Fecha de vencimiento"
            type="date"
            error={form.formState.errors.due_date?.message}
            {...form.register("due_date")}
          />
          <Select
            label="Estado"
            options={[
              { value: "OPEN", label: "Abierta" },
              { value: "CLOSED", label: "Cerrada" },
            ]}
            {...form.register("status")}
          />
          {save.isError && <Alert variant="error">{getErrorMessage(save.error)}</Alert>}
        </form>
      </Modal>
    </div>
  )
}
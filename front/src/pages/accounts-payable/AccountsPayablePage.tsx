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
  listAccountsPayable,
  updateAccountPayable,
  deleteAccountPayable,
} from "@/services/accounting.service"
import { getErrorMessage } from "@/lib/api"
import { formatDate } from "@/lib/utils"
import type { AccountsPayable } from "@/types"

const payableSchema = z.object({
  outstanding_amount: z.string().min(0),
  due_date: z.string().optional(),
  status: z.enum(["OPEN", "CLOSED"]),
})

type PayableForm = z.infer<typeof payableSchema>

export function AccountsPayablePage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<AccountsPayable | null>(null)

  const apQ = useQuery({
    queryKey: ["accounts-payable"],
    queryFn: listAccountsPayable,
  })

  const form = useForm<PayableForm>({
    resolver: zodResolver(payableSchema),
    defaultValues: { outstanding_amount: "", due_date: "", status: "OPEN" },
  })

  const openEdit = (a: AccountsPayable) => {
    setEditing(a)
    form.reset({
      outstanding_amount: String(a.outstanding_amount ?? ""),
      due_date: a.due_date ?? "",
      status: a.status,
    })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: PayableForm) =>
      updateAccountPayable(editing!.id, {
        outstanding_amount: Number(values.outstanding_amount),
        due_date: values.due_date || null,
        status: values.status,
      }),
    onSuccess: () => {
      toast.success("Cuenta por pagar actualizada")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["accounts-payable"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteAccountPayable,
    onSuccess: () => {
      toast.success("Cuenta por pagar eliminada")
      queryClient.invalidateQueries({ queryKey: ["accounts-payable"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<AccountsPayable>[] = [
    {
      key: "supplier_id",
      header: "Proveedor",
      render: (a) => (
        <span className="font-medium text-slate-800">{a.supplier_id.slice(0, 8)}…</span>
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
              if (confirm("¿Eliminar esta cuenta por pagar?")) remove.mutate(a.id)
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
        title="Cuentas por pagar"
        description="Deudas con proveedores por conceptos de compra"
      />

      {apQ.isError && <Alert variant="error">{apQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={apQ.data ?? []}
        loading={apQ.isLoading}
        keyExtractor={(a) => a.id}
        emptyTitle="Sin cuentas por pagar"
        emptyDescription="Las deudas a proveedores se generan automáticamente con cada compra al crédito."
        emptyIcon={HandCoins}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Editar cuenta por pagar"
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
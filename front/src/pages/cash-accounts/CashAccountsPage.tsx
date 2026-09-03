import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Trash2, Pencil, Wallet } from "lucide-react"

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
  listCashAccounts,
  createCashAccount,
  updateCashAccount,
  deleteCashAccount,
} from "@/services/accounting.service"
import { getErrorMessage } from "@/lib/api"
import type { CashAccount } from "@/types"

const accountSchema = z.object({
  name: z.string().min(1, "El nombre es obligatorio"),
  account_type: z.enum(["CASH", "BANK"]),
})

type AccountForm = z.infer<typeof accountSchema>

export function CashAccountsPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<CashAccount | null>(null)

  const accountsQ = useQuery({
    queryKey: ["cash-accounts"],
    queryFn: listCashAccounts,
  })

  const form = useForm<AccountForm>({
    resolver: zodResolver(accountSchema),
    defaultValues: { name: "", account_type: "CASH" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ name: "", account_type: "CASH" })
    setOpen(true)
  }

  const openEdit = (a: CashAccount) => {
    setEditing(a)
    form.reset({ name: a.name, account_type: a.account_type })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: AccountForm) =>
      editing ? updateCashAccount(editing.id, values) : createCashAccount(values),
    onSuccess: () => {
      toast.success(editing ? "Cuenta actualizada" : "Cuenta creada")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["cash-accounts"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteCashAccount,
    onSuccess: () => {
      toast.success("Cuenta eliminada")
      queryClient.invalidateQueries({ queryKey: ["cash-accounts"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<CashAccount>[] = [
    {
      key: "name",
      header: "Cuenta",
      render: (a) => <span className="font-medium text-slate-800">{a.name}</span>,
    },
    {
      key: "account_type",
      header: "Tipo",
      render: (a) =>
        a.account_type === "CASH" ? (
          <Badge variant="info">Efectivo</Badge>
        ) : (
          <Badge variant="default">Banco</Badge>
        ),
    },
    {
      key: "currency",
      header: "Moneda",
      hiddenOnMobile: true,
      render: (a) => <span>{a.currency}</span>,
    },
    {
      key: "current_balance",
      header: "Saldo",
      render: (a) => (
        <span className="font-semibold text-slate-800">
          {Number(a.current_balance).toLocaleString("en-US", {
            style: "currency",
            currency: a.currency || "MXN",
          })}
        </span>
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
              if (confirm(`¿Eliminar la cuenta "${a.name}"?`)) remove.mutate(a.id)
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
        title="Cuentas de efectivo / banco"
        description="Administra las cuentas donde se registra el dinero"
      >
        <Button onClick={openCreate}>
          <Plus className="h-4 w-4" /> Nueva cuenta
        </Button>
      </PageHeader>

      {accountsQ.isError && <Alert variant="error">{accountsQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={accountsQ.data ?? []}
        loading={accountsQ.isLoading}
        keyExtractor={(a) => a.id}
        emptyTitle="Sin cuentas"
        emptyDescription="Registra una cuenta de efectivo o bancaria."
        emptyIcon={Wallet}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar cuenta" : "Nueva cuenta"}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear cuenta"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre"
            placeholder="Ej. Caja principal"
            error={form.formState.errors.name?.message}
            {...form.register("name")}
          />
          <Select
            label="Tipo"
            options={[
              { value: "CASH", label: "Efectivo" },
              { value: "BANK", label: "Banco" },
            ]}
            error={form.formState.errors.account_type?.message}
            {...form.register("account_type")}
          />
          {save.isError && <Alert variant="error">{getErrorMessage(save.error)}</Alert>}
        </form>
      </Modal>
    </div>
  )
}
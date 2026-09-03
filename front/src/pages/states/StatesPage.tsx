import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Trash2, Pencil, MapPin } from "lucide-react"

import {
  Button,
  Input,
  Modal,
  PageHeader,
  DataTable,
  Alert,
  Select,
  type Column,
} from "@/components/ui"
import {
  listCountries,
  listStates,
  createState,
  updateState,
  deleteState,
} from "@/services/locations.service"
import { getErrorMessage } from "@/lib/api"
import type { StateProvince } from "@/types"

const stateSchema = z.object({
  name: z.string().min(1, "El nombre es obligatorio"),
  country_id: z.string().min(1, "Selecciona un país"),
})

type StateForm = z.infer<typeof stateSchema>

export function StatesPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<StateProvince | null>(null)

  const statesQ = useQuery({ queryKey: ["states"], queryFn: listStates })
  const countriesQ = useQuery({ queryKey: ["countries"], queryFn: listCountries })

  const countries = countriesQ.data ?? []
  const countryById = new Map(countries.map((c) => [c.id, c.name]))

  const form = useForm<StateForm>({
    resolver: zodResolver(stateSchema),
    defaultValues: { name: "", country_id: "" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ name: "", country_id: "" })
    setOpen(true)
  }

  const openEdit = (s: StateProvince) => {
    setEditing(s)
    form.reset({ name: s.name, country_id: s.country_id })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: StateForm) =>
      editing ? updateState(editing.id, values) : createState(values),
    onSuccess: () => {
      toast.success(editing ? "Estado actualizado" : "Estado creado")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["states"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteState,
    onSuccess: () => {
      toast.success("Estado eliminado")
      queryClient.invalidateQueries({ queryKey: ["states"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<StateProvince>[] = [
    {
      key: "name",
      header: "Estado / Provincia",
      render: (s) => <span className="font-medium text-slate-800">{s.name}</span>,
    },
    {
      key: "country_id",
      header: "País",
      render: (s) => <span>{countryById.get(s.country_id) ?? "—"}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (s) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(s)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-red-600 hover:bg-red-50"
            onClick={() => {
              if (confirm(`¿Eliminar el estado "${s.name}"?`)) remove.mutate(s.id)
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
        title="Estados y provincias"
        description="Catálogo de divisiones territoriales por país"
      >
        <Button onClick={openCreate}>
          <Plus className="h-4 w-4" /> Nuevo estado
        </Button>
      </PageHeader>

      {statesQ.isError && <Alert variant="error">{statesQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={statesQ.data ?? []}
        loading={statesQ.isLoading}
        keyExtractor={(s) => s.id}
        emptyTitle="Sin estados"
        emptyDescription="Agrega estados o provincias para categorizar municipios."
        emptyIcon={MapPin}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar estado" : "Nuevo estado"}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear estado"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre"
            placeholder="Ej. Jalisco"
            error={form.formState.errors.name?.message}
            {...form.register("name")}
          />
          <Select
            label="País"
            placeholder="Selecciona"
            options={countries.map((c) => ({ value: c.id, label: c.name }))}
            error={form.formState.errors.country_id?.message}
            {...form.register("country_id")}
          />
          {save.isError && <Alert variant="error">{getErrorMessage(save.error)}</Alert>}
        </form>
      </Modal>
    </div>
  )
}
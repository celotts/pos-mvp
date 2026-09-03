import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Trash2, Pencil, Globe } from "lucide-react"

import {
  Button,
  Input,
  Modal,
  PageHeader,
  DataTable,
  Alert,
  type Column,
} from "@/components/ui"
import {
  listCountries,
  createCountry,
  updateCountry,
  deleteCountry,
} from "@/services/locations.service"
import { getErrorMessage } from "@/lib/api"
import type { Country } from "@/types"

const countrySchema = z.object({
  name: z.string().min(1, "El nombre es obligatorio"),
  iso_code: z
    .string()
    .min(2, "Código ISO de 2 letras")
    .max(3, "Máximo 3 letras")
    .regex(/^[A-Za-z]{2,3}$/, "Solo letras (ISO-3166)"),
})

type CountryForm = z.infer<typeof countrySchema>

export function CountriesPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Country | null>(null)

  const countriesQ = useQuery({ queryKey: ["countries"], queryFn: listCountries })

  const form = useForm<CountryForm>({
    resolver: zodResolver(countrySchema),
    defaultValues: { name: "", iso_code: "" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ name: "", iso_code: "" })
    setOpen(true)
  }

  const openEdit = (c: Country) => {
    setEditing(c)
    form.reset({ name: c.name, iso_code: c.iso_code })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: CountryForm) =>
      editing ? updateCountry(editing.id, values) : createCountry(values),
    onSuccess: () => {
      toast.success(editing ? "País actualizado" : "País creado")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["countries"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteCountry,
    onSuccess: () => {
      toast.success("País eliminado")
      queryClient.invalidateQueries({ queryKey: ["countries"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<Country>[] = [
    {
      key: "name",
      header: "País",
      render: (c) => <span className="font-medium text-slate-800">{c.name}</span>,
    },
    {
      key: "iso_code",
      header: "Código ISO",
      render: (c) => <span className="uppercase">{c.iso_code}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (c) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(c)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-red-600 hover:bg-red-50"
            onClick={() => {
              if (confirm(`¿Eliminar el país "${c.name}"?`)) remove.mutate(c.id)
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
        title="Países"
        description="Catálogo de países del sistema"
      >
        <Button onClick={openCreate}>
          <Plus className="h-4 w-4" /> Nuevo país
        </Button>
      </PageHeader>

      {countriesQ.isError && <Alert variant="error">{countriesQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={countriesQ.data ?? []}
        loading={countriesQ.isLoading}
        keyExtractor={(c) => c.id}
        emptyTitle="Sin países"
        emptyDescription="Agrega países para poder categorizar estados y municipios."
        emptyIcon={Globe}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar país" : "Nuevo país"}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear país"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre"
            placeholder="Ej. México"
            error={form.formState.errors.name?.message}
            {...form.register("name")}
          />
          <Input
            label="Código ISO"
            placeholder="Ej. MX"
            maxLength={3}
            error={form.formState.errors.iso_code?.message}
            {...form.register("iso_code")}
          />
          {save.isError && <Alert variant="error">{getErrorMessage(save.error)}</Alert>}
        </form>
      </Modal>
    </div>
  )
}
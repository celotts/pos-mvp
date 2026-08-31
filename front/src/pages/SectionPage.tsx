import { Construction, Plus } from 'lucide-react'

import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { PageHeader } from '../components/ui/brand'
import { getMenuIcon } from '../menu/menu'
import type { MenuItem } from '../types'

/**
 * Página genérica para los formularios del menú.
 * Representa el formulario final que se construirá por módulo.
 */
export function SectionPage({ item }: { item: MenuItem }) {
  const Icon = item.icon ? getMenuIcon(item.icon) : null

  return (
    <div className="space-y-6">
      <PageHeader
        title={item.label}
        subtitle={`Formulario del módulo "${item.label}".`}
        actions={
          <Button type="button" disabled aria-label="Reservado para crear registro">
            <Plus className="h-4 w-4" />
            Nuevo
          </Button>
        }
      />

      <Card>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
            {Icon ? <Icon className="h-7 w-7 text-slate-500" /> : <Construction className="h-7 w-7 text-slate-500" />}
          </div>
          <h3 className="text-lg font-semibold text-slate-900">
            Módulo en preparación
          </h3>
          <p className="mt-1.5 max-w-sm text-sm text-slate-500">
            Aquí se construirá el formulario de {item.label.toLowerCase()} con listado,
            alta, edición y baja de registros. Tu rol ya tiene acceso a esta sección.
          </p>
        </div>
      </Card>
    </div>
  )
}
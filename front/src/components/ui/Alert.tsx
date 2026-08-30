import type { ReactNode } from 'react'

type Kind = 'info' | 'error' | 'warning' | 'success'

const STYLES: Record<Kind, string> = {
  info: 'border-brand-200 bg-brand-50 text-brand-800',
  error: 'border-rose-200 bg-rose-50 text-rose-800',
  warning: 'border-amber-200 bg-amber-50 text-amber-800',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-800',
}

interface AlertProps {
  kind?: Kind
  title?: string
  children: ReactNode
}

/** Notificación contextual (éxito, error, advertencia o información). */
export function Alert({ kind = 'info', title, children }: AlertProps) {
  return (
    <div
      className={`flex flex-col gap-1 rounded-lg border px-4 py-3 text-sm ${STYLES[kind]}`}
    >
      {title ? <p className="font-semibold">{title}</p> : null}
      <div>{children}</div>
    </div>
  )
}
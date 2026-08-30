import type { InputHTMLAttributes, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface FieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  hint?: ReactNode
}

/** Campo de formulario con label, error e hint opcional. */
export function Field({ label, error, hint, className = '', ...props }: FieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-slate-700" htmlFor={props.id}>
        {label}
      </label>
      <input
        className={`w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:ring-2 focus:ring-brand-500 ${
          error ? 'border-rose-400 focus:border-rose-400' : 'border-slate-300'
        } ${className}`}
        {...props}
      />
      {hint ? (
        <div className="flex items-center gap-1.5 text-xs text-slate-500">{hint}</div>
      ) : null}
      {error ? (
        <div className="flex items-center gap-1.5 text-xs text-rose-600">
          <AlertTriangle className="h-3.5 w-3.5" />
          {error}
        </div>
      ) : null}
    </div>
  )
}
import type { ReactNode } from 'react'

interface CardProps {
  header?: ReactNode
  children: ReactNode
  className?: string
}

/** Contenedor de tarjeta blanca con encabezado opcional. */
export function Card({ header, children, className = '' }: CardProps) {
  return (
    <div
      className={`overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}
    >
      {header ? (
        <div className="border-b border-slate-200 px-5 py-4">{header}</div>
      ) : null}
      <div className="px-5 py-5">{children}</div>
    </div>
  )
}
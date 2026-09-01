import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/** Une clases de Tailwind de forma segura y sin conflictos. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

/** Formatea un número a moneda (USD por defecto). */
export function formatCurrency(
  value: number | string | null | undefined,
  currency = "USD",
): string {
  const n = Number(value)
  if (Number.isNaN(n)) return "-"
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(n)
}

/** Formatea una fecha ISO a formato local legible. */
export function formatDate(
  iso?: string | null,
  opts: Intl.DateTimeFormatOptions = {
    dateStyle: "medium",
    timeStyle: "short",
  },
): string {
  if (!iso) return "-"
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return "-"
  return new Intl.DateTimeFormat("es-ES", opts).format(d)
}

/** Trunca texto largo con elipses. */
export function truncate(value: string, length = 40): string {
  if (value.length <= length) return value
  return `${value.slice(0, length)}…`
}

/** Convierte el primer carácter a mayúscula. */
export function capitalize(value?: string | null): string {
  if (!value) return ""
  return value.charAt(0).toUpperCase() + value.slice(1).toLowerCase()
}

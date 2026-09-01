import * as React from "react"
import { AlertCircle, CheckCircle2, Info, XCircle } from "lucide-react"

import { cn } from "@/lib/utils"

type AlertVariant = "info" | "success" | "warning" | "error"

interface AlertProps {
  variant?: AlertVariant
  title?: string
  children?: React.ReactNode
  className?: string
}

const config: Record<
  AlertVariant,
  { icon: React.ComponentType<{ className?: string }>; classes: string }
> = {
  info: { icon: Info, classes: "border-brand-200 bg-brand-50 text-brand-800" },
  success: {
    icon: CheckCircle2,
    classes: "border-emerald-200 bg-emerald-50 text-emerald-800",
  },
  warning: {
    icon: AlertCircle,
    classes: "border-amber-200 bg-amber-50 text-amber-800",
  },
  error: { icon: XCircle, classes: "border-red-200 bg-red-50 text-red-800" },
}

export function Alert({
  variant = "info",
  title,
  children,
  className,
}: AlertProps) {
  const { icon: Icon, classes } = config[variant]
  return (
    <div
      role="alert"
      className={cn("flex gap-3 rounded-lg border p-3 text-sm", classes, className)}
    >
      <Icon className="mt-0.5 h-5 w-5 shrink-0" />
      <div>
        {title && <p className="font-semibold">{title}</p>}
        {children && <div className="mt-0.5">{children}</div>}
      </div>
    </div>
  )
}

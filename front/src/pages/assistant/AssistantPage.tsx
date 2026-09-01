import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import {
  Send,
  Bot,
  Loader2,
  TrendingUp,
  PackageSearch,
  ShieldAlert,
  Coins,
  Sparkles,
} from "lucide-react"

import { PageHeader, Card, CardContent, Alert, Button } from "@/components/ui"
import { assistantChat } from "@/services/assistant.service"
import { listStores } from "@/services/stores.service"
import { getErrorMessage } from "@/lib/api"
import type { InsightRecommendation } from "@/types"

type SuggestionCategory = {
  title: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  items: { label: string; prompt: string }[]
}

const CATEGORIES: SuggestionCategory[] = [
  {
    title: "Maximizar ventas",
    icon: TrendingUp,
    color: "border-brand-200 bg-brand-50 text-brand-700",
    items: [
      { label: "Productos más vendidos", prompt: "¿Cuáles son los productos más vendidos?" },
      { label: "Resumen de ventas del mes", prompt: "Resume las ventas de los últimos 30 días" },
    ],
  },
  {
    title: "Rentabilidad",
    icon: Coins,
    color: "border-emerald-200 bg-emerald-50 text-emerald-700",
    items: [
      { label: "Mejores y peores márgenes", prompt: "¿Qué productos tienen el mejor y el peor margen de ganancia?" },
    ],
  },
  {
    title: "Inventario y stock",
    icon: PackageSearch,
    color: "border-amber-200 bg-amber-50 text-amber-700",
    items: [
      { label: "Stock bajo / agotado", prompt: "¿Qué productos tienen stock más bajo?" },
      { label: "Salud del inventario", prompt: "Evalúa la salud de mi inventario" },
    ],
  },
  {
    title: "Prevenir pérdidas",
    icon: ShieldAlert,
    color: "border-red-200 bg-red-50 text-red-700",
    items: [
      { label: "Riesgo de desabasto", prompt: "¿Qué productos están en riesgo de quedarse sin stock?" },
    ],
  },
]

const CATEGORY_TONE: Record<string, string> = {
  SALES: "border-brand-200 bg-brand-50 text-brand-800",
  INVENTORY: "border-amber-200 bg-amber-50 text-amber-800",
  MARGIN: "border-emerald-200 bg-emerald-50 text-emerald-800",
  RISK: "border-red-200 bg-red-50 text-red-800",
}

export function AssistantPage() {
  const [message, setMessage] = useState("")
  const [storeId, setStoreId] = useState("")
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState<string | null>(null)
  const [insights, setInsights] = useState<InsightRecommendation[]>([])
  const [error, setError] = useState<string | null>(null)

  const storesQ = useQuery({ queryKey: ["stores"], queryFn: listStores })
  const stores = storesQ.data ?? []

  const send = async (text?: string) => {
    const q = (text ?? message).trim()
    if (!q || loading) return
    setLoading(true)
    setError(null)
    setAnswer(null)
    setInsights([])
    try {
      const res = await assistantChat(q, storeId || null)
      setAnswer(res.answer)
      setInsights(res.insights)
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo consultar al asistente"))
    } finally {
      setLoading(false)
      if (!text) setMessage("")
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Asistente Ejecutivo IA"
        description="Toma de decisiones con datos reales: ventas, rentabilidad, inventario y riesgos."
      >
        <div className="flex min-w-[200px] flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Tienda (contexto)</label>
          <select
            value={storeId}
            onChange={(e) => setStoreId(e.target.value)}
            className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">Todas las tiendas</option>
            {stores.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </PageHeader>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {CATEGORIES.map((cat) => (
          <Card key={cat.title} className={cat.color}>
            <CardContent className="p-4">
              <div className="mb-2 flex items-center gap-2">
                <cat.icon className="h-4 w-4" />
                <p className="text-sm font-semibold">{cat.title}</p>
              </div>
              <div className="space-y-1">
                {cat.items.map((it) => (
                  <button
                    key={it.prompt}
                    onClick={() => {
                      setMessage(it.prompt)
                      send(it.prompt)
                    }}
                    disabled={loading}
                    className="block w-full rounded bg-white/70 px-2 py-1 text-left text-xs leading-snug hover:bg-white disabled:opacity-50"
                  >
                    {it.label}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="space-y-4 p-5">
          <div className="flex gap-2">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  send()
                }
              }}
              disabled={loading}
              placeholder="Escribe una pregunta de negocio…"
              className="h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 disabled:opacity-60"
            />
            <Button onClick={() => send()} disabled={loading || !message.trim()}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Enviar
            </Button>
          </div>

          {error && <Alert variant="error">{error}</Alert>}

          {loading && (
            <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
              <Loader2 className="h-5 w-5 animate-spin text-brand-600" />
              <p className="text-sm text-slate-600">
                El asistente está consultando tus datos…
              </p>
            </div>
          )}

          {!loading && answer && !error && (
            <div className="space-y-3">
              <div className="flex gap-3 rounded-lg border border-slate-200 bg-white p-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-white">
                  <Bot className="h-5 w-5" />
                </div>
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
                  {answer}
                </div>
              </div>

              {insights.length > 0 && (
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <p className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
                    <Sparkles className="h-4 w-4 text-brand-600" /> Recomendaciones accionables
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {insights.map((ins, i) => (
                      <span
                        key={i}
                        className={`rounded-lg border px-3 py-1.5 text-xs font-medium ${
                          CATEGORY_TONE[ins.category] ?? "border-slate-200 bg-white text-slate-700"
                        }`}
                      >
                        {ins.category}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {!loading && !answer && !error && (
            <Alert variant="info">
              El asistente ejecutivo analiza tus datos reales para ayudarte a{" "}
              <b>maximizar ganancias, optimizar inventario y prevenir pérdidas</b>.{" "}
              Usa las tarjetas de arriba para consultas con valor o escribe tu propia
              pregunta de negocio.
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

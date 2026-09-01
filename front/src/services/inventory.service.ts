import { api } from "@/lib/api"

export interface StockoutRiskItem {
  product_id: string
  product_name: string
  stock_quantity: number
  avg_daily_demand: number
  forecast_next_days: number
  days_of_stock_left: number | null
  risk: "OUT_OF_STOCK" | "CRITICAL" | "WARNING" | "OK" | "NO_SALES"
  recommended_quantity?: number
}

export interface StockoutRiskResponse {
  horizon_days: number
  lead_time_days: number
  items: StockoutRiskItem[]
}

export async function getStockoutRisk(): Promise<StockoutRiskResponse> {
  // Este endpoint NO usa la envoltura ApiResponse: devuelve el objeto directo.
  const res = await api.get<StockoutRiskResponse>("/analytics/stockout-risk")
  return res.data
}

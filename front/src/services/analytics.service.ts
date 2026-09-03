import { api } from "@/lib/api"
import type {
  CrossSellResponse,
  ProductBundle,
  StockoutRiskResponse,
} from "@/types"

/**
 * El controlador de analítica devuelve los datos JSON crudos (sin la envoltura
 * estándar ApiResponse), por lo que se lee `res.data` directamente.
 */

export async function listBundles(params?: {
  days?: number
  limit?: number
  min_support?: number
}): Promise<ProductBundle[]> {
  const res = await api.get<ProductBundle[]>("/analytics/bundles", { params })
  return res.data
}

export async function getStockoutRisk(params?: {
  horizon?: number
  lead_time_days?: number
  lookback_days?: number
}): Promise<StockoutRiskResponse> {
  const res = await api.get<StockoutRiskResponse>("/analytics/stockout-risk", {
    params,
  })
  return res.data
}

export async function getCrossSell(params: {
  product_id: string
  days?: number
  limit?: number
  min_support?: number
}): Promise<CrossSellResponse> {
  const res = await api.get<CrossSellResponse>("/analytics/cross-sell", {
    params,
  })
  return res.data
}
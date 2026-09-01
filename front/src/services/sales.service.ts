import { httpGet, httpPost } from "./http"
import type { Sale, SaleCreate } from "@/types"

export async function listSales(): Promise<Sale[]> {
  return httpGet<Sale[]>("/sales/")
}

export async function getSale(id: string): Promise<Sale> {
  return httpGet<Sale>(`/sales/${id}`)
}

export async function registerSale(payload: SaleCreate): Promise<Sale> {
  return httpPost<Sale>("/sales/", payload)
}

/** Devuelve (cancela) una venta completa. Reintegra el stock. */
export async function returnSale(id: string): Promise<Sale> {
  return httpPost<Sale>(`/sales/${id}/return`)
}

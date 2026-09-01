import { httpGet, httpPost } from "./http"
import type { Purchase, PurchaseCreate } from "@/types"

export async function listPurchases(): Promise<Purchase[]> {
  return httpGet<Purchase[]>("/purchases/")
}

export async function registerPurchase(
  payload: PurchaseCreate,
): Promise<Purchase> {
  return httpPost<Purchase>("/purchases/", payload)
}

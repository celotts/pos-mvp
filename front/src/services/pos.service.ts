import { httpGet, httpPost } from "./http"
import type { PosTerminal, Shift, ShiftOpen } from "@/types"
import { api } from "@/lib/api"
import type { ApiResponse } from "@/types"

export interface PosTerminalPayload {
  name: string
  location?: string | null
}

// ─── Terminales POS ─────────────────────────────────────────────────────────

export async function listTerminals(): Promise<PosTerminal[]> {
  return httpGet<PosTerminal[]>("/terminals/")
}

export async function createTerminal(
  payload: PosTerminalPayload,
): Promise<PosTerminal> {
  return httpPost<PosTerminal>("/terminals/", payload)
}

export async function updateTerminal(
  id: string,
  payload: PosTerminalPayload,
): Promise<PosTerminal> {
  const res = await api.put<ApiResponse<PosTerminal>>(`/terminals/${id}`, payload)
  return res.data.data
}

export async function deleteTerminal(id: string): Promise<void> {
  await api.delete(`/terminals/${id}`)
}

// ─── Turnos (shifts) ────────────────────────────────────────────────────────

export async function openShift(payload: ShiftOpen): Promise<Shift> {
  return httpPost<Shift>("/shifts/open", payload)
}

export async function closeShift(
  shiftId: string,
  payload: { ending_cash?: number | string; notes?: string | null },
): Promise<Shift> {
  const res = await api.put<ApiResponse<Shift>>(
    `/shifts/${shiftId}/close`,
    payload,
  )
  return res.data.data
}

export async function listShifts(): Promise<Shift[]> {
  return httpGet<Shift[]>("/shifts/")
}

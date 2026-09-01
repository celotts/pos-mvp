import { httpPost } from "./http"
import type { ChatRequest, ChatResponse } from "@/types"

export interface ChatResult {
  answer: string
  insights: { category: string }[]
}

/**
 * Consulta el agente de Inteligencia de Negocio (IA). El backend usa ReAct
 * con herramientas que consultan la BD real, y degrada a RAG si falla.
 */
export async function assistantChat(
  message: string,
  contextStoreId?: string | null,
): Promise<ChatResult> {
  const payload: ChatRequest = {
    message,
    context_store_id: contextStoreId ?? null,
  }
  const res = await httpPost<ChatResponse>("/assistant/chat", payload)
  return {
    answer: res.answer,
    insights: res.insights ?? [],
  }
}

export async function analyzeInventoryFlow(
  message: string,
  contextStoreId?: string | null,
): Promise<{ answer: string }> {
  const payload: ChatRequest = {
    message,
    context_store_id: contextStoreId ?? null,
  }
  const res = await httpPost<ChatResponse>(
    "/assistant/analyze-inventory-flow",
    payload,
  )
  return { answer: res.answer }
}

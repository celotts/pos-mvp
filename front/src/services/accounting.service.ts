import { httpGet, httpPost, httpPut, httpDelete } from "./http"
import type {
  CashAccount,
  CashAccountType,
  AccountsPayable,
  AccountsReceivable,
  AccountStatus,
} from "@/types"

// ─── Cuentas de Efectivo / Banco ────────────────────────────────────────────

export async function listCashAccounts(): Promise<CashAccount[]> {
  return httpGet<CashAccount[]>("/cash-accounts/")
}

export async function createCashAccount(payload: {
  name: string
  account_type: CashAccountType
}): Promise<CashAccount> {
  return httpPost<CashAccount>("/cash-accounts/", payload)
}

export async function updateCashAccount(
  id: string,
  payload: { name: string; account_type: CashAccountType },
): Promise<CashAccount> {
  return httpPut<CashAccount>(`/cash-accounts/${id}`, payload)
}

export async function deleteCashAccount(id: string): Promise<void> {
  await httpDelete(`/cash-accounts/${id}`)
}

// ─── Cuentas por Pagar ──────────────────────────────────────────────────────

export async function listAccountsPayable(): Promise<AccountsPayable[]> {
  return httpGet<AccountsPayable[]>("/accounts-payable/")
}

export async function updateAccountPayable(
  id: string,
  payload: Partial<{
    outstanding_amount: number | string
    due_date: string | null
    status: AccountStatus
  }>,
): Promise<AccountsPayable> {
  return httpPut<AccountsPayable>(`/accounts-payable/${id}`, payload)
}

export async function deleteAccountPayable(id: string): Promise<void> {
  await httpDelete(`/accounts-payable/${id}`)
}

// ─── Cuentas por Cobrar ─────────────────────────────────────────────────────

export async function listAccountsReceivable(): Promise<AccountsReceivable[]> {
  return httpGet<AccountsReceivable[]>("/accounts-receivable/")
}

export async function updateAccountReceivable(
  id: string,
  payload: Partial<{
    outstanding_amount: number | string
    due_date: string | null
    status: AccountStatus
  }>,
): Promise<AccountsReceivable> {
  return httpPut<AccountsReceivable>(`/accounts-receivable/${id}`, payload)
}

export async function deleteAccountReceivable(id: string): Promise<void> {
  await httpDelete(`/accounts-receivable/${id}`)
}
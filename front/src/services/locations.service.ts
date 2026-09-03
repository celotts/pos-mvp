import { httpGet, httpPost, httpPut, httpDelete } from "./http"
import type { Country, StateProvince, Municipality, Specialty } from "@/types"

// ─── Países ─────────────────────────────────────────────────────────────────

export async function listCountries(): Promise<Country[]> {
  return httpGet<Country[]>("/countries/")
}

export async function createCountry(
  payload: { name: string; iso_code: string },
): Promise<Country> {
  return httpPost<Country>("/countries/", payload)
}

export async function updateCountry(
  id: string,
  payload: { name: string; iso_code: string },
): Promise<Country> {
  return httpPut<Country>(`/countries/${id}`, payload)
}

export async function deleteCountry(id: string): Promise<void> {
  await httpDelete(`/countries/${id}`)
}

// ─── Estados / Provincias ───────────────────────────────────────────────────

export async function listStates(): Promise<StateProvince[]> {
  return httpGet<StateProvince[]>("/states/")
}

export async function createState(
  payload: { name: string; country_id: string },
): Promise<StateProvince> {
  return httpPost<StateProvince>("/states/", payload)
}

export async function updateState(
  id: string,
  payload: { name: string; country_id: string },
): Promise<StateProvince> {
  return httpPut<StateProvince>(`/states/${id}`, payload)
}

export async function deleteState(id: string): Promise<void> {
  await httpDelete(`/states/${id}`)
}

// ─── Municipios ─────────────────────────────────────────────────────────────

export async function listMunicipalities(): Promise<Municipality[]> {
  return httpGet<Municipality[]>("/municipalities/")
}

export async function createMunicipality(
  payload: { name: string; state_id: string },
): Promise<Municipality> {
  return httpPost<Municipality>("/municipalities/", payload)
}

export async function updateMunicipality(
  id: string,
  payload: { name: string; state_id: string },
): Promise<Municipality> {
  return httpPut<Municipality>(`/municipalities/${id}`, payload)
}

export async function deleteMunicipality(id: string): Promise<void> {
  await httpDelete(`/municipalities/${id}`)
}

// ─── Especialidades ─────────────────────────────────────────────────────────

export async function listSpecialties(): Promise<Specialty[]> {
  return httpGet<Specialty[]>("/specialties/")
}

export async function createSpecialty(
  payload: { name: string; description?: string | null },
): Promise<Specialty> {
  return httpPost<Specialty>("/specialties/", payload)
}

export async function updateSpecialty(
  id: string,
  payload: { name: string; description?: string | null },
): Promise<Specialty> {
  return httpPut<Specialty>(`/specialties/${id}`, payload)
}

export async function deleteSpecialty(id: string): Promise<void> {
  await httpDelete(`/specialties/${id}`)
}
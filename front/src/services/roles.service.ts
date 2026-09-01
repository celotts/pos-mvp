import { api } from "@/lib/api"
import type { Role, RoleWithPermissions } from "@/types"
import type { ApiResponse } from "@/types"
import { httpGet, httpPost } from "./http"

export interface RolePayload {
  name: string
  description?: string | null
}

export async function listRoles(): Promise<RoleWithPermissions[]> {
  return httpGet<RoleWithPermissions[]>("/roles/")
}

export async function createRole(payload: RolePayload): Promise<Role> {
  return httpPost<Role>("/roles/", payload)
}

export async function assignRolePermissions(
  roleId: string,
  permissionCodes: string[],
): Promise<RoleWithPermissions> {
  const res = await api.put<ApiResponse<RoleWithPermissions>>(
    `/roles/${roleId}/permissions`,
    { permission_codes: permissionCodes },
  )
  return res.data.data
}

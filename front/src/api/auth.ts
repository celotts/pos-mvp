import { apiRequest } from './client'
import type { LoginResponseData, UserWithRole } from '../types'

/** Autentica con email y contraseña. Devuelve token + usuario (con rol). */
export async function login(
  email: string,
  password: string,
): Promise<LoginResponseData> {
  return apiRequest<LoginResponseData>('/v1/login/access-token', {
    method: 'POST',
    body: { username: email, password },
  })
}

/** Obtiene el usuario actual (con su rol) usando el token guardado. */
export async function fetchCurrentUser(): Promise<UserWithRole> {
  return apiRequest<UserWithRole>('/v1/users/me')
}
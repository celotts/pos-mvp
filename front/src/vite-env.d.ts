/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_ACCESS_TOKEN_EXPIRE_SECONDS?: string
  readonly VITE_TOKEN_REFRESH_MARGIN_SECONDS?: string
  readonly VITE_API_PROXY_TARGET?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

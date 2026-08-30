# Punto de configuración de pytest (rootdir: /app/backend/app).
# Las pruebas unitarias usan AsyncMock en vez de una BD real:
# los modelos incluyen pgvector, incompatible con sqlite de prueba.
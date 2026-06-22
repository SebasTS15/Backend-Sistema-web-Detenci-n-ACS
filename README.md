# Backend Tesis Apnea

Backend con FastAPI para consumir el modelo PyTorch `modelo_apnea_central_0-3.pth`, procesar ventanas de senal fisiologica y guardar consultas/resultados en PostgreSQL local.

## Instalacion

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` con los datos sensibles de tu proyecto: conexión a la base de datos, JWT y credenciales de acceso.

## Ejecutar

```powershell
uvicorn app.main:app --reload
```

Documentacion interactiva:

```text
http://127.0.0.1:8000/docs
```

## Autenticación JWT

Para obtener un token usa `POST /api/v1/auth/token` con JSON:

```json
{
  "username": "admin",
  "password": "admin"
}
```

Luego usa el header `Authorization: Bearer <token>` en los endpoints protegidos como `/api/v1/predict`.

## Entrada de prediccion

`POST /api/v1/predict`

Este endpoint ahora recibe archivos `multipart/form-data` con los formatos soportados: `.edf`, `.dat` y `.apn`.

Ejemplo con `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict" \
  -H "Authorization: Bearer <token>" \
  -F "archivo=@/ruta/a/registro.edf" \
  -F "usuario_id=1" \
  -F "paciente_id=paciente-001" \
  -F "metadata={\"fuente\": \"frontend\"}" \
  -F "normalize=true" \
  -F "guardar_resultado=true" \
  -F "guardar_historial=true"
```

La API lee el archivo, extrae las señales esperadas y ajusta la entrada a `3840 x 3`; si faltan muestras rellena con ceros, si sobran recorta, y si hay más/menos canales adapta a 3 canales.

## Nota sobre tablas existentes

El backend usa las tablas `usuarios`, `resultados` e `historial_consultas`. Como no se incluyo el esquema exacto, las inserciones usan columnas habituales:

- `resultados`: `usuario_id`, `paciente_id`, `prediccion`, `probabilidad`, `clase`, `modelo`, `metadata`, `created_at`
- `historial_consultas`: `usuario_id`, `endpoint`, `request`, `response`, `created_at`

Si tus tablas tienen otros nombres de columnas, ajusta `app/db/repositories.py`.

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

```json
{
  "usuario_id": 1,
  "paciente_id": "paciente-001",
  "signals": [
    [0.12, 0.03, 0.44],
    [0.10, 0.02, 0.41]
  ],
  "metadata": {
    "fuente": "frontend"
  },
  "guardar_resultado": true,
  "guardar_historial": true
}
```

La API ajusta la entrada a `3840 x 3`: si faltan muestras rellena con ceros, si sobran recorta, y si llegan mas o menos canales adapta a 3 canales.

## Nota sobre tablas existentes

El backend usa las tablas `usuarios`, `resultados` e `historial_consultas`. Como no se incluyo el esquema exacto, las inserciones usan columnas habituales:

- `resultados`: `usuario_id`, `paciente_id`, `prediccion`, `probabilidad`, `clase`, `modelo`, `metadata`, `created_at`
- `historial_consultas`: `usuario_id`, `endpoint`, `request`, `response`, `created_at`

Si tus tablas tienen otros nombres de columnas, ajusta `app/db/repositories.py`.

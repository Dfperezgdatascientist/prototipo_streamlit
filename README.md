# Autoservicio Data & IA — Diners Club

Plataforma web en Python/Streamlit para ejecución de procesos batch con autenticación, auditoría y exportación a Excel.

## Estructura
```
autoservicio/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── deploy.sh           # Script de despliegue en servidor físico
└── audit_log.jsonl     # Log de auditoría (se genera al ejecutar)
```

## Instalación local (desarrollo)
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en servidor físico
```bash
bash deploy.sh
# Disponible en http://IP_SERVIDOR:8080
```

## Usuarios de prueba
| Usuario       | Contraseña  | Rol            |
|---------------|-------------|----------------|
| demo          | demo        | Demo           |
| sandra.ortiz  | Diners2024! | Analista Senior|
| admin         | Admin123!   | Admin          |

## Jobs disponibles
| Job                  | Descripción                                      |
|----------------------|--------------------------------------------------|
| Carga desde SFTP     | Lee archivos SFTP y los carga a Teradata         |
| Consulta Teradata    | Ejecuta SQL sobre DWH_PRESTAGE                   |
| Reporte IA Agents    | Genera reporte de alertas por fecha              |
| Ingreso Manual       | Formulario de captura + exportación Excel        |

## Para conectar Teradata real
En `app.py`, reemplaza las funciones `run_job_*` con llamadas reales a `teradatasql`.

## Migración a Databricks
Streamlit es compatible nativamente con Databricks Apps — 
cuando llegue la migración, el código se reutiliza sin reescribir.
```

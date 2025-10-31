# Ventas Viaje X Mundo

Este es el repositorio del proyecto Ventas Viaje X Mundo, donde se gestionarán las ventas de viajes y servicios turísticos.

## Arquitectura actual

La primera iteración del sistema implementa un backend en **FastAPI + SQLModel** que permite:

- Administrar agentes de la agencia.
- Crear y editar vouchers de viaje con control de estado.
- Registrar movimientos de ingresos y egresos asociados a cada voucher y agente.
- Consultar un tablero financiero con totales de ingresos, egresos y saldo pendiente.

La base de datos utiliza SQLite y se crea automáticamente en `backend/data/viajexmundo.db`.

## Puesta en marcha

1. Crear y activar un entorno virtual de Python 3.11 o superior.
2. Instalar dependencias (desde la raíz del repositorio):

   ```bash
   pip install -r requirements.txt
   ```

   > Si prefieres ejecutar el comando dentro del directorio `backend/`, utiliza `pip install -r requirements.txt` sin el prefijo `backend/`.

3. Ejecutar la API:

   ```bash
   uvicorn backend.app.main:app --reload
   ```

La documentación interactiva estará disponible en `http://127.0.0.1:8000/docs`.

## Pruebas

Para validar el flujo principal existe una prueba automatizada que puede ejecutarse con:

```bash
pytest backend/tests
```

## Próximos pasos sugeridos

- Añadir autenticación de usuarios y control de permisos.
- Construir el front-end web para los agentes internos.
- Incorporar exportación de vouchers en PDF y reportes contables.

## Licencia

Este proyecto está bajo la Licencia MIT.
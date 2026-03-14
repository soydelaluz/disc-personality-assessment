# Instrucciones Técnicas para Integración del Sistema DISC

Este documento está diseñado para que un Agente de IA pueda implementar la integración del módulo DISC en la aplicación "Manual de Perfiles Técnicos".

## Cambios Realizados en el Repositorio
Se ha transformado una aplicación monolítica de Streamlit en un sistema modular preparado para integración:
1.  **`disc_core.py`**: Contiene la lógica matemática de puntuación, normalización y cálculo de vectores DISC. Es independiente de la UI.
2.  **`disc_report.py`**: Maneja la generación de reportes PDF profesionales usando `reportlab`.
3.  **`api.py`**: Servicio FastAPI que expone la lógica DISC a través de endpoints REST (`/questions`, `/evaluate`).
4.  **`strengths.json`**: Base de datos de fortalezas corregida y optimizada.

## Flujo de Integración Recomendado

### 1. Portal del Usuario (Área de Exámenes)
- **Implementación**: Crear una nueva pestaña o sección "Evaluación de Personalidad" en el portal del estudiante/colaborador.
- **Acción**: El frontend de React debe consumir `/questions` del servicio Python para presentar el cuestionario.
- **Finalización**: Una vez enviado, el backend de Express debe enviar las respuestas a `/evaluate` del servicio Python.
- **Persistencia**: Guardar el resultado (JSON) en la tabla de `technicians` o una nueva tabla `disc_results` vinculada al `technician_id`.
- **UI Post-Examen**: El usuario solo debe ver un mensaje confirmando que ha terminado: *"Evaluación completada con éxito"* e información mínima (ej. la fecha de realización). **No mostrar resultados detallados al usuario.**

### 2. Panel Administrativo (Área de Performance)
- **Implementación**: Dentro de la gestión de desempeño (Performance Management), al ver el perfil detallado de un técnico.
- **Visibilidad**: Solo roles con permisos de `recursos_humanos`, `admin_global` o `superadmin` deben tener acceso a esta información.
- **Contenido**:
    - Mostrar el gráfico DISC (el backend puede solicitar el vector al servicio Python).
    - Mostrar la descripción personalizada del perfil, fortalezas y desafíos.
    - Botón para **Descargar Reporte PDF** (el backend de Express puede hacer proxy a la función de generación de PDF o solicitar el buffer al servicio Python).
    - Acceso al JSON bruto si es necesario para analíticas avanzadas.

### 3. Seguridad y RBAC
- Asegurar que los endpoints de lectura de resultados DISC en Express.js estén protegidos por los guards de roles correspondientes.
- La lógica de "Solo Admin ve los resultados" se implementa en la capa de UI de React filtrando por el `permissions_json` del usuario actual.

## Pasos para el Agente de IA:
1.  **Levantar el servicio Python**: Asegurarse de que `python api.py` corra junto al backend de Node.js.
2.  **Modificar base de datos**: Añadir soporte para almacenar el objeto de resultados DISC vinculado al técnico.
3.  **Crear Componente React**: Un componente de formulario dinámico que itere sobre las preguntas de la API.
4.  **Configurar Rutas de Express**: Endpoints que actúen como puente entre el frontend y el servicio de IA en Python.

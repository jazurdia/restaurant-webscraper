# Restaurant Webscraper — Proyecto 2 (Sesgos y Equidad)

## Descripción

Este repositorio contiene un scraper automatizado para recolectar reseñas de restaurantes en Manhattan desde Google Maps, utilizando el Actor oficial `compass/google-maps-reviews-scraper` de Apify. El proyecto está diseñado para analizar **sesgos y equidad** en las opiniones públicas sobre restaurantes en diferentes barrios con distintos perfiles socioeconómicos.

### Objetivo del Proyecto

Extraer y analizar un conjunto de datos real (2,000+ reseñas) para identificar potenciales sesgos en:
- Calificaciones y lenguaje según el barrio
- Representación y acceso a plataformas de reseñas
- Expectativas y estándares aplicados a diferentes tipos de establecimientos
- Patrones de respuesta de propietarios

---

## Características Principales

- **Multi-cuenta inteligente**: Usa múltiples tokens de Apify para maximizar créditos gratuitos ($5 por cuenta)
- **Cambio automático de tokens**: Detecta cuando un token se queda sin créditos y cambia al siguiente automáticamente
- **Actor oficial de Apify**: Utiliza `compass/google-maps-reviews-scraper` con esquema de salida validado
- **Guardado progresivo**: Guarda resultados cada 5 restaurantes para prevenir pérdida de datos
- **Manejo robusto de errores**: Reintentos exponenciales, detección de errores de créditos, y guardado de emergencia
- **Logging detallado**: Seguimiento completo del proceso con timestamps y niveles de severidad
- **Formato flexible**: Exporta resultados en CSV y JSON

---

## Estructura del Repositorio

```
restaurant-webscraper/
├── webscraper.py                    # Script principal con ApifyMultiAccountScraper
├── pyproject.toml                   # Configuración de dependencias (uv)
├── uv.lock                          # Lock file de dependencias
├── .gitignore                       # Archivos a ignorar en git
├── config/
│   ├── __init__.py                  # Hacer config un paquete Python
│   └── personal_tokens.py           # Tokens de Apify
├── rest_data/
│   ├── high_income.json             # Restaurantes de barrios alto ingreso
│   ├── mid_income.json              # Restaurantes de barrios ingreso medio
│   └── low_income.json              # Restaurantes de barrios ingreso bajo
├── Instrucciones Proyecto 2.md      # Requerimientos del proyecto
└── README.md                        # Este archivo
```

---

## Requisitos del Sistema

- **Python**: 3.10 o superior
- **uv**: Manejador de paquetes ultra-rápido (reemplazo de pip/venv)
- **Sistema Operativo**: Windows, macOS, o Linux
- **Conexión a Internet**: Requerida para scraping

---

## Instalación y Configuración

### Paso 1: Instalar uv

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verifica la instalación:
```bash
uv --version
```

### Paso 2: Clonar el repositorio

```bash
git clone https://github.com/jazurdia/restaurant-webscraper
cd restaurant-webscraper
```

### Paso 3: Instalar dependencias

```bash
uv sync
```

Este comando:
- Crea automáticamente un entorno virtual en `.venv`
- Instala todas las dependencias (`apify-client`, `pandas`)
- Genera/actualiza `uv.lock` para reproducibilidad

**Nota**: No necesitas activar manualmente el entorno virtual. `uv` lo maneja automáticamente.

### Paso 4: Configurar tokens de Apify

Edita `config/personal_tokens.py`:

```python
APIFY_TOKENS = [
    "apify_api_TU_TOKEN_1_AQUI",
    "apify_api_TU_TOKEN_2_AQUI",
    "apify_api_TU_TOKEN_3_AQUI",
    "apify_api_TU_TOKEN_4_AQUI",
]
```

Reemplaza los valores de ejemplo con tus tokens reales de Apify.

### Paso 5: Preparar datos de restaurantes

Los archivos en `rest_data/` contienen listas de restaurantes en formato JSON.

#### Estructura de cada archivo JSON:

```json
[
  {
    "url": "https://www.google.com/maps/place/Restaurant+Name/@40.7614,-73.9799,17z/...",
    "name": "Restaurant Name",
    "neighborhood": "Upper East Side",
    "cuisine_type": "Italian"
  },
  {
    "url": "https://www.google.com/maps/place/Another+Restaurant/@40.7656,-73.9877,17z/...",
    "name": "Another Restaurant Name",
    "neighborhood": "Upper East Side",
    "cuisine_type": "Japanese"
  }
]
```

#### Campos requeridos:
- `url`: URL completa de Google Maps del restaurante
- `name`: Nombre del restaurante
- `neighborhood`: Nombre del barrio (debe ser consistente)
- `cuisine_type`: Tipo de cocina (opcional, pero recomendado)

---

## Ejecución

### Ejecutar el scraper

```bash
uv run webscraper.py
```

**Nota**: `uv run` automáticamente usa el entorno virtual correcto.

### Qué esperar durante la ejecución

El scraper mostrará logs detallados:

```
[2025-01-15 10:30:00] INFO: Initialized with 4 Apify accounts
[2025-01-15 10:30:00] INFO: Estimated capacity: ~40000 reviews
[2025-01-15 10:30:00] INFO: Loaded 45 restaurants from 3 files
[2025-01-15 10:30:05] INFO: ============================================================
[2025-01-15 10:30:05] INFO: Scraping: Daniel (Upper East Side)
[2025-01-15 10:30:05] INFO: ============================================================
[2025-01-15 10:30:05] INFO: Attempt 1/3 using account #1
[2025-01-15 10:30:35] INFO: Scraper completed. Dataset ID: abc123xyz
[2025-01-15 10:30:36] INFO: Successfully extracted 50 reviews from Daniel
```

### Archivos de salida

Al finalizar encontrarás:

1. **Archivos finales**:
   - `manhattan_reviews_final.csv`: Todos los datos en formato CSV
   - `manhattan_reviews_final.json`: Todos los datos en formato JSON

2. **Archivos de progreso** (cada 5 restaurantes):
   - `reviews_progress_5.csv`
   - `reviews_progress_10.csv`
   - `reviews_progress_15.csv`
   - etc.

3. **Archivo de emergencia** (solo si hay error fatal):
   - `manhattan_reviews_emergency_save.csv`

### Estructura de los datos recolectados

Cada review incluye:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `restaurant_name` | Nombre del restaurante | "Daniel" |
| `neighborhood` | Barrio | "Upper East Side" |
| `cuisine_type` | Tipo de cocina | "French" |
| `place_url` | URL de Google Maps | "https://..." |
| `reviewer_name` | Nombre del reviewer | "John D." |
| `rating` | Calificación (1-5) | 5 |
| `review_text` | Texto de la reseña | "Excellent food..." |
| `review_length` | Longitud del texto | 145 |
| `published_date` | Fecha de publicación | "2 months ago" |
| `published_timestamp` | Timestamp Unix | 1698765432 |
| `likes_count` | Número de "me gusta" | 12 |
| `reviewer_total_reviews` | Total reviews del autor | 245 |
| `is_local_guide` | Es guía local | true/false |
| `owner_response` | Respuesta del dueño | "Thank you..." |
| `review_id` | ID único de review | "abc123" |
| `review_url` | URL directa a review | "https://..." |

---

## Estructura del Código

### Clase Principal: `ApifyMultiAccountScraper`

```python
class ApifyMultiAccountScraper:
    """
    Gestiona múltiples tokens de Apify y coordina el scraping
    """
    
    # Métodos principales:
    __init__(api_tokens, max_retries)           # Inicializar con tokens
    scrape_restaurant_reviews(...)              # Scraper individual
    scrape_multiple_restaurants(...)            # Scraper por lotes
    get_next_available_client(check_credits)    # Gestión de tokens
    check_token_credits(client, token_index)    # Verificar créditos
    save_to_csv(filename)                       # Guardar en CSV
    save_to_json(filename)                      # Guardar en JSON
    get_summary_stats()                         # Estadísticas
```

### Flujo de Ejecución

```
1. Cargar tokens desde config/personal_tokens.py
2. Cargar restaurantes desde rest_data/*.json
3. Inicializar ApifyMultiAccountScraper
4. Para cada restaurante:
   a. Seleccionar token disponible (round-robin)
   b. Ejecutar Actor de Apify
   c. Extraer y normalizar datos
   d. Guardar progreso cada 5 restaurantes
   e. Si hay error de créditos, cambiar token
5. Guardar resultados finales (CSV + JSON)
6. Mostrar estadísticas sumarias
```

---

## Contribuyentes

**Integrantes del Proyecto:**
- **Javier Azurdia** — 21242
- **Angel Castellanos** — 21700
- **Diego Morales** — 21146

**Curso**: Inteligencia Artificial Responsable  
**Institución**: Universidad del Valle de Guatemala  
**Fecha**: Enero 2025

---

## Licencia

Este proyecto es material académico desarrollado para fines educativos. No está licenciado para uso comercial.

---

## Referencias y Recursos

### Documentación de Herramientas
- [Apify Documentation](https://docs.apify.com/)
- [Google Maps Reviews Scraper Actor](https://apify.com/compass/google-maps-reviews-scraper)
- [uv Documentation](https://docs.astral.sh/uv/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
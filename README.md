
# API de Condonaciones - Sparta Ledger

API desarrollada en Python con FastAPI para la gestión de condonaciones de crédito.

##  Características

- **FastAPI**: Framework moderno y rápido para construir APIs
- **Validación automática**: Usando Pydantic
- **Documentación interactiva**: Swagger UI y ReDoc
- **Múltiples endpoints**: Consulta todos, solo condonados, o pendientes
- **Manejo de errores**: Respuestas estructuradas

##  Requisitos

- Python 3.8 o superior
- MySQL/MariaDB con las bases de datos:
  - `db-mega-reporte` (contiene tbl_segundometro_semana y gastos_cobranza)

##  Instalación

### 1. Crear entorno virtual

```bash
cd api_python
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y ajusta los valores:

```bash
copy .env.example .env
```

Edita `.env` con tus credenciales de base de datos:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_DATABASE=db-mega-reporte
DB_SEGUNDOMETRO=segundometro
```

##  Ejecución

### Modo desarrollo

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

##  Documentación

Una vez iniciada la API, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

##  Endpoints

###  Autenticación

**Todos los endpoints requieren un API Key válido en el header:**

```http
X-API-Key: tu-api-key-aqui
```

### 1. Obtener condonación por ID de crédito

Retorna los gastos de cobranza **condonados** (`condonado = 1`). Si no hay gastos condonados, retorna array vacío.

```http
GET /api/condonaciones/{id_credito}
```

**Ejemplo:**
```bash
curl -H "X-API-Key: APIKEY" \
     http://localhost:8000/api/condonaciones/12345
```

**Respuesta:**
```json
{
  "status_code": 200,
  "status_message": "OK",
  "success": true,
  "mensaje": "Se encontraron 2 gastos condonados",
  "datos_generales": {
    "id_credito": 12345,
    "nombre_cliente": "Juan Pérez García",
    "id_cliente": 67890,
    "domicilio_completo": "Calle Principal #123, Col. Centro",
    "bucket_morosidad": "B2",
    "dias_mora": 15,
    "saldo_vencido": 3500.00
  },
  "condonacion_cobranza": {
    "detalle": [
      {
        "periodoinicio": "2026-01-01",
        "periodofin": "2026-01-07",
        "semana": "2026-01",
        "parcialidad": "1/52",
        "monto_valor": 150.50,
        "cuota": 150.00,
        "condonado": 1,
        "fecha_condonacion": "2026-01-28T10:30:00"
      }
    ]
  }
}
```

**Si no hay gastos condonados:**
```json
{
  "status_code": 200,
  "status_message": "OK",
  "success": true,
  "mensaje": "No hay gastos condonados para este crédito",
  "datos_generales": { ... },
  "condonacion_cobranza": {
    "detalle": []
  }
}
```

### 2. Obtener solo gastos condonados

Retorna únicamente los gastos que ya fueron condonados (condonado = 1).

```http
GET /api/condonaciones/{id_credito}/solo-condonados
```

**Ejemplo:**
```bash
curl -H "X-API-Key: APIKEY" \
     http://localhost:8000/api/condonaciones/12345/solo-condonados
```

### 3. Obtener gastos pendientes de condonar

Retorna únicamente los gastos que NO han sido condonados.

```http
GET /api/condonaciones/{id_credito}/pendientes
```

**Ejemplo:**
```bash
curl -H "X-API-Key: APIKEY" \
     http://localhost:8000/api/condonaciones/12345/pendientes
```

##  Estructura del Proyecto

```
api_python/
├── main.py                 # Archivo principal de la API
├── requirements.txt        # Dependencias de Python
├── .env.example           # Ejemplo de variables de entorno
├── .env                   # Variables de entorno (no incluir en git)
├── .gitignore            # Archivos ignorados por git
├── README.md             # Documentación
├── test_api.py           # Script de pruebas
├── config/               # Configuraciones
│   ├── __init__.py
│   ├── database.py       # Configuración de base de datos
│   └── security.py       # Sistema de autenticación
├── models/               # Modelos Pydantic
│   ├── __init__.py
│   └── condonaciones.py  # Modelos de condonación
├── routers/              # Rutas/Endpoints
│   ├── __init__.py
│   └── condonaciones.py  # Router de condonaciones
└── utils/                # Utilidades
    ├── __init__.py
    └── validations.py    # Validaciones de negocio
```

##  Estructura de Datos

### Base de datos: `db-mega-reporte`

**Tabla: `tbl_segundometro_semana`**
Contiene los datos generales del cliente y crédito.

**Tabla: `gastos_cobranza`**
Contiene los detalles de gastos de cobranza con los siguientes campos:
- `periodo_inicio`
- `periodo_fin`
- `SEMANA`
- `parcialidad`
- `monto_valor`
- `cuota`
- `condonado` (0 o 1)
- `fecha_condonacion`

##  Tecnologías Utilizadas

- **FastAPI**: Framework web
- **Pydantic**: Validación de datos
- **PyMySQL**: Conexión a MySQL
- **Uvicorn**: Servidor ASGI
- **Python-dotenv**: Manejo de variables de entorno

##  Seguridad

La API está protegida con **API Keys**:

### Generar una nueva API Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Configurar API Keys

Agrega las API Keys en el archivo `.env`:

```env
API_KEYS=key1,key2,key3
```

Puedes tener múltiples API Keys separadas por comas (una por cliente/aplicación).

### Usar la API Key

Incluye el header `X-API-Key` en todas tus peticiones:

```bash
curl -H "X-API-Key: tu-api-key" http://localhost:8000/api/condonaciones/12345
```

### Desde PHP:

```php
$api_key = "APIKEY";
$id_credito = 12345;
$url = "http://localhost:8000/api/condonaciones/" . $id_credito;

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "X-API-Key: $api_key"
]);
$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);
```

### Respuestas de Error de Autenticación

**Sin API Key o API Key inválida:**
```json
{
  "detail": "API Key inválida o no autorizada"
}
```
Status: `401 Unauthorized`

##  Manejo de Errores

La API retorna códigos de estado HTTP estándar:

| Código | Significado | Responsable | Descripción |
|--------|-------------|-------------|-------------|
| `200` | Todo bien | Nadie | Operación exitosa |
| `400` | Request mal formado | Cliente | ID inválido o datos incorrectos |
| `401` | No autenticado | Cliente | API Key inválida o faltante |
| `404` | No encontrado | Cliente | Crédito no existe |
| `422` | Entidad no procesable | Cliente | Tipo de dato inválido (texto en lugar de número) |
| `500` | Error del servidor | Backend | Error interno de base de datos o servidor |

### Ejemplos de Respuestas

**Éxito (200):**
```json
{
  "status_code": 200,
  "status_message": "OK",
  "success": true,
  "mensaje": "Se encontraron 3 gastos condonados",
  "datos_generales": { ... },
  "condonacion_cobranza": { ... }
}
```

**Bad Request (400):**
```json
{
  "detail": "El ID del crédito no puede tener todos los dígitos iguales (1111111)"
}
```

**No Autenticado (401):**
```json
{
  "detail": "API Key inválida o no autorizada"
}
```

**Entidad No Procesable (422):**
```json
{
  "status_code": 422,
  "status_message": "Unprocessable Entity",
  "success": false,
  "mensaje": "El campo 'id_credito' debe ser mayor a 0. Valor recibido: 0",
  "detail": [ ... ]
}
```

**No Encontrado (404):**

**No Encontrado (404):**
```json
{
  "detail": "No se encontró información del crédito 99999. Verifica que el ID sea correcto."
}
```

**Error del Servidor (500):**
```json
{
  "detail": "Error de base de datos: Connection refused"
}
```

##  Seguridad

- ✅ Autenticación mediante API Keys
- ✅ Las credenciales de base de datos se manejan mediante variables de entorno
- ✅ Validación automática de entrada con Pydantic
- ✅ Uso de prepared statements para prevenir SQL injection
- ✅ Control de acceso por cliente mediante API Keys únicas

##  Notas

- Asegúrate de que las bases de datos estén accesibles desde el servidor de la API
- Los nombres de las bases de datos deben coincidir con tu configuración de MySQL
- La API usa conexiones con context managers para asegurar el cierre apropiado de conexiones

##  Integración con PHP

Esta API puede ser consumida desde tu aplicación PHP existente usando cURL o Guzzle:

```php
<?php
$api_key = "APIKEY";
$id_credito = 12345;
$url = "http://localhost:8000/api/condonaciones/" . $id_credito;

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "X-API-Key: $api_key"
]);
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http_code === 200) {
    $data = json_decode($response, true);
    
    // Verificar estado de la respuesta
    if ($data['success']) {
        echo "Código HTTP: " . $data['status_code'] . " - " . $data['status_message'] . "\n";
        echo "Cliente: " . $data['datos_generales']['nombre_cliente'] . "\n";
        echo "Gastos condonados: " . count($data['condonacion_cobranza']['detalle']) . "\n";
    }
} else {
    echo "Error HTTP: " . $http_code . "\n";
    echo "Detalle: " . $response;
}
?>
```

##  Soporte

Para problemas o preguntas, consulta la documentación interactiva en `/docs` o contacta al equipo de desarrollo.

---

**Versión**: 1.0.0  
**Última actualización**: 28 de Enero 2026

# API-GET-ConsumoCondonaciones


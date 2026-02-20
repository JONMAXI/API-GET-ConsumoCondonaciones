"""
Modelos Pydantic para Condonaciones
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime, date


class DetalleCondonacion(BaseModel):
    """Modelo para detalle de condonación (gastos de cobranza)"""
    
    periodoinicio: Optional[date] = Field(None, description="Fecha inicio del periodo")
    periodofin: Optional[date] = Field(None, description="Fecha fin del periodo")
    semana: Optional[Union[str, int]] = Field(None, description="Semana del gasto")
    parcialidad: Optional[Union[str, int]] = Field(None, description="Parcialidad")
    monto_valor: Optional[float] = Field(None, description="Monto del gasto")
    cuota: Optional[float] = Field(None, description="Cuota")
    condonado: Optional[int] = Field(None, description="Marca si está condonado (0 o 1)")
    fecha_condonacion: Optional[datetime] = Field(None, description="Fecha de condonación")
    status: Optional[str] = Field(None, description="Estatus del gasto: CONDONADO o PENDIENTE")
    
    class Config:
        json_schema_extra = {
            "example": {
                "periodoinicio": "2026-01-01",
                "periodofin": "2026-01-07",
                "semana": "2026-01",
                "parcialidad": "1/52",
                "monto_valor": 150.50,
                "cuota": 150.00,
                "condonado": 1,
                "fecha_condonacion": "2026-01-28T10:30:00",
                "status": "CONDONADO"
            }
        }


class DatosGenerales(BaseModel):
    """Modelo para datos generales del cliente/crédito"""
    
    id_credito: Optional[int] = Field(None, description="ID del crédito")
    nombre_cliente: Optional[str] = Field(None, description="Nombre del cliente")
    id_cliente: Optional[int] = Field(None, description="ID del cliente")
    domicilio_completo: Optional[str] = Field(None, description="Domicilio del cliente")
    bucket_morosidad: Optional[str] = Field(None, description="Bucket de morosidad")
    dias_mora: Optional[int] = Field(None, description="Días de mora")
    saldo_vencido: Optional[float] = Field(None, description="Saldo vencido")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_credito": 12345,
                "nombre_cliente": "Juan Pérez García",
                "id_cliente": 67890,
                "domicilio_completo": "Calle Principal #123, Col. Centro",
                "bucket_morosidad": "B2",
                "dias_mora": 15,
                "saldo_vencido": 3500.00
            }
        }


class CondonacionCobranza(BaseModel):
    """Modelo que agrupa los detalles de condonación"""
    
    detalle: List[DetalleCondonacion] = Field(
        default_factory=list,
        description="Lista de detalles de gastos de cobranza"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
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


class CondonacionResponse(BaseModel):
    """Modelo de respuesta completo para la API de condonaciones"""
    
    status_code: int = Field(200, description="Código HTTP de respuesta")
    status_message: str = Field("OK", description="Significado del código HTTP")
    success: bool = Field(True, description="Indica si la operación fue exitosa")
    mensaje: str = Field("", description="Mensaje de respuesta")
    datos_generales: Optional[DatosGenerales] = Field(None, description="Datos generales del cliente")
    condonacion_cobranza: Optional[CondonacionCobranza] = Field(None, description="Detalles de condonación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "status_message": "OK",
                "success": True,
                "mensaje": "Se encontraron 2 gastos condonados",
                "datos_generales": {
                    "id_credito": 12345,
                    "nombre_cliente": "Juan Pérez García",
                    "id_cliente": 67890,
                    "domicilio_completo": "Calle Principal #123",
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
        }


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    
    success: bool = Field(False, description="Indica que hubo un error")
    mensaje: str = Field("", description="Mensaje de error")
    error: Optional[str] = Field(None, description="Detalle del error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "mensaje": "No se encontraron datos para el crédito",
                "error": None
            }
        }

        
class ResumenGeneral(BaseModel):
    """Modelo para el resumen estadístico del endpoint general"""
    
    total_registros: int = Field(..., description="Total de registros encontrados")
    condonados: int = Field(..., description="Total de registros condonados")
    pendientes: int = Field(..., description="Total de registros pendientes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_registros": 5,
                "condonados": 2,
                "pendientes": 3
            }
        }


class ResponseGeneral(BaseModel):
    """Modelo de respuesta para el endpoint general con STATUS"""
    
    status_code: int = Field(200, description="Código HTTP de respuesta")
    status_message: str = Field("OK", description="Significado del código HTTP")
    success: bool = Field(True, description="Indica si la operación fue exitosa")
    mensaje: str = Field("", description="Mensaje de respuesta")
    datos_generales: DatosGenerales = Field(..., description="Datos generales del cliente")
    resumen: ResumenGeneral = Field(..., description="Resumen estadístico")
    detalle: List[DetalleCondonacion] = Field(..., description="Lista completa de gastos con STATUS")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "status_message": "OK",
                "success": True,
                "mensaje": "Se encontraron 5 registros",
                "datos_generales": {
                    "id_credito": 12345,
                    "nombre_cliente": "Juan Pérez García",
                    "id_cliente": 67890,
                    "domicilio_completo": "Calle Principal #123",
                    "bucket_morosidad": "B2",
                    "dias_mora": 15,
                    "saldo_vencido": 3500.00
                },
                "resumen": {
                    "total_registros": 5,
                    "condonados": 2,
                    "pendientes": 3
                },
                "detalle": [
                    {
                        "periodoinicio": "2026-01-01",
                        "periodofin": "2026-01-07",
                        "semana": "2026-01",
                        "parcialidad": "1/52",
                        "monto_valor": 150.50,
                        "cuota": 150.00,
                        "condonado": 1,
                        "fecha_condonacion": "2026-01-28T10:30:00",
                        "status": "CONDONADO"
                    },
                    {
                        "periodoinicio": "2026-01-08",
                        "periodofin": "2026-01-14",
                        "semana": "2026-02",
                        "parcialidad": "2/52",
                        "monto_valor": 150.50,
                        "cuota": 150.00,
                        "condonado": 0,
                        "fecha_condonacion": None,
                        "status": "PENDIENTE"
                    }
                ]
            }
        }
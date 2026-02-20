"""
Router de Condonaciones
Endpoints para gestión de condonaciones de crédito
"""

from fastapi import APIRouter, HTTPException, Depends, Path, Security
from typing import Optional
import pymysql

from models.condonaciones import (
    CondonacionResponse,
    ErrorResponse,
    DatosGenerales,
    CondonacionCobranza,
    DetalleCondonacion
)
from config.database import get_db_connection
from config.security import verify_api_key
from utils.validations import validar_id_credito, validar_datos_encontrados

router = APIRouter()


@router.get(
    "/condonaciones/{id_credito}",
    response_model=CondonacionResponse,
    responses={
        200: {"description": "Éxito - Datos obtenidos correctamente"},
        400: {"description": "Bad Request - ID inválido o mal formado"},
        401: {"description": "No Autenticado - API Key inválida o faltante"},
        404: {"description": "No Encontrado - Crédito no existe"},
        500: {"description": "Error del Servidor - Error interno"}
    },
    summary="Obtener información de condonación por ID de crédito",
    description="Retorna los gastos de cobranza CONDONADOS (condonado=1). Si no hay gastos condonados, retorna array vacío."
)
async def get_condonacion_por_credito(
    id_credito: int = Path(..., description="ID del crédito a consultar", gt=0),
    api_key: str = Security(verify_api_key)
):
    """
    Obtiene información completa de condonación para un crédito específico.
    
    - **id_credito**: ID del crédito a consultar
    
    Retorna:
    - **datos_generales**: Información del cliente y crédito
    - **condonacion_cobranza**: Lista de detalles de gastos de cobranza
    """
    
    try:
        # Validar ID de crédito
        validar_id_credito(id_credito)
        
        # Obtener datos generales del cliente desde tbl_segundometro_semana
        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:
                query_datos_generales = """
                    SELECT 
                        Id_credito as id_credito,
                        Nombre_cliente as nombre_cliente,
                        Id_cliente as id_cliente,
                        Domicilio_Completo as domicilio_completo,
                        Bucket_Morosidad_Real as bucket_morosidad,
                        Dias_mora as dias_mora,
                        saldo_vencido_inicio as saldo_vencido
                    FROM tbl_segundometro_semana
                    WHERE Id_credito = %s
                    LIMIT 1
                """
                
                cursor.execute(query_datos_generales, (id_credito,))
                datos_generales_row = cursor.fetchone()
                
                # Validar que se encontraron datos
                validar_datos_encontrados(datos_generales_row, 'cliente', id_credito)
                
                # Convertir a modelo Pydantic
                datos_generales = DatosGenerales(**datos_generales_row)
        
        # Obtener gastos de cobranza desde db-mega-reporte (solo condonados)
        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:
                query_gastos = """
                    SELECT 
                        periodo_inicio as periodoinicio,
                        periodo_fin as periodofin,
                        SEMANA as semana,
                        parcialidad,
                        monto_valor,
                        cuota,
                        condonado,
                        fecha_condonacion
                    FROM gastos_cobranza
                    WHERE Id_credito = %s
                      AND condonado = 1
                    ORDER BY periodo_inicio ASC
                """
                
                cursor.execute(query_gastos, (id_credito,))
                detalles_rows = cursor.fetchall()
                
                # Convertir a modelos Pydantic (puede estar vacío si no hay condonados)
                detalles = [DetalleCondonacion(**row) for row in detalles_rows]
                
                condonacion_cobranza = CondonacionCobranza(detalle=detalles)
        
        # Construir respuesta
        mensaje = f"Se encontraron {len(detalles)} gastos condonados" if detalles else "No hay gastos condonados para este crédito"
        response = CondonacionResponse(
            status_code=200,
            status_message="OK",
            success=True,
            mensaje=mensaje,
            datos_generales=datos_generales,
            condonacion_cobranza=condonacion_cobranza
        )
        
        return response
        
    except HTTPException:
        raise
    except pymysql.Error as db_error:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(db_error)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/condonaciones/{id_credito}/solo-condonados",
    response_model=CondonacionResponse,
    responses={
        200: {"description": "Éxito - Datos obtenidos correctamente"},
        400: {"description": "Bad Request - ID inválido o mal formado"},
        401: {"description": "No Autenticado - API Key inválida o faltante"},
        404: {"description": "No Encontrado - Crédito no existe"},
        500: {"description": "Error del Servidor - Error interno"}
    },
    summary="Obtener solo gastos condonados",
    description="Retorna únicamente los gastos que ya fueron condonados (condonado = 1). Igual al endpoint principal."
)
async def get_solo_condonados(
    id_credito: int = Path(..., description="ID del crédito a consultar", gt=0),
    api_key: str = Security(verify_api_key)
):
    """
    Obtiene información de condonación mostrando solo los gastos ya condonados.
    
    - **id_credito**: ID del crédito a consultar
    
    Retorna solo los registros donde condonado = 1
    """
    
    try:
        # Validar ID de crédito
        validar_id_credito(id_credito)
        
        # Obtener datos generales
        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:
                query_datos_generales = """
                    SELECT 
                        Id_credito as id_credito,
                        Nombre_cliente as nombre_cliente,
                        Id_cliente as id_cliente,
                        Domicilio_Completo as domicilio_completo,
                        Bucket_Morosidad_Real as bucket_morosidad,
                        Dias_mora as dias_mora,
                        saldo_vencido_inicio as saldo_vencido
                    FROM tbl_segundometro_semana
                    WHERE Id_credito = %s
                    LIMIT 1
                """
                
                cursor.execute(query_datos_generales, (id_credito,))
                datos_generales_row = cursor.fetchone()
                
                # Validar que se encontraron datos
                validar_datos_encontrados(datos_generales_row, 'cliente', id_credito)
                
                datos_generales = DatosGenerales(**datos_generales_row)
        
        # Obtener solo gastos condonados
        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:
                query_gastos = """
                    SELECT 
                        periodo_inicio as periodoinicio,
                        periodo_fin as periodofin,
                        SEMANA as semana,
                        parcialidad,
                        monto_valor,
                        cuota,
                        condonado,
                        fecha_condonacion
                    FROM gastos_cobranza
                    WHERE Id_credito = %s
                      AND condonado = 1
                    ORDER BY periodo_inicio ASC
                """
                
                cursor.execute(query_gastos, (id_credito,))
                detalles_rows = cursor.fetchall()
                
                detalles = [DetalleCondonacion(**row) for row in detalles_rows]
                condonacion_cobranza = CondonacionCobranza(detalle=detalles)
        
        response = CondonacionResponse(
            status_code=200,
            status_message="OK",
            success=True,
            mensaje=f"Se encontraron {len(detalles)} gastos condonados",
            datos_generales=datos_generales,
            condonacion_cobranza=condonacion_cobranza
        )
        
        return response
        
    except HTTPException:
        raise
    except pymysql.Error as db_error:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(db_error)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/condonaciones/{id_credito}/pendientes",
    response_model=CondonacionResponse,
    responses={
        200: {"description": "Éxito - Datos obtenidos correctamente"},
        400: {"description": "Bad Request - ID inválido o mal formado"},
        401: {"description": "No Autenticado - API Key inválida o faltante"},
        404: {"description": "No Encontrado - Crédito no existe"},
        500: {"description": "Error del Servidor - Error interno"}
    },
    summary="Obtener solo gastos pendientes de condonar",
    description="Retorna únicamente los gastos que NO han sido condonados (condonado = 0 o NULL)"
)
async def get_pendientes_condonacion(
    id_credito: int = Path(..., description="ID del crédito a consultar", gt=0),
    api_key: str = Security(verify_api_key)
):
    """
    Obtiene información mostrando solo los gastos pendientes de condonación.
    
    - **id_credito**: ID del crédito a consultar
    
    Retorna solo los registros donde condonado IS NULL o condonado = 0
    """
    
    try:
        # Validar ID de crédito
        validar_id_credito(id_credito)
        
        # Obtener datos generales
        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:
                query_datos_generales = """
                    SELECT 
                        Id_credito as id_credito,
                        Nombre_cliente as nombre_cliente,
                        Id_cliente as id_cliente,
                        Domicilio_Completo as domicilio_completo,
                        Bucket_Morosidad_Real as bucket_morosidad,
                        Dias_mora as dias_mora,
                        saldo_vencido_inicio as saldo_vencido
                    FROM tbl_segundometro_semana
                    WHERE Id_credito = %s
                    LIMIT 1
                """
                
                cursor.execute(query_datos_generales, (id_credito,))
                datos_generales_row = cursor.fetchone()
                
                # Validar que se encontraron datos
                validar_datos_encontrados(datos_generales_row, 'cliente', id_credito)
                
                datos_generales = DatosGenerales(**datos_generales_row)
        
        # Obtener solo gastos pendientes
        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:
                query_gastos = """
                    SELECT 
                        periodo_inicio as periodoinicio,
                        periodo_fin as periodofin,
                        SEMANA as semana,
                        parcialidad,
                        monto_valor,
                        cuota,
                        condonado,
                        fecha_condonacion
                    FROM gastos_cobranza
                    WHERE Id_credito = %s
                      AND (condonado IS NULL OR condonado = 0)
                    ORDER BY periodo_inicio ASC
                """
                
                cursor.execute(query_gastos, (id_credito,))
                detalles_rows = cursor.fetchall()
                
                detalles = [DetalleCondonacion(**row) for row in detalles_rows]
                condonacion_cobranza = CondonacionCobranza(detalle=detalles)
        
        response = CondonacionResponse(
            status_code=200,
            status_message="OK",
            success=True,
            mensaje=f"Se encontraron {len(detalles)} gastos pendientes de condonación",
            datos_generales=datos_generales,
            condonacion_cobranza=condonacion_cobranza
        )
        
        return response
        
    except HTTPException:
        raise
    except pymysql.Error as db_error:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(db_error)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
@router.get(
    "/condonaciones/{id_credito}/general",
    responses={
        200: {"description": "Éxito - Datos obtenidos correctamente"},
        400: {"description": "Bad Request - ID inválido o mal formado"},
        401: {"description": "No Autenticado - API Key inválida o faltante"},
        404: {"description": "No Encontrado - Crédito no existe"},
        500: {"description": "Error del Servidor - Error interno"}
    },
    summary="Obtener información general con STATUS",
    description="Retorna TODOS los gastos (condonados y pendientes) con un campo STATUS que indica 'CONDONADO' o 'PENDIENTE'"
)
async def get_general(
    id_credito: int = Path(..., description="ID del crédito a consultar", gt=0),
    api_key: str = Security(verify_api_key)
):
    """
    Endpoint GENERAL que muestra toda la información con STATUS (PENDIENTE/CONDONADO)
    
    - **id_credito**: ID del crédito a consultar
    
    Retorna:
    - **datos_generales**: Información del cliente y crédito
    - **resumen**: Totales de registros condonados y pendientes
    - **detalle**: Lista completa con campo STATUS incluido
    """
    
    try:
        # Validar ID de crédito
        validar_id_credito(id_credito)
        
        # 1. Obtener datos generales del cliente
        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:
                query_datos_generales = """
                    SELECT 
                        Id_credito as id_credito,
                        Nombre_cliente as nombre_cliente,
                        Id_cliente as id_cliente,
                        Domicilio_Completo as domicilio_completo,
                        Bucket_Morosidad_Real as bucket_morosidad,
                        Dias_mora as dias_mora,
                        saldo_vencido_inicio as saldo_vencido
                    FROM tbl_segundometro_semana
                    WHERE Id_credito = %s
                    LIMIT 1
                """
                
                cursor.execute(query_datos_generales, (id_credito,))
                datos_generales_row = cursor.fetchone()
                
                # Validar que se encontraron datos
                validar_datos_encontrados(datos_generales_row, 'cliente', id_credito)
                
                # Convertir a diccionario con tipos correctos
                datos_generales = {
                    "id_credito": datos_generales_row['id_credito'],
                    "nombre_cliente": datos_generales_row['nombre_cliente'],
                    "id_cliente": datos_generales_row['id_cliente'],
                    "domicilio_completo": datos_generales_row['domicilio_completo'],
                    "bucket_morosidad": datos_generales_row['bucket_morosidad'],
                    "dias_mora": datos_generales_row['dias_mora'],
                    "saldo_vencido": float(datos_generales_row['saldo_vencido']) if datos_generales_row['saldo_vencido'] else 0
                }
        
        # 2. Obtener TODOS los gastos con STATUS
        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:
                query_gastos = """
                    SELECT 
                        periodo_inicio as periodoinicio,
                        periodo_fin as periodofin,
                        SEMANA as semana,
                        parcialidad,
                        monto_valor,
                        cuota,
                        condonado,
                        fecha_condonacion,
                        CASE 
                            WHEN condonado = 1 THEN 'CONDONADO'
                            ELSE 'PENDIENTE'
                        END as status
                    FROM gastos_cobranza
                    WHERE Id_credito = %s
                    ORDER BY periodo_inicio ASC
                """
                
                cursor.execute(query_gastos, (id_credito,))
                gastos_rows = cursor.fetchall()
                
                # Procesar cada gasto
                detalles = []
                for row in gastos_rows:
                    detalle = {
                        "periodoinicio": row['periodoinicio'].strftime("%Y-%m-%d") if row['periodoinicio'] else None,
                        "periodofin": row['periodofin'].strftime("%Y-%m-%d") if row['periodofin'] else None,
                        "semana": row['semana'],
                        "parcialidad": row['parcialidad'],
                        "monto_valor": float(row['monto_valor']) if row['monto_valor'] else 0,
                        "cuota": float(row['cuota']) if row['cuota'] else 0,
                        "condonado": row['condonado'],
                        "fecha_condonacion": row['fecha_condonacion'].strftime("%Y-%m-%d %H:%M:%S") if row['fecha_condonacion'] else None,
                        "status": row['status']  # ← NUEVO CAMPO
                    }
                    detalles.append(detalle)
        
        # 3. Calcular resumen
        total_registros = len(detalles)
        condonados = sum(1 for d in detalles if d['condonado'] == 1)
        pendientes = total_registros - condonados
        
        # 4. Construir respuesta
        return {
            "status_code": 200,
            "status_message": "OK",
            "success": True,
            "mensaje": f"Se encontraron {total_registros} registros",
            "datos_generales": datos_generales,
            "resumen": {
                "total_registros": total_registros,
                "condonados": condonados,
                "pendientes": pendientes
            },
            "detalle": detalles
        }
        
    except HTTPException:
        raise
    except pymysql.Error as db_error:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(db_error)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
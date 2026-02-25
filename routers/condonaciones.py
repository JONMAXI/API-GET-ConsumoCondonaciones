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
    DetalleCondonacion,
    ResumenSimpleResponse
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
    try:
        validar_id_credito(id_credito)
        
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
                validar_datos_encontrados(datos_generales_row, 'cliente', id_credito)
                datos_generales = DatosGenerales(**datos_generales_row)
        
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
        
        mensaje = f"Se encontraron {len(detalles)} gastos condonados" if detalles else "No hay gastos condonados para este crédito"
        return CondonacionResponse(
            status_code=200,
            status_message="OK",
            success=True,
            mensaje=mensaje,
            datos_generales=datos_generales,
            condonacion_cobranza=condonacion_cobranza
        )
        
    except HTTPException:
        raise
    except pymysql.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


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
    try:
        validar_id_credito(id_credito)
        
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
                validar_datos_encontrados(datos_generales_row, 'cliente', id_credito)
                datos_generales = DatosGenerales(**datos_generales_row)
        
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
        
        return CondonacionResponse(
            status_code=200,
            status_message="OK",
            success=True,
            mensaje=f"Se encontraron {len(detalles)} gastos condonados",
            datos_generales=datos_generales,
            condonacion_cobranza=condonacion_cobranza
        )
        
    except HTTPException:
        raise
    except pymysql.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


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
    try:
        validar_id_credito(id_credito)
        
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
                validar_datos_encontrados(datos_generales_row, 'cliente', id_credito)
                datos_generales = DatosGenerales(**datos_generales_row)
        
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
        
        return CondonacionResponse(
            status_code=200,
            status_message="OK",
            success=True,
            mensaje=f"Se encontraron {len(detalles)} gastos pendientes de condonación",
            datos_generales=datos_generales,
            condonacion_cobranza=condonacion_cobranza
        )
        
    except HTTPException:
        raise
    except pymysql.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


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
    try:
        validar_id_credito(id_credito)
        
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
                validar_datos_encontrados(datos_generales_row, 'cliente', id_credito)
                datos_generales = {
                    "id_credito": datos_generales_row['id_credito'],
                    "nombre_cliente": datos_generales_row['nombre_cliente'],
                    "id_cliente": datos_generales_row['id_cliente'],
                    "domicilio_completo": datos_generales_row['domicilio_completo'],
                    "bucket_morosidad": datos_generales_row['bucket_morosidad'],
                    "dias_mora": datos_generales_row['dias_mora'],
                    "saldo_vencido": float(datos_generales_row['saldo_vencido']) if datos_generales_row['saldo_vencido'] else 0
                }
        
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
                
                detalles = []
                for row in gastos_rows:
                    detalles.append({
                        "periodoinicio": row['periodoinicio'].strftime("%Y-%m-%d") if row['periodoinicio'] else None,
                        "periodofin": row['periodofin'].strftime("%Y-%m-%d") if row['periodofin'] else None,
                        "semana": row['semana'],
                        "parcialidad": row['parcialidad'],
                        "monto_valor": float(row['monto_valor']) if row['monto_valor'] else 0,
                        "cuota": float(row['cuota']) if row['cuota'] else 0,
                        "condonado": row['condonado'],
                        "fecha_condonacion": row['fecha_condonacion'].strftime("%Y-%m-%d %H:%M:%S") if row['fecha_condonacion'] else None,
                        "status": row['status']
                    })
        
        total_registros = len(detalles)
        condonados = sum(1 for d in detalles if d['condonado'] == 1)
        pendientes = total_registros - condonados
        
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
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get(
    "/condonaciones/{id_credito}/resumen-simple",
    response_model=ResumenSimpleResponse,
    responses={
        200: {"description": "Éxito - Datos obtenidos correctamente"},
        400: {"description": "Bad Request - ID inválido o mal formado"},
        401: {"description": "No Autenticado - API Key inválida o faltante"},
        404: {"description": "No Encontrado - Crédito no existe"},
        500: {"description": "Error del Servidor - Error interno"}
    },
    summary="Resumen simple de gastos de cobranza",
    description=(
        "Retorna un resumen con totales calculados: total de parcialidades, "
        "monto total a condonar (suma de monto_valor), condonados y pendientes. Sin detalle de registros."
    )
)
async def get_resumen_simple(
    id_credito: int = Path(..., description="ID del crédito a consultar", gt=0),
    api_key: str = Security(verify_api_key)
):
    """
    Resumen simple de gastos de cobranza — totales calculados, sin lista de registros.

    - **id_credito**: ID del crédito a consultar

    Retorna:
    - **total_parcialidades**: Conteo total de registros
    - **monto_total**: Suma de monto_valor de todos los registros
    - **condonados**: Cantidad con condonado = 1
    - **pendientes**: Cantidad con condonado = 0 o NULL
    """

    try:
        validar_id_credito(id_credito)

        with get_db_connection(database="db-mega-reporte") as conn:
            with conn.cursor() as cursor:

                # Verificar que el crédito existe
                cursor.execute(
                    "SELECT Id_credito FROM tbl_segundometro_semana WHERE Id_credito = %s LIMIT 1",
                    (id_credito,)
                )
                validar_datos_encontrados(cursor.fetchone(), 'cliente', id_credito)

                # Obtener totales directamente desde SQL
                query_resumen = """
                    SELECT
                        COUNT(*)                                    AS total_parcialidades,
                        COALESCE(SUM(monto_valor), 0)               AS monto_total,
                        SUM(CASE WHEN condonado = 1 THEN 1 ELSE 0 END) AS condonados,
                        SUM(CASE WHEN condonado != 1 OR condonado IS NULL THEN 1 ELSE 0 END) AS pendientes
                    FROM gastos_cobranza
                    WHERE Id_credito = %s
                """
                cursor.execute(query_resumen, (id_credito,))
                row = cursor.fetchone()

        return ResumenSimpleResponse(
            status_code=200,
            status_message="OK",
            id_credito=id_credito,
            total_parcialidades=row["total_parcialidades"],
            monto_total=float(row["monto_total"]),
            condonados=row["condonados"],
            pendientes=row["pendientes"]
        )

    except HTTPException:
        raise
    except pymysql.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
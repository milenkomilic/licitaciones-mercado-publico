from django.core.management.base import BaseCommand
import os
import django
import requests
import time
import logging
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
import pytz  # Para manejar zonas horarias
from appone.models import LicitacionDiaria, ItemLicitacionDiaria

# Configurar el entorno de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "licitaciones_mercado_publico.settings")
django.setup()

# Configuración inicial
base_url = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
from django.conf import settings
ticket = settings.MERCADO_PUBLICO_TICKET
max_retries = 100
retry_wait_time = 0.3
estados_permitidos = [5,6,7,8,18,19]

# Calcular la fecha del día anterior
# fecha = (datetime.now() - timedelta(days=1)).strftime('%d%m%Y')
# logging.info(f"Fecha para consulta: {fecha}")

# Calcular la fecha de un día específico
fecha = "18022025"

# Configurar logging para mostrar en la terminal
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Asegurarse de que el logging se muestre en la terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Agregar el manejador a la configuración de logging
logging.getLogger().handlers = [console_handler]

# Zona horaria predeterminada
timezone = pytz.timezone("America/Santiago")  # Cambia según tu región

def convertir_fecha(fecha_naive):
    """Convierte una fecha naive a una fecha con zona horaria."""
    if fecha_naive:
        try:
            fecha_datetime = datetime.strptime(fecha_naive, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            try:
                fecha_datetime = datetime.strptime(fecha_naive, "%Y-%m-%dT%H:%M:%S")
            except ValueError as e:
                logging.warning(f"No se pudo convertir la fecha '{fecha_naive}': {e}")
                return None
        return make_aware(fecha_datetime, timezone)
    return None

class Command(BaseCommand):
    help = "Actualiza las licitaciones desde la API de Mercado Público"

    def handle(self, *args, **kwargs):
        try:
            # Inicia el temporizador
            start_time = time.time()
            logging.info("Iniciando la actualización de licitaciones...")
            
            # Paso 1: Obtener todas las licitaciones
            licitaciones = self.obtener_licitaciones()
            
            if licitaciones:
                for index, licitacion in enumerate(licitaciones, start=1):
                    codigo_externo = licitacion.get("CodigoExterno")
                    logging.info(f"Procesando licitación {index}/{len(licitaciones)}: {codigo_externo}")
                    
                    detalle = self.obtener_detalle_licitacion(codigo_externo)
                    self.guardar_licitacion(codigo_externo, detalle)
                logging.info("Actualización de licitaciones completada exitosamente.")
                self.stdout.write(self.style.SUCCESS("Actualización completada con éxito."))
            else:
                logging.warning("No se encontraron licitaciones para procesar.")
                self.stdout.write(self.style.WARNING("No se encontraron licitaciones para procesar."))

            # Detenemos el temporizador
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Convertir a horas, minutos y segundos
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Log y mensaje en consola
            logging.info(f"El script tardó {int(hours)}h {int(minutes)}m {seconds:.2f}s en ejecutarse.")
            self.stdout.write(self.style.SUCCESS(f"Tiempo total de ejecución: {int(hours)}h {int(minutes)}m {seconds:.2f}s."))

        except Exception as e:
            logging.error(f"Se produjo un error al ejecutar la actualización: {e}")
            self.stdout.write(self.style.ERROR(f"Error al ejecutar la actualización: {e}"))

    def obtener_licitaciones(self):
        logging.info("Obteniendo listado de licitaciones...")
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{base_url}?fecha={fecha}&ticket={ticket}")
                if response.status_code == 200:
                    listado = response.json().get("Listado", [])
                    
                    # Filtrar por estados permitidos
                    listado_filtrado = [
                        licitacion for licitacion in listado
                        if licitacion.get("CodigoEstado") in estados_permitidos
                    ]

                    logging.info(f"Se encontraron {len(listado_filtrado)} licitaciones con estados permitidos.")
                    return listado_filtrado
                else:
                    logging.warning(f"Error en listado de licitaciones: {response.status_code}")
            except Exception as e:
                logging.error(f"Excepción obteniendo listado: {e}")
            time.sleep(retry_wait_time)
        logging.error("No se pudo obtener el listado de licitaciones después de varios intentos.")
        return []

    def obtener_detalle_licitacion(self, codigo_externo):
        logging.info(f"Obteniendo detalle para licitación: {codigo_externo}")
        for attempt in range(max_retries):
            try:
                detalle_response = requests.get(f"{base_url}?codigo={codigo_externo}&ticket={ticket}")
                if detalle_response.status_code == 200:
                    detalle_data = detalle_response.json()
                    if "Listado" in detalle_data and detalle_data["Listado"]:
                        logging.debug(f"Detalle obtenido correctamente para {codigo_externo}.")
                        return detalle_data["Listado"][0]
                    else:
                        logging.warning(f"Detalle vacío o incompleto para {codigo_externo}")
                        return None
                else:
                    logging.warning(f"Error detalle para {codigo_externo}: {detalle_response.status_code}")
            except requests.RequestException as e:
                logging.error(f"Excepción procesando detalle para {codigo_externo}: {e}")
            time.sleep(retry_wait_time)
        logging.error(f"No se pudo obtener detalle para: {codigo_externo} después de {max_retries} intentos.")
        return None

    def guardar_licitacion(self, codigo_externo, detalle):
        if not detalle:
            logging.error(f"No se pudo guardar la licitación {codigo_externo}: detalle vacío o nulo.")
            return

        try:
            logging.info(f"Guardando licitación: {codigo_externo}")
            
            # Validar datos requeridos y opcionales
            comprador = detalle.get("Comprador", {})
            fechas = detalle.get("Fechas", {})
            adjudicacion = detalle.get("Adjudicacion") or {}
            items = detalle.get("Items") or {}
            listado_items = items.get("Listado", []) or []

            # Guardar la licitación principal
            licitacion, created = LicitacionDiaria.objects.update_or_create(
                codigo_externo=codigo_externo,
                defaults={
                    # Datos principales
                    "nombre": detalle.get("Nombre", None),
                    "descripcion": detalle.get("Descripcion", None),
                    "codigo_estado": detalle.get("CodigoEstado", None),
                    "fecha_cierre": convertir_fecha(detalle.get("FechaCierre")),
                    "estado": detalle.get("Estado", None),
                    
                    # Información del comprador
                    "codigo_organismo": comprador.get("CodigoOrganismo", None),
                    "nombre_organismo": comprador.get("NombreOrganismo", None),
                    "rut_unidad": comprador.get("RutUnidad", None),
                    "codigo_unidad": comprador.get("CodigoUnidad", None),
                    "nombre_unidad": comprador.get("NombreUnidad", None),
                    "direccion_unidad": comprador.get("DireccionUnidad", None),
                    "comuna_unidad": comprador.get("ComunaUnidad", None),
                    "region_unidad": comprador.get("RegionUnidad", None),
                    "rut_usuario": comprador.get("RutUsuario", None),
                    "codigo_usuario": comprador.get("CodigoUsuario", None),
                    "nombre_usuario": comprador.get("NombreUsuario", None),
                    "cargo_usuario": comprador.get("CargoUsuario", None),

                    # Datos principales 2
                    "dias_cierre_licitacion": detalle.get("DiasCierreLicitacion", None),
                    "informada": detalle.get("Informada", None),
                    "codigo_tipo": detalle.get("CodigoTipo", None),
                    "tipo": detalle.get("Tipo", None),
                    "tipo_convocatoria": detalle.get("TipoConvocatoria", None),
                    "moneda": detalle.get("Moneda", None),
                    "etapas": detalle.get("Etapas", None),
                    "estado_etapas": detalle.get("EstadoEtapas", None),
                    "toma_razon": detalle.get("TomaRazon", None),
                    "estado_publicidad_ofertas": detalle.get("EstadoPublicidadOfertas", None),
                    "justificacion_publicidad": detalle.get("JustificacionPublicidad", None),
                    "contrato": detalle.get("Contrato", None),
                    "obras": detalle.get("Obras", None),
                    "cantidad_reclamos": detalle.get("CantidadReclamos", None),

                    # Fechas
                    "fecha_creacion": convertir_fecha(fechas.get("FechaCreacion")),
                    "fecha_inicio": convertir_fecha(fechas.get("FechaInicio")),
                    "fecha_final": convertir_fecha(fechas.get("FechaFinal")),
                    "fecha_pub_respuestas": convertir_fecha(fechas.get("FechaPubRespuestas")),
                    "fecha_acto_apertura_tecnica": convertir_fecha(fechas.get("FechaActoAperturaTecnica")),
                    "fecha_acto_apertura_economica": convertir_fecha(fechas.get("FechaActoAperturaEconomica")),
                    "fecha_publicacion": convertir_fecha(fechas.get("FechaPublicacion")),
                    "fecha_adjudicacion": convertir_fecha(fechas.get("FechaAdjudicacion")),
                    "fecha_estimada_adjudicacion": convertir_fecha(fechas.get("FechaEstimadaAdjudicacion")),
                    "fecha_visita_terreno": convertir_fecha(fechas.get("FechaVisitaTerreno")),
                    "fecha_entrega_antecedentes": convertir_fecha(fechas.get("FechaEntregaAntecedentes")),

                    # Datos principales 3
                    "unidad_tiempo_evaluacion": detalle.get("UnidadTiempoEvaluacion", None),
                    "direccion_visita": detalle.get("DireccionVisita", None),
                    "direccion_entrega": detalle.get("DireccionEntrega", None),
                    "estimacion": detalle.get("Estimacion", None),
                    "fuente_financiamiento": detalle.get("FuenteFinanciamiento", None),
                    "visibilidad_monto": detalle.get("VisibilidadMonto", None),
                    "monto_estimado": detalle.get("MontoEstimado", None),
                    "tiempo": detalle.get("Tiempo", None),
                    "unidad_tiempo": detalle.get("UnidadTiempo", None),
                    "modalidad": detalle.get("Modalidad", None),
                    "tipo_pago": detalle.get("TipoPago", None),
                    "subcontratacion": detalle.get("SubContratacion", None),
                    "unidad_tiempo_duracion_contrato": detalle.get("UnidadTiempoDuracionContrato", None),
                    "tiempo_duracion_contrato": detalle.get("TiempoDuracionContrato", None),
                    "tipo_duracion_contrato": detalle.get("TipoDuracionContrato", None),
                    "justificacion_monto_estimado": detalle.get("JustificacionMontoEstimado", None),
                    "observacion_contract": detalle.get("ObservacionContract", None),
                    "extension_plazo": detalle.get("ExtensionPlazo", None),
                    "es_base_tipo": detalle.get("EsBaseTipo", None),
                    "unidad_tiempo_contrato_licitacion": detalle.get("UnidadTiempoContratoLicitacion", None),
                    "valor_tiempo_renovacion": detalle.get("ValorTiempoRenovacion", None),
                    "periodo_tiempo_renovacion": detalle.get("PeriodoTiempoRenovacion", None),
                    "es_renovable": detalle.get("EsRenovable", None),

                    # Adjudicacion
                    "adjudicacion_tipo": adjudicacion.get("Tipo", None),
                    "adjudicacion_fecha": convertir_fecha(adjudicacion.get("Fecha")),
                    "adjudicacion_numero": adjudicacion.get("Numero", None),
                    "adjudicacion_numero_oferentes": adjudicacion.get("NumeroOferentes", None),
                    "adjudicacion_url_acta": adjudicacion.get("UrlActa", None),
                }
            )

            # Procesar y guardar los ítems asociados a la licitación
            for item_data in listado_items:
                adjudicacion_data = item_data.get("Adjudicacion", {}) or {}
                correlativo = item_data.get("Correlativo")
                if correlativo is None:
                    logging.warning(f"Ítem sin correlativo en la licitación {codigo_externo}, se omitirá: {item_data}")
                    continue

                # Crear o actualizar el ítem
                ItemLicitacionDiaria.objects.update_or_create(
                    licitacion=licitacion,
                    correlativo=correlativo,
                    defaults={
                        "codigo_externo": codigo_externo,
                        "codigo_producto": item_data.get("CodigoProducto", None),
                        "codigo_categoria": item_data.get("CodigoCategoria", None),
                        "categoria": item_data.get("Categoria", None),
                        "nombre_producto": item_data.get("NombreProducto", None),
                        "descripcion": item_data.get("Descripcion", None),
                        "unidad_medida": item_data.get("UnidadMedida", None),
                        "cantidad": item_data.get("Cantidad", None),
                        "adjudicacion_rut_proveedor": adjudicacion_data.get("RutProveedor", None),
                        "adjudicacion_nombre_proveedor": adjudicacion_data.get("NombreProveedor", None),
                        "adjudicacion_cantidad": adjudicacion_data.get("Cantidad", None),
                        "adjudicacion_monto_unitario": adjudicacion_data.get("MontoUnitario", None),
                    }
                )

            logging.info(f"Licitación {codigo_externo} guardada exitosamente.")
        except Exception as e:
            logging.error(f"Error al guardar la licitación {codigo_externo}: {e}")
            logging.debug(f"Detalle de la licitación con error: {detalle}")

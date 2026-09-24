import datetime
from django.core.management.base import BaseCommand
from django.db import transaction

from appone.models import (
    LicitacionDiaria,
    ItemLicitacionDiaria,
    LicitacionArchivo,
    ItemLicitacionArchivo,
    UsuarioLicitacionPrioridad,
    UsuarioLicitacionPrioridadArchivado,
)

# Ejemplo de uso:
#   python manage.py archivar_licitaciones --fecha 2025-01-31  (para una fecha específica)
#   python manage.py archivar_licitaciones                     (usa el día de ayer por defecto)

class Command(BaseCommand):
    help = 'Archiva licitaciones, ítems y priorizaciones del día anterior (o de un día específico)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fecha',
            type=str,
            help="Fecha a archivar en formato AAAA-MM-DD. Si no se especifica, se usa el día de ayer.",
        )

    def handle(self, *args, **options):
        # Determinar la fecha a archivar (por defecto, día anterior)
        if options.get('fecha'):
            try:
                fecha_objetivo = datetime.datetime.strptime(options['fecha'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR("Formato de fecha incorrecto. Usa AAAA-MM-DD."))
                return
        else:
            fecha_objetivo = datetime.date.today() - datetime.timedelta(days=1)

        self.stdout.write(f"Archivando datos de la fecha: {fecha_objetivo}")

        # 1. Archivar licitaciones diarias
        licitaciones_diarias = LicitacionDiaria.objects.all()  # Puedes filtrar por fecha si lo requieres

        if not licitaciones_diarias.exists():
            self.stdout.write("No hay licitaciones diarias para archivar.")
            return

        archivados_map = {}  # key: id de LicitacionDiaria, value: LicitacionArchivo instance

        try:
            with transaction.atomic():
                # Archivar licitaciones diarias
                for lic in licitaciones_diarias:
                    lic_archivada, created = LicitacionArchivo.objects.update_or_create(
                        codigo_externo=lic.codigo_externo,
                        defaults={
                            'nombre': lic.nombre,
                            'descripcion': lic.descripcion,
                            'codigo_estado': lic.codigo_estado,
                            'fecha_cierre': lic.fecha_cierre,
                            'estado': lic.estado,
                            'codigo_organismo': lic.codigo_organismo,
                            'nombre_organismo': lic.nombre_organismo,
                            'rut_unidad': lic.rut_unidad,
                            'codigo_unidad': lic.codigo_unidad,
                            'nombre_unidad': lic.nombre_unidad,
                            'direccion_unidad': lic.direccion_unidad,
                            'comuna_unidad': lic.comuna_unidad,
                            'region_unidad': lic.region_unidad,
                            'rut_usuario': lic.rut_usuario,
                            'codigo_usuario': lic.codigo_usuario,
                            'nombre_usuario': lic.nombre_usuario,
                            'cargo_usuario': lic.cargo_usuario,
                            'fecha_creacion': lic.fecha_creacion,
                            'fecha_inicio': lic.fecha_inicio,
                            'fecha_final': lic.fecha_final,
                            'fecha_pub_respuestas': lic.fecha_pub_respuestas,
                            'fecha_acto_apertura_tecnica': lic.fecha_acto_apertura_tecnica,
                            'fecha_acto_apertura_economica': lic.fecha_acto_apertura_economica,
                            'fecha_publicacion': lic.fecha_publicacion,
                            'fecha_adjudicacion': lic.fecha_adjudicacion,
                            'fecha_estimada_adjudicacion': lic.fecha_estimada_adjudicacion,
                            'fecha_soporte_fisico': lic.fecha_soporte_fisico,
                            'fecha_tiempo_evaluacion': lic.fecha_tiempo_evaluacion,
                            'fecha_estimada_firma': lic.fecha_estimada_firma,
                            'fechas_usuario': lic.fechas_usuario,
                            'fecha_visita_terreno': lic.fecha_visita_terreno,
                            'fecha_entrega_antecedentes': lic.fecha_entrega_antecedentes,
                            'dias_cierre_licitacion': lic.dias_cierre_licitacion,
                            'informada': lic.informada,
                            'codigo_tipo': lic.codigo_tipo,
                            'tipo': lic.tipo,
                            'tipo_convocatoria': lic.tipo_convocatoria,
                            'moneda': lic.moneda,
                            'etapas': lic.etapas,
                            'estado_etapas': lic.estado_etapas,
                            'toma_razon': lic.toma_razon,
                            'estado_publicidad_ofertas': lic.estado_publicidad_ofertas,
                            'justificacion_publicidad': lic.justificacion_publicidad,
                            'contrato': lic.contrato,
                            'obras': lic.obras,
                            'cantidad_reclamos': lic.cantidad_reclamos,
                            'unidad_tiempo_evaluacion': lic.unidad_tiempo_evaluacion,
                            'direccion_visita': lic.direccion_visita,
                            'direccion_entrega': lic.direccion_entrega,
                            'estimacion': lic.estimacion,
                            'fuente_financiamiento': lic.fuente_financiamiento,
                            'visibilidad_monto': lic.visibilidad_monto,
                            'monto_estimado': lic.monto_estimado,
                            'tiempo': lic.tiempo,
                            'unidad_tiempo': lic.unidad_tiempo,
                            'modalidad': lic.modalidad,
                            'tipo_pago': lic.tipo_pago,
                            'subcontratacion': lic.subcontratacion,
                            'unidad_tiempo_duracion_contrato': lic.unidad_tiempo_duracion_contrato,
                            'tiempo_duracion_contrato': lic.tiempo_duracion_contrato,
                            'tipo_duracion_contrato': lic.tipo_duracion_contrato,
                            'justificacion_monto_estimado': lic.justificacion_monto_estimado,
                            'observacion_contract': lic.observacion_contract,
                            'extension_plazo': lic.extension_plazo,
                            'es_base_tipo': lic.es_base_tipo,
                            'unidad_tiempo_contrato_licitacion': lic.unidad_tiempo_contrato_licitacion,
                            'valor_tiempo_renovacion': lic.valor_tiempo_renovacion,
                            'periodo_tiempo_renovacion': lic.periodo_tiempo_renovacion,
                            'es_renovable': lic.es_renovable,
                            'adjudicacion_tipo': lic.adjudicacion_tipo,
                            'adjudicacion_fecha': lic.adjudicacion_fecha,
                            'adjudicacion_numero': lic.adjudicacion_numero,
                            'adjudicacion_numero_oferentes': lic.adjudicacion_numero_oferentes,
                            'adjudicacion_url_acta': lic.adjudicacion_url_acta,
                            'fecha_archivado': fecha_objetivo,
                        }
                    )
                    archivados_map[lic.id] = lic_archivada

                self.stdout.write(self.style.SUCCESS(f"Archivadas {len(archivados_map)} licitaciones."))

                # 2. Archivar ítems asociados
                items_diarios = ItemLicitacionDiaria.objects.filter(licitacion__in=licitaciones_diarias)
                items_archivar = []
                for item in items_diarios:
                    lic_archivada = archivados_map.get(item.licitacion.id)
                    if lic_archivada:
                        item_archivado = ItemLicitacionArchivo(
                            licitacion=lic_archivada,
                            codigo_externo=item.codigo_externo,
                            correlativo=item.correlativo,
                            codigo_producto=item.codigo_producto,
                            codigo_categoria=item.codigo_categoria,
                            categoria=item.categoria,
                            nombre_producto=item.nombre_producto,
                            descripcion=item.descripcion,
                            unidad_medida=item.unidad_medida,
                            cantidad=item.cantidad,
                            adjudicacion_rut_proveedor=item.adjudicacion_rut_proveedor,
                            adjudicacion_nombre_proveedor=item.adjudicacion_nombre_proveedor,
                            adjudicacion_cantidad=item.adjudicacion_cantidad,
                            adjudicacion_monto_unitario=item.adjudicacion_monto_unitario,
                            fecha_archivado=fecha_objetivo,
                        )
                        items_archivar.append(item_archivado)
                ItemLicitacionArchivo.objects.bulk_create(items_archivar)
                self.stdout.write(self.style.SUCCESS(f"Archivados {len(items_archivar)} ítems."))

                # 3. Archivar priorizaciones (nuevos datos)
                priorizaciones_diarias = UsuarioLicitacionPrioridad.objects.all()
                priorizaciones_archivar = []
                for prior in priorizaciones_diarias:
                    prior_archivada = UsuarioLicitacionPrioridadArchivado(
                        usuario=prior.usuario,
                        codigo_licitacion=prior.codigo_licitacion,
                        prioridad=prior.prioridad,
                        run_id=prior.run_id,
                        tiempo_ejecucion=prior.tiempo_ejecucion,
                        perfil_utilizado=prior.perfil_utilizado,
                        estado_proceso=prior.estado_proceso,
                        # Asignamos la fecha de archivado
                        fecha_archivado=fecha_objetivo,
                    )
                    priorizaciones_archivar.append(prior_archivada)
                UsuarioLicitacionPrioridadArchivado.objects.bulk_create(priorizaciones_archivar)
                self.stdout.write(self.style.SUCCESS(f"Archivadas {len(priorizaciones_archivar)} priorizaciones."))

                # 4. Una vez archivados todos los datos, eliminar los registros diarios:
                items_diarios.delete()
                licitaciones_diarias.delete()
                priorizaciones_diarias.delete()

                self.stdout.write(self.style.SUCCESS("Eliminados los registros diarios archivados."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocurrió un error durante el archivado: {e}"))

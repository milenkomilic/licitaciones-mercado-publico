import os
import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime
import shutil  # Para mover archivos

from appone.models import UsuarioLicitacionPrioridad

User = get_user_model()

class Command(BaseCommand):
    help = 'Puebla la tabla UsuarioLicitacionPrioridad a partir del JSON de consulta_priorizacion_resultados. Después mueve los archivos a una carpeta de respaldos.'

    def add_arguments(self, parser):
        default_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'consulta_priorizacion_resultados.json'
        )
        parser.add_argument(
            '--json_file',
            type=str,
            default=default_path,
            help='Ruta al archivo JSON con los resultados de la consulta de priorización.'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        self.stdout.write(f"Usando archivo JSON: {json_file}")

        # 1) Leer el archivo JSON y procesar la creación/actualización de registros en UsuarioLicitacionPrioridad
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al leer el archivo JSON: {e}"))
            return

        total_registros = 0

        for user_id_str, licitaciones in data.items():
            try:
                usuario = User.objects.get(id_usuario=int(user_id_str))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Usuario con ID {user_id_str} no existe. Se omitirá."))
                continue

            for codigo_licitacion, prioridad in licitaciones.items():
                obj, created = UsuarioLicitacionPrioridad.objects.update_or_create(
                    usuario=usuario,
                    codigo_licitacion=codigo_licitacion,
                    defaults={'prioridad': prioridad}
                )
                total_registros += 1
                if created:
                    self.stdout.write(f"Creado: {usuario} - {codigo_licitacion} : {prioridad}")
                else:
                    self.stdout.write(f"Actualizado: {usuario} - {codigo_licitacion} : {prioridad}")

        self.stdout.write(self.style.SUCCESS(f"Se han procesado {total_registros} registros de UsuarioLicitacionPrioridad."))

        # 2) Mover los 3 archivos solicitados a la carpeta de respaldo con la fecha actual
        # Formato de fecha DDMMYYYY
        date_str = datetime.now().strftime("%d%m%Y")
        backup_folder = os.path.join(os.path.dirname(__file__), 'data', 'respaldo', date_str)

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        files_to_move = [
            'consulta_priorizacion_resultados.json',
            'keywords_licitaciones.json',
            'profiles_clientes_usuario.json'
        ]

        for file_name in files_to_move:
            src_path = os.path.join(os.path.dirname(__file__), 'data', file_name)
            dst_path = os.path.join(backup_folder, file_name)
            try:
                shutil.move(src_path, dst_path)
                self.stdout.write(self.style.SUCCESS(f"Archivo movido a respaldo: {file_name}"))
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"No se encontró {file_name} en data/. Se omitirá."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al mover {file_name}: {e}"))

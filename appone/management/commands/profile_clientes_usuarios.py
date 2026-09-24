import json
import os
from django.core.management.base import BaseCommand
from appone.models import Usuario, Cliente, Sector, PalabrasClave, PalabrasClaveUsuario

def get_initials(nombre):
    """
    Retorna las iniciales de un nombre. Ejemplo: "Juan Rodriguez" -> "JR"
    """
    palabras = nombre.split()
    return ''.join([p[0].upper() for p in palabras if p])

def obtener_keywords(admin):
    """Devuelve una lista de palabras clave asociadas al admin."""
    return list(PalabrasClave.objects.filter(admin=admin).values_list('keywords', flat=True))

def obtener_keywords_usuario(usuario):
    """Devuelve las palabras clave personalizadas del usuario."""
    return PalabrasClaveUsuario.objects.filter(usuario=usuario).values_list('keywords_usuario', flat=True)

class Command(BaseCommand):
    help = (
        "Genera un perfil compacto de clientes para cada usuario, "
        "basado en los clientes asignados, usando iniciales en lugar del nombre completo, "
        "incluyendo el rol del usuario y las keywords asignadas por su admin y el usuario, "
        "usando sectores desde la base de datos."
    )

    def add_arguments(self, parser):
        # Definir la ruta predeterminada dentro de commands/data
        default_path = os.path.join(os.path.dirname(__file__), 'data', 'profiles_clientes_usuario.json')

        parser.add_argument(
            '--salida',
            type=str,
            default=default_path,
            help=f'Ruta del archivo de salida (formato JSON newline delimited). '
                 f'Si no se especifica, se usará la ruta por defecto: {default_path}'
        )

    def handle(self, *args, **options):
        salida = options['salida']
        
        # Se cargan los sectores desde la base de datos.
        sectores = Sector.objects.all()
        SECTOR_ID_MAP = {sector.codigo.lower().strip(): sector.id for sector in sectores}

        # Se recorren todos los usuarios
        usuarios = Usuario.objects.all()
        perfiles = {}
        
        for usuario in usuarios:
            clientes = Cliente.objects.filter(asignado_a=usuario, estado='activo')
            if not clientes.exists():
                continue

            perfil_usuario = {}
            for cliente in clientes:
                sector_code = cliente.sector.codigo.lower().strip() if cliente.sector else 'otro'
                if sector_code not in SECTOR_ID_MAP:
                    sector_code = 'otro'
                perfil_usuario[sector_code] = perfil_usuario.get(sector_code, 0) + 1

            perfil_reducido = {str(SECTOR_ID_MAP[k]): v for k, v in perfil_usuario.items() if k in SECTOR_ID_MAP}
            rol_usuario = usuario.rol.nombre_rol if usuario.rol else ''

            # Obtener las palabras clave del admin y del usuario
            keywords_admin = obtener_keywords(usuario.creado_por) if usuario.creado_por else []
            keywords_usuario = obtener_keywords_usuario(usuario)

            perfiles[str(usuario.id_usuario)] = {
                'n': get_initials(usuario.nombre),
                'p': perfil_reducido,
                'r': rol_usuario,
                'k_admin': keywords_admin,
                'k_usuario': list(keywords_usuario),
            }
        
        # Asegurarse de que el directorio de salida exista
        directorio = os.path.dirname(salida)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
        
        try:
            with open(salida, 'w', encoding='utf-8') as f:
                for user_id, data in perfiles.items():
                    linea = json.dumps({user_id: data}, ensure_ascii=False, separators=(',', ':'))
                    f.write(linea + "\n")
            self.stdout.write(self.style.SUCCESS(f"Perfiles compactos guardados en: {salida}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al escribir el archivo: {e}"))

import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from appone.models import Usuario, UsuarioLicitacionPrioridad, LicitacionDiaria
from django.db.models import Sum

class Command(BaseCommand):
    help = "Envía mensajes de WhatsApp a contactos con información de licitaciones usando la API de WhatsApp Business"

    def add_arguments(self, parser):
        parser.add_argument('--rut', type=str, help='RUT del usuario al que enviar el mensaje')

    def handle(self, *args, **options):
        # Configurar credenciales de WhatsApp Business API desde settings.py o variables de entorno
        ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN  # Asegúrate de definirlo en settings.py
        PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID  # Identificador del número de WhatsApp

        # Filtrar usuarios según el RUT (si se proporciona) o tomar todos
        if options['rut']:
            contacts = Usuario.objects.filter(rut=options['rut'])
            if not contacts.exists():
                self.stdout.write(self.style.ERROR(f'No se encontró un usuario con el RUT {options["rut"]}'))
                return
        else:
            contacts = Usuario.objects.all()

        self.stdout.write(f"Procesando {contacts.count()} contactos...")

        for contact in contacts:
            try:
                self.stdout.write(f"Procesando usuario: {contact.nombre} (ID: {contact.id_usuario})")

                # Obtener licitaciones asignadas
                licitaciones_asignadas = UsuarioLicitacionPrioridad.objects.filter(usuario_id=contact.id_usuario)
                num_licitaciones = licitaciones_asignadas.count()
                self.stdout.write(f"Número de licitaciones asignadas: {num_licitaciones}")

                # Obtener códigos de licitación
                codigos_licitacion = list(licitaciones_asignadas.values_list('codigo_licitacion', flat=True))
                self.stdout.write(f"Códigos de licitación: {codigos_licitacion}")

                # Calcular monto total
                total_monto = 0
                if num_licitaciones > 0:
                    licitaciones_diarias = LicitacionDiaria.objects.filter(codigo_externo__in=codigos_licitacion)
                    self.stdout.write(f"Licitaciones diarias encontradas: {licitaciones_diarias.count()}")
                    total_monto = licitaciones_diarias.aggregate(total=Sum('monto_estimado'))['total'] or 0
                    self.stdout.write(f"Monto total calculado: {total_monto}")

                # Formatear monto
                monto_formateado = self.format_monto(total_monto)

                # Arreglo de variables para que coincidan con la plantilla aprobada por META
                nombre = contact.nombre
                numero_licitaciones = str(num_licitaciones)
                monto_total = monto_formateado

                # Crear cuerpo del mensaje
                message_data = {
                    "messaging_product": "whatsapp",
                    "to": contact.phone_number,
                    "type": "template",
                    "template": {
                        "name": "informacion_de_licitaciones2",
                        "language": {"code": "es"},
                        "components": [
                            {
                                "type": "body",
                                "parameters": [
                                    {"type": "text", "parameter_name": "nombre", "text": nombre},
                                    {"type": "text", "parameter_name": "numero_licitaciones", "text": numero_licitaciones},
                                    {"type": "text", "parameter_name": "monto_total", "text": monto_total}
                                ]
                            }
                        ]
                    }
                }


                # Imprimir el JSON antes de enviarlo para verificarlo
                print(json.dumps(message_data, indent=4, ensure_ascii=False))

                # Enviar solicitud a la API de WhatsApp
                url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
                headers = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                }
                response = requests.post(url, json=message_data, headers=headers)

                # Verificar respuesta
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"Mensaje enviado a {contact.phone_number}: {response.json()}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Error al enviar mensaje a {contact.phone_number}: {response.text}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error en usuario {contact.phone_number}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Proceso de envío de mensajes completado.'))

    def format_monto(self, monto):
        """Formatea el monto como pesos chilenos con separadores de miles."""
        return f"${monto:,.0f}".replace(",", ".")

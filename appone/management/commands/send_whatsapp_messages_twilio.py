# appones/management/commands/send_whatsapp_messages.py
from django.core.management.base import BaseCommand
from twilio.rest import Client
from django.conf import settings
from appone.models import Usuario, UsuarioLicitacionPrioridad, LicitacionDiaria
from django.db.models import Sum
import os

class Command(BaseCommand):
    help = 'Envía mensajes de WhatsApp a contactos con información de licitaciones asignadas'

    def add_arguments(self, parser):
        parser.add_argument('--rut', type=str, help='RUT del usuario al que enviar el mensaje')

    def handle(self, *args, **options):
        # Configura el cliente de Twilio
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

        client = Client(account_sid, auth_token)

        # Filtra usuarios según el RUT (si se proporciona) o toma todos
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

                # Obtener las licitaciones asignadas al usuario
                licitaciones_asignadas = UsuarioLicitacionPrioridad.objects.filter(usuario_id=contact.id_usuario)
                num_licitaciones = licitaciones_asignadas.count()
                self.stdout.write(f"Número de licitaciones asignadas: {num_licitaciones}")

                # Definir codigos_licitacion antes de usarlo
                codigos_licitacion = list(licitaciones_asignadas.values_list('codigo_licitacion', flat=True))
                self.stdout.write(f"Códigos de licitación: {codigos_licitacion}")

                # Calcular el monto total de las licitaciones
                total_monto = 0
                if num_licitaciones > 0:
                    # Filtrar licitaciones diarias por codigo_externo
                    licitaciones_diarias = LicitacionDiaria.objects.filter(codigo_externo__in=codigos_licitacion)
                    self.stdout.write(f"Licitaciones diarias encontradas: {licitaciones_diarias.count()}")
                    total_monto = licitaciones_diarias.aggregate(total=Sum('monto_estimado'))['total'] or 0
                    self.stdout.write(f"Monto total calculado: {total_monto}")

                # Formatear el monto total
                monto_formateado = self.format_monto(total_monto)

                # Crear el mensaje personalizado
                message_body = (
                    f"Hola {contact.nombre}, tienes {num_licitaciones} licitaciones "
                    f"asignadas avaluadas en {monto_formateado}."
                )

                # Enviar el mensaje a través de Twilio WhatsApp
                message = client.messages.create(
                    from_=whatsapp_number,
                    body=message_body,
                    to=f'whatsapp:{contact.phone_number}'
                )

                self.stdout.write(
                    self.style.SUCCESS(f'Mensaje enviado exitosamente a {contact.phone_number}: {message.sid}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error al enviar mensaje a {contact.phone_number}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Proceso de envío de mensajes completado.'))

    def format_monto(self, monto):
        """Formatea el monto como pesos chilenos con separadores de miles."""
        return f"${monto:,.0f}".replace(",", ".")
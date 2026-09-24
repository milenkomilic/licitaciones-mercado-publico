from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, rut, nombre, email=None, password=None, **extra_fields):
        if not rut:
            raise ValueError('El usuario debe tener un RUT válido.')
        rut = rut.replace('.', '').replace('-', '').upper()
        usuario = self.model(rut=rut, nombre=nombre, email=self.normalize_email(email), **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, rut, nombre, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(rut, nombre, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    rol = models.ForeignKey('Rol', on_delete=models.SET_NULL, null=True, blank=True)
    cliente_id = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, help_text="Formato: +1234567890")
    creado_por = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='usuarios_creados'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions',
        blank=True,
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre



class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name="roles",
        null=True,
        blank=True
    )

    class Meta:
        unique_together = (("nombre_rol", "creado_por"),)



class PalabrasClave(models.Model):
    admin = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='palabras_clave'
    )
    keywords = models.CharField(
        max_length=255,
        help_text="Ingresa múltiples palabras clave separadas por comas. (Máx. 255 caracteres)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.keywords


class PalabrasClaveUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='palabras_clave_usuario'
    )
    keywords_usuario = models.CharField(
        max_length=100,
        help_text="Ingresa múltiples palabras clave separadas por comas. (Máx. 100 caracteres)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.keywords_usuario


class Sector(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Sector"
        verbose_name_plural = "Sectores"
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion


class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('individual', 'Individual'),
        ('empresa', 'Empresa'),
        ('institucion', 'Institución'),
    ]

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    nombre_cliente = models.CharField(max_length=255)
    rut_cliente = models.CharField(
        max_length=20,
        help_text="RUT del cliente (ejemplo: 12.345.678-9)"
    )
    tipo_cliente = models.CharField(max_length=20, choices=TIPO_CLIENTE_CHOICES)
    contacto_principal = models.CharField(
        max_length=255,
        help_text="Nombre y apellidos de la persona de contacto"
    )
    email = models.EmailField()
    # Ahora se usa una relación ForeignKey en lugar de un CharField con choices
    sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        help_text="Sector o industria"
    )
    descripcion_rubro = models.TextField(help_text="Descripción del rubro que ejerce")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_creados'
    )
    asignado_a = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='clientes_asignados'
    )

    class Meta:
        unique_together = ('rut_cliente', 'creado_por')

    def __str__(self):
        return self.nombre_cliente



class LicitacionArchivo(models.Model):
    # Datos principales de la licitación
    codigo_externo = models.CharField(max_length=255, unique=True)
    nombre = models.TextField()
    descripcion = models.TextField(blank=True, null=True)
    codigo_estado = models.CharField(max_length=10, blank=True, null=True)
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)

    # Información del comprador
    codigo_organismo = models.CharField(max_length=50, blank=True, null=True)
    nombre_organismo = models.TextField(blank=True, null=True)
    rut_unidad = models.CharField(max_length=20, blank=True, null=True)
    codigo_unidad = models.CharField(max_length=50, blank=True, null=True)
    nombre_unidad = models.TextField(blank=True, null=True)
    direccion_unidad = models.TextField(blank=True, null=True)
    comuna_unidad = models.TextField(blank=True, null=True)
    region_unidad = models.TextField(blank=True, null=True)
    rut_usuario = models.CharField(max_length=20, blank=True, null=True)
    codigo_usuario = models.CharField(max_length=50, blank=True, null=True)
    nombre_usuario = models.TextField(blank=True, null=True)
    cargo_usuario = models.TextField(blank=True, null=True)

    # Información de fechas
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_final = models.DateTimeField(blank=True, null=True)
    fecha_pub_respuestas = models.DateTimeField(blank=True, null=True)
    fecha_acto_apertura_tecnica = models.DateTimeField(blank=True, null=True)
    fecha_acto_apertura_economica = models.DateTimeField(blank=True, null=True)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    fecha_adjudicacion = models.DateTimeField(blank=True, null=True)
    fecha_estimada_adjudicacion = models.DateTimeField(blank=True, null=True)
    fecha_soporte_fisico = models.DateTimeField(blank=True, null=True)
    fecha_tiempo_evaluacion = models.DateTimeField(blank=True, null=True)
    fecha_estimada_firma = models.DateTimeField(blank=True, null=True)
    fechas_usuario = models.TextField(blank=True, null=True)
    fecha_visita_terreno = models.DateTimeField(blank=True, null=True)
    fecha_entrega_antecedentes = models.DateTimeField(blank=True, null=True)

    # Información adicional
    dias_cierre_licitacion = models.IntegerField(blank=True, null=True)
    informada = models.BooleanField(blank=True, null=True)
    codigo_tipo = models.CharField(max_length=50, blank=True, null=True)
    tipo = models.TextField(blank=True, null=True)
    tipo_convocatoria = models.TextField(blank=True, null=True)
    moneda = models.CharField(max_length=10, blank=True, null=True)
    etapas = models.TextField(blank=True, null=True)
    estado_etapas = models.TextField(blank=True, null=True)
    toma_razon = models.BooleanField(blank=True, null=True)
    estado_publicidad_ofertas = models.TextField(blank=True, null=True)
    justificacion_publicidad = models.TextField(blank=True, null=True)
    contrato = models.TextField(blank=True, null=True)
    obras = models.IntegerField(blank=True, null=True)
    cantidad_reclamos = models.IntegerField(blank=True, null=True)
    unidad_tiempo_evaluacion = models.TextField(blank=True, null=True)
    direccion_visita = models.TextField(blank=True, null=True)
    direccion_entrega = models.TextField(blank=True, null=True)
    estimacion = models.FloatField(blank=True, null=True)
    fuente_financiamiento = models.TextField(blank=True, null=True)
    visibilidad_monto = models.BooleanField(blank=True, null=True)
    monto_estimado = models.FloatField(blank=True, null=True)
    tiempo = models.IntegerField(blank=True, null=True)
    unidad_tiempo = models.TextField(blank=True, null=True)
    modalidad = models.TextField(blank=True, null=True)
    tipo_pago = models.TextField(blank=True, null=True)
    subcontratacion = models.TextField(blank=True, null=True)
    unidad_tiempo_duracion_contrato = models.TextField(blank=True, null=True)
    tiempo_duracion_contrato = models.IntegerField(blank=True, null=True)
    tipo_duracion_contrato = models.TextField(blank=True, null=True)
    justificacion_monto_estimado = models.TextField(blank=True, null=True)
    observacion_contract = models.TextField(blank=True, null=True)
    extension_plazo = models.BooleanField(blank=True, null=True)
    es_base_tipo = models.BooleanField(blank=True, null=True)
    unidad_tiempo_contrato_licitacion = models.TextField(blank=True, null=True)
    valor_tiempo_renovacion = models.FloatField(blank=True, null=True)
    periodo_tiempo_renovacion = models.TextField(blank=True, null=True)
    es_renovable = models.BooleanField(blank=True, null=True)

    # Información de adjudicación
    adjudicacion_tipo = models.TextField(blank=True, null=True)
    adjudicacion_fecha = models.DateTimeField(blank=True, null=True)
    adjudicacion_numero = models.CharField(max_length=50, blank=True, null=True)
    adjudicacion_numero_oferentes = models.IntegerField(blank=True, null=True)
    adjudicacion_url_acta = models.TextField(blank=True, null=True)

    # Fecha de archivado
    fecha_archivado = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class ItemLicitacionArchivo(models.Model):
    # Relación con Licitación
    licitacion = models.ForeignKey(LicitacionArchivo, on_delete=models.CASCADE, related_name="items")

    # Codigo Externo
    codigo_externo = models.CharField(max_length=255, null=True)

    # Datos del ítem
    correlativo = models.IntegerField()
    codigo_producto = models.CharField(max_length=50, blank=True, null=True)
    codigo_categoria = models.CharField(max_length=50, blank=True, null=True)
    categoria = models.TextField(blank=True, null=True)
    nombre_producto = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.TextField(blank=True, null=True)
    cantidad = models.FloatField(blank=True, null=True)

    # Información de adjudicación del ítem
    adjudicacion_rut_proveedor = models.CharField(max_length=20, blank=True, null=True)
    adjudicacion_nombre_proveedor = models.TextField(blank=True, null=True)
    adjudicacion_cantidad = models.IntegerField(blank=True, null=True)
    adjudicacion_monto_unitario = models.FloatField(blank=True, null=True)

    # Fecha de archivado
    fecha_archivado = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Ítem {self.correlativo} - {self.nombre_producto}"


class LicitacionDiaria(models.Model):
    # Datos principales de la licitación
    codigo_externo = models.CharField(max_length=255, unique=True)
    nombre = models.TextField()
    descripcion = models.TextField(blank=True, null=True)
    codigo_estado = models.CharField(max_length=10, blank=True, null=True)
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)

    # Información del comprador
    codigo_organismo = models.CharField(max_length=50, blank=True, null=True)
    nombre_organismo = models.TextField(blank=True, null=True)
    rut_unidad = models.CharField(max_length=20, blank=True, null=True)
    codigo_unidad = models.CharField(max_length=50, blank=True, null=True)
    nombre_unidad = models.TextField(blank=True, null=True)
    direccion_unidad = models.TextField(blank=True, null=True)
    comuna_unidad = models.TextField(blank=True, null=True)
    region_unidad = models.TextField(blank=True, null=True)
    rut_usuario = models.CharField(max_length=20, blank=True, null=True)
    codigo_usuario = models.CharField(max_length=50, blank=True, null=True)
    nombre_usuario = models.TextField(blank=True, null=True)
    cargo_usuario = models.TextField(blank=True, null=True)

    # Información de fechas
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_final = models.DateTimeField(blank=True, null=True)
    fecha_pub_respuestas = models.DateTimeField(blank=True, null=True)
    fecha_acto_apertura_tecnica = models.DateTimeField(blank=True, null=True)
    fecha_acto_apertura_economica = models.DateTimeField(blank=True, null=True)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    fecha_adjudicacion = models.DateTimeField(blank=True, null=True)
    fecha_estimada_adjudicacion = models.DateTimeField(blank=True, null=True)
    fecha_soporte_fisico = models.DateTimeField(blank=True, null=True)
    fecha_tiempo_evaluacion = models.DateTimeField(blank=True, null=True)
    fecha_estimada_firma = models.DateTimeField(blank=True, null=True)
    fechas_usuario = models.TextField(blank=True, null=True)
    fecha_visita_terreno = models.DateTimeField(blank=True, null=True)
    fecha_entrega_antecedentes = models.DateTimeField(blank=True, null=True)

    # Información adicional
    dias_cierre_licitacion = models.IntegerField(blank=True, null=True)
    informada = models.BooleanField(blank=True, null=True)
    codigo_tipo = models.CharField(max_length=50, blank=True, null=True)
    tipo = models.TextField(blank=True, null=True)
    tipo_convocatoria = models.TextField(blank=True, null=True)
    moneda = models.CharField(max_length=10, blank=True, null=True)
    etapas = models.TextField(blank=True, null=True)
    estado_etapas = models.TextField(blank=True, null=True)
    toma_razon = models.BooleanField(blank=True, null=True)
    estado_publicidad_ofertas = models.TextField(blank=True, null=True)
    justificacion_publicidad = models.TextField(blank=True, null=True)
    contrato = models.TextField(blank=True, null=True)
    obras = models.IntegerField(blank=True, null=True)
    cantidad_reclamos = models.IntegerField(blank=True, null=True)
    unidad_tiempo_evaluacion = models.TextField(blank=True, null=True)
    direccion_visita = models.TextField(blank=True, null=True)
    direccion_entrega = models.TextField(blank=True, null=True)
    estimacion = models.FloatField(blank=True, null=True)
    fuente_financiamiento = models.TextField(blank=True, null=True)
    visibilidad_monto = models.BooleanField(blank=True, null=True)
    monto_estimado = models.FloatField(blank=True, null=True)
    tiempo = models.IntegerField(blank=True, null=True)
    unidad_tiempo = models.TextField(blank=True, null=True)
    modalidad = models.TextField(blank=True, null=True)
    tipo_pago = models.TextField(blank=True, null=True)
    subcontratacion = models.TextField(blank=True, null=True)
    unidad_tiempo_duracion_contrato = models.TextField(blank=True, null=True)
    tiempo_duracion_contrato = models.IntegerField(blank=True, null=True)
    tipo_duracion_contrato = models.TextField(blank=True, null=True)
    justificacion_monto_estimado = models.TextField(blank=True, null=True)
    observacion_contract = models.TextField(blank=True, null=True)
    extension_plazo = models.BooleanField(blank=True, null=True)
    es_base_tipo = models.BooleanField(blank=True, null=True)
    unidad_tiempo_contrato_licitacion = models.TextField(blank=True, null=True)
    valor_tiempo_renovacion = models.FloatField(blank=True, null=True)
    periodo_tiempo_renovacion = models.TextField(blank=True, null=True)
    es_renovable = models.BooleanField(blank=True, null=True)

    # Información de adjudicación
    adjudicacion_tipo = models.TextField(blank=True, null=True)
    adjudicacion_fecha = models.DateTimeField(blank=True, null=True)
    adjudicacion_numero = models.CharField(max_length=50, blank=True, null=True)
    adjudicacion_numero_oferentes = models.IntegerField(blank=True, null=True)
    adjudicacion_url_acta = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class ItemLicitacionDiaria(models.Model):
    licitacion = models.ForeignKey(LicitacionDiaria, on_delete=models.CASCADE, related_name="items")

    # Codigo Externo
    codigo_externo = models.CharField(max_length=255, null=True)

    # Datos del ítem
    correlativo = models.IntegerField()
    codigo_producto = models.CharField(max_length=50, blank=True, null=True)
    codigo_categoria = models.CharField(max_length=50, blank=True, null=True)
    categoria = models.TextField(blank=True, null=True)
    nombre_producto = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.TextField(blank=True, null=True)
    cantidad = models.FloatField(blank=True, null=True)

    # Información de adjudicación del ítem
    adjudicacion_rut_proveedor = models.CharField(max_length=20, blank=True, null=True)
    adjudicacion_nombre_proveedor = models.TextField(blank=True, null=True)
    adjudicacion_cantidad = models.IntegerField(blank=True, null=True)
    adjudicacion_monto_unitario = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Ítem {self.correlativo} - {self.nombre_producto}"


class UsuarioLicitacionPrioridad(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='licitaciones_priorizadas'
    )
    codigo_licitacion = models.CharField(max_length=255)
    prioridad = models.BooleanField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    run_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Identificador del proceso de priorización"
    )
    tiempo_ejecucion = models.DurationField(
        blank=True,
        null=True,
        help_text="Tiempo de ejecución del proceso de priorización"
    )
    perfil_utilizado = models.JSONField(
        blank=True,
        null=True,
        help_text="Datos del perfil utilizados en la priorización (en formato JSON)"
    )
    estado_proceso = models.CharField(
        max_length=50,
        default="completado",
        help_text="Estado del proceso de priorización (por ejemplo, 'pendiente', 'completado', 'error')"
    )

    class Meta:
        unique_together = ('usuario', 'codigo_licitacion')
        verbose_name = "Prioridad de Licitación por Usuario"
        verbose_name_plural = "Prioridades de Licitaciones por Usuario"

    def __str__(self):
        return f"{self.usuario} - {self.codigo_licitacion} : {self.prioridad}"


class UsuarioLicitacionPrioridadArchivado(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='licitaciones_priorizadas_archivadas'
    )
    codigo_licitacion = models.CharField(max_length=255)
    prioridad = models.BooleanField()
    fecha_archivado = models.DateTimeField(auto_now_add=True)
    
    run_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Identificador del proceso de priorización"
    )
    tiempo_ejecucion = models.DurationField(
        blank=True,
        null=True,
        help_text="Tiempo de ejecución del proceso de priorización"
    )
    perfil_utilizado = models.JSONField(
        blank=True,
        null=True,
        help_text="Datos del perfil utilizados en la priorización (en formato JSON)"
    )
    estado_proceso = models.CharField(
        max_length=50,
        default="completado",
        help_text="Estado del proceso de priorización (por ejemplo, 'pendiente', 'completado', 'error')"
    )

    class Meta:
        unique_together = ('usuario', 'codigo_licitacion', 'fecha_archivado')
        verbose_name = "Prioridad Archivada de Licitación por Usuario"
        verbose_name_plural = "Prioridades Archivadas de Licitaciones por Usuario"

    def __str__(self):
        return f"{self.usuario} - {self.codigo_licitacion} archivado en {self.fecha_archivado} : {self.prioridad}"
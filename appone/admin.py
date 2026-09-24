from django.forms import ValidationError
from .models import Usuario, Rol, LicitacionArchivo, ItemLicitacionArchivo, LicitacionDiaria, ItemLicitacionDiaria
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

admin.site.register(Rol)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('rut', 'nombre', 'email', 'rol', 'is_staff', 'is_active')  # Muestra campos relevantes en el listado
    list_filter = ('is_staff', 'is_active', 'rol')  # Filtros para facilitar la búsqueda
    search_fields = ('rut', 'nombre', 'email')  # Búsqueda por RUT, nombre o email
    ordering = ('rut',)  # Orden por RUT

    # Estructura de los formularios de edición y creación
    fieldsets = (
        (None, {'fields': ('rut', 'password')}),  # Campos obligatorios
        ('Información personal', {'fields': ('nombre', 'email', 'rol', 'cliente_id')}),  # Información adicional
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),  # Permisos
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('rut', 'nombre', 'email', 'password1', 'password2', 'rol', 'is_staff', 'is_active')},
        ),
    )

    # Métodos adicionales
    def save_model(self, request, obj, form, change):
        """
        Validar que los roles no sean de nivel jerárquico 1 al ser asignados por el admin.
        """
        if obj.rol and obj.rol.nivel == 1 and not request.user.is_superuser:
            raise ValidationError("Solo los superusuarios pueden asignar roles estratégicos.")
        super().save_model(request, obj, form, change)

@admin.register(ItemLicitacionArchivo)
class ItemLicitacionAdmin(admin.ModelAdmin):
    # Campos visibles en la lista de ítems
    list_display = (
        'codigo_externo',
        'nombre_producto',
        'correlativo',
        'cantidad',
        'adjudicacion_nombre_proveedor',
        'adjudicacion_monto_unitario',
    )
    
    # Campos habilitados para búsqueda
    search_fields = (
        'licitacion__codigo_externo',
        'nombre_producto',
        'codigo_producto',
        'adjudicacion_nombre_proveedor',
    )
    
    # Filtros en la barra lateral
    list_filter = (
        'licitacion__estado',
    )

@admin.register(LicitacionArchivo)
class LicitacionAdmin(admin.ModelAdmin):
    # Campos visibles en la lista de licitaciones
    list_display = (
        'codigo_externo', 
        'nombre', 
        'estado', 
        'fecha_cierre', 
        'monto_estimado', 
        'adjudicacion_tipo',
    )
    
    # Campos habilitados para búsqueda
    search_fields = ('codigo_externo', 'nombre', 'nombre_organismo')
    
    # Filtros en la barra lateral
    list_filter = ('estado', 'moneda', 'tipo_convocatoria')


@admin.register(ItemLicitacionDiaria)
class ItemLicitacionDiariaAdmin(admin.ModelAdmin):
    # Campos visibles en la lista de ítems
    list_display = (
        'codigo_externo',
        'nombre_producto',
        'correlativo',
        'cantidad',
        'adjudicacion_nombre_proveedor',
        'adjudicacion_monto_unitario',
    )
    
    # Campos habilitados para búsqueda
    search_fields = (
        'licitacion__codigo_externo',
        'nombre_producto',
        'codigo_producto',
        'adjudicacion_nombre_proveedor',
    )
    
    # Filtros en la barra lateral
    list_filter = (
        'licitacion__estado',
    )

@admin.register(LicitacionDiaria)
class LicitacionDiariaAdmin(admin.ModelAdmin):
    # Campos visibles en la lista de licitaciones
    list_display = (
        'codigo_externo', 
        'nombre', 
        'estado', 
        'fecha_cierre', 
        'monto_estimado', 
        'adjudicacion_tipo',
    )
    
    # Campos habilitados para búsqueda
    search_fields = ('codigo_externo', 'nombre', 'nombre_organismo')
    
    # Filtros en la barra lateral
    list_filter = ('estado', 'moneda', 'tipo_convocatoria')

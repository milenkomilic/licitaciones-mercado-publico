import datetime
from itertools import count
import pandas as pd
import openpyxl
from io import BytesIO
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q
from appone.forms import UsuarioForm, RolForm, PalabrasClaveForm, PalabrasClaveUsuarioForm, ClienteForm, SectorForm, SubidaClientesForm
from appone.models import (
    Rol,
    Usuario,
    Cliente,
    Sector,
    LicitacionDiaria,
    UsuarioLicitacionPrioridad,
    UsuarioLicitacionPrioridadArchivado,
    LicitacionArchivo,
    PalabrasClave,
    PalabrasClaveUsuario
)
from django.db.models import Count


def parse_possible_date(date_str):
    """
    Intenta convertir date_str a objeto date usando distintos formatos.
    Retorna un objeto date si la conversión es exitosa o None en caso contrario.
    """
    # Lista de formatos que aceptamos
    formatos = ['%d/%m/%Y', '%d-%m-%Y', '%d%m%Y']
    for fmt in formatos:
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import datetime
from django.db.models import Q, Count
from .models import LicitacionArchivo, Usuario, UsuarioLicitacionPrioridadArchivado
from django.core.paginator import Paginator

@login_required
def listar_licitaciones_archivadas(request):
    fecha_str = request.GET.get('fecha_archivado', '').strip()
    tipo_licitaciones = request.GET.get('tipo', 'priorizadas').strip()

    fechas_con_datos = LicitacionArchivo.objects.exclude(fecha_archivado__isnull=True)\
        .order_by('fecha_archivado')\
        .values_list('fecha_archivado', flat=True)\
        .distinct()

    user = request.user

    if not fecha_str:
        opciones = {}
        if user.is_superuser:
            opciones['mostrar_todas'] = True
            opciones['mostrar_priorizadas'] = False
        else:
            opciones['mostrar_todas'] = True
            opciones['mostrar_priorizadas'] = True

        return render(request, 'listar_licitaciones_archivadas.html', {
            'fechas_con_datos': fechas_con_datos,
            'mostrar_calendario': True,
            'tipo': tipo_licitaciones,
            'opciones': opciones
        })

    try:
        fecha_archivado = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return render(request, 'error.html', {'mensaje': 'Formato de fecha incorrecto. Usa AAAA-MM-DD.'})

    search_query = request.GET.get('search', '').strip()
    estado_filtro = request.GET.get('codigo_estado', '')
    organismo_filtro = request.GET.get('organismo', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    ordenar_por = request.GET.get('ordenar_por', '-fecha_publicacion')

    if user.is_staff:
        licitaciones = LicitacionArchivo.objects.filter(fecha_archivado=fecha_archivado)
    else:
        if tipo_licitaciones == 'todas':
            licitaciones = LicitacionArchivo.objects.filter(fecha_archivado=fecha_archivado)
        else:
            codigos_priorizados = UsuarioLicitacionPrioridadArchivado.objects.filter(
                usuario=user, prioridad=True
            ).values_list('codigo_licitacion', flat=True)

            if not codigos_priorizados:
                return render(request, 'listar_licitaciones_archivadas.html', {
                    'licitaciones': [],
                    'fecha_archivado': fecha_archivado,
                    'fechas_con_datos': fechas_con_datos,
                    'tipo': tipo_licitaciones,
                    'mensaje': 'No hay licitaciones archivadas disponibles para tu perfil en esta fecha.'
                })

            licitaciones = LicitacionArchivo.objects.filter(
                codigo_externo__in=codigos_priorizados,
                fecha_archivado=fecha_archivado
            )

    # Aplicar filtros
    if search_query:
        licitaciones = licitaciones.filter(
            Q(nombre__icontains=search_query) | Q(codigo_externo__icontains=search_query)
        )
    if estado_filtro:
        licitaciones = licitaciones.filter(estado=estado_filtro)
    if organismo_filtro:
        licitaciones = licitaciones.filter(nombre_organismo__icontains=organismo_filtro)
    if fecha_inicio and fecha_fin:
        licitaciones = licitaciones.filter(fecha_publicacion__range=[fecha_inicio, fecha_fin])

    # Ordenar
    licitaciones = licitaciones.order_by(ordenar_por)

    # Paginación
    paginator = Paginator(licitaciones, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Mapeo de estados
    estado_map = {
        '5': 'Publicada',
        '6': 'Cerrada',
        '7': 'Desierta',
        '8': 'Adjudicada',
        '18': 'Revocada',
        '19': 'Suspendida'
    }

    # Agregar el estado mapeado a cada licitación
    for licitacion in page_obj:
        licitacion.estado_display = estado_map.get(str(licitacion.estado), licitacion.estado)

    # Calcular la distribución de estados (solo si no hay filtro de estado)
    estado_distribucion = []
    if not estado_filtro:
        distribucion_raw = licitaciones.values('estado').annotate(total=Count('estado')).order_by()
        print("Distribución cruda:", list(distribucion_raw))  # Depuración
        estado_distribucion = [
            {'estado': estado_map.get(str(item['estado']), item['estado']), 'total': item['total']}
            for item in distribucion_raw
        ]
        print("Distribución mapeada:", estado_distribucion)  # Depuración

    return render(request, 'listar_licitaciones_archivadas.html', {
        'licitaciones': page_obj,
        'fecha_archivado': fecha_archivado,
        'fechas_con_datos': fechas_con_datos,
        'mostrar_calendario': False,
        'tipo': tipo_licitaciones,
        'search_query': search_query,
        'estado_filtro': estado_filtro,
        'organismo_filtro': organismo_filtro,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'ordenar_por': ordenar_por,
        'estado_distribucion': estado_distribucion
    })


@login_required
def detalle_licitacion_archivada(request, id):
    licitacion = get_object_or_404(LicitacionArchivo, id=id)
    return render(request, 'detalle_licitacion_archivada.html', {'licitacion': licitacion})


@login_required
def listar_licitaciones_generales(request):
    """
    Vista que muestra todas las licitaciones disponibles para cualquier usuario con filtros avanzados.
    """
    search_query = request.GET.get('search', '').strip()
    estado_filtro = request.GET.get('codigo_estado', '')
    organismo_filtro = request.GET.get('organismo', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    ordenar_por = request.GET.get('ordenar_por', '-fecha_publicacion')

    licitaciones = LicitacionDiaria.objects.all()

    # Aplicar filtros
    if search_query:
        licitaciones = licitaciones.filter(
            Q(nombre__icontains=search_query) | Q(codigo_externo__icontains=search_query)
        )
    if estado_filtro:
        licitaciones = licitaciones.filter(codigo_estado=estado_filtro)
    if organismo_filtro:
        licitaciones = licitaciones.filter(nombre_organismo__icontains=organismo_filtro)
    if fecha_inicio and fecha_fin:
        licitaciones = licitaciones.filter(fecha_publicacion__range=[fecha_inicio, fecha_fin])
    
    # Ordenar
    licitaciones = licitaciones.order_by(ordenar_por)

    # Paginación
    paginator = Paginator(licitaciones, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Mapeo de estados largos a nombres cortos
    estado_map = {
        'Desierta (o art. 3 ó 9 Ley 19.886)': 'Desierta',
        'Publicada': 'Publicada',
        'Cerrada': 'Cerrada',
        'Adjudicada': 'Adjudicada',
        'Revocada': 'Revocada',
        'Suspendida': 'Suspendida'
    }

    # Agregar el estado mapeado a cada licitación
    for licitacion in page_obj:
        licitacion.estado_display = estado_map.get(licitacion.estado, licitacion.estado)

    # Calcular la distribución de estados (también mapeamos para el gráfico)
    estado_distribucion_raw = licitaciones.values('estado').annotate(total=Count('estado')).order_by()
    estado_distribucion = [
        {'estado': estado_map.get(item['estado'], item['estado']), 'total': item['total']}
        for item in estado_distribucion_raw
    ]
    # print("Estado Distribución:", estado_distribucion)

    return render(request, 'listar_licitaciones_generales.html', {
        'licitaciones': page_obj,
        'search_query': search_query,
        'estado_filtro': estado_filtro,
        'organismo_filtro': organismo_filtro,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'ordenar_por': ordenar_por,
        'estado_distribucion': estado_distribucion,
    })


@login_required
def listar_licitaciones_priorizadas(request):
    """
    Vista que muestra solo las licitaciones priorizadas para el usuario actual, basadas en el análisis de la IA,
    con filtros avanzados y gráfico de distribución de estados.
    """
    search_query = request.GET.get('search', '').strip()
    estado_filtro = request.GET.get('codigo_estado', '')
    organismo_filtro = request.GET.get('organismo', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    ordenar_por = request.GET.get('ordenar_por', '-fecha_cierre')
    user = request.user

    # Obtener los códigos de licitaciones priorizadas para el usuario actual
    codigos_priorizados = UsuarioLicitacionPrioridad.objects.filter(
        usuario=user,
        prioridad=True
    ).values_list('codigo_licitacion', flat=True)

    if not codigos_priorizados:
        print("No hay licitaciones priorizadas para este usuario.")
        return render(request, 'listar_licitaciones_priorizadas.html', {
            'licitaciones': [],
            'mensaje': 'No hay licitaciones recomendadas disponibles para tu perfil.'
        })

    # Filtrar licitaciones priorizadas
    licitaciones = LicitacionDiaria.objects.filter(codigo_externo__in=codigos_priorizados)

    # Aplicar filtros
    if search_query:
        licitaciones = licitaciones.filter(
            Q(nombre__icontains=search_query) | Q(codigo_externo__icontains=search_query)
        )
    if estado_filtro:
        licitaciones = licitaciones.filter(codigo_estado=estado_filtro)
    if organismo_filtro:
        licitaciones = licitaciones.filter(nombre_organismo__icontains=organismo_filtro)
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            licitaciones = licitaciones.filter(fecha_publicacion__range=[fecha_inicio_dt, fecha_fin_dt])
        except ValueError:
            print("Formato de fecha inválido, ignorando filtro de fechas.")

    # Ordenar
    licitaciones = licitaciones.order_by(ordenar_por)

    # Paginación
    paginator = Paginator(licitaciones, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Mapeo de estados largos a nombres cortos
    estado_map = {
        'Desierta (o art. 3 ó 9 Ley 19.886)': 'Desierta',
        'Publicada': 'Publicada',
        'Cerrada': 'Cerrada',
        'Adjudicada': 'Adjudicada',
        'Revocada': 'Revocada',
        'Suspendida': 'Suspendida'
    }

    # Agregar el estado mapeado a cada licitación
    for licitacion in page_obj:
        licitacion.estado_display = estado_map.get(licitacion.estado, licitacion.estado)

    # Calcular la distribución de estados basada en las licitaciones filtradas
    estado_distribucion_raw = licitaciones.values('estado').annotate(total=Count('estado')).order_by()
    estado_distribucion = [
        {'estado': estado_map.get(item['estado'], item['estado']), 'total': item['total']}
        for item in estado_distribucion_raw
    ]
    # print("Estado Distribución:", estado_distribucion)

    # print(f"Licitaciones priorizadas enviadas al template: {licitaciones.count()}")

    return render(request, 'listar_licitaciones_priorizadas.html', {
        'licitaciones': page_obj,
        'search_query': search_query,
        'estado_filtro': estado_filtro,
        'organismo_filtro': organismo_filtro,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'ordenar_por': ordenar_por,
        'estado_distribucion': estado_distribucion,
    })


def detalle_licitacion(request, id):
    licitacion = get_object_or_404(LicitacionDiaria, id=id)
    return render(request, 'detalle_licitacion.html', {'licitacion': licitacion})


def is_superadmin(user):
    return user.is_superuser


def is_admin(user):
    return user.is_staff


def home(request):
    return render(request, 'home.html')


def user_login(request):
    alert = None

    if request.method == 'POST':
        rut = request.POST.get('rut')
        password = request.POST.get('password')

        user = authenticate(request, username=rut, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            if Usuario.objects.filter(rut=rut).exists():
                alert = {"type": "danger", "message": "Contraseña incorrecta."}
            else:
                alert = {"type": "danger", "message": "El usuario no existe."}

    return render(request, 'login.html', {'alert': alert})


def user_logout(request):
    logout(request)
    return redirect('/')

@login_required
@user_passes_test(is_admin)
def gestion_usuarios(request):
    # Obtener parámetros de filtro desde GET
    search_text = request.GET.get('search_text', '')  # Búsqueda unificada
    rol_id = request.GET.get('rol', '')  # Filtro por rol
    ordenar_por = request.GET.get('ordenar_por', 'nombre')  # Ordenamiento por defecto
    alert = request.GET.get('alert', None)
    alert_type = request.GET.get('type', 'info')

    # Filtrado según rol
    if request.user.is_superuser:
        usuarios = Usuario.objects.all()
    else:
        usuarios = Usuario.objects.filter(creado_por=request.user)

    # Aplicar filtros
    if search_text:
        usuarios = usuarios.filter(
            Q(rut__icontains=search_text) |
            Q(nombre__icontains=search_text) |
            Q(email__icontains=search_text)
            # Si tienes numero_telefono, añade: Q(numero_telefono__icontains=search_text)
        )
    if rol_id:
        usuarios = usuarios.filter(rol_id=rol_id)

    # Ordenar
    if ordenar_por not in ['nombre', 'email']:  # Validar opciones, no hay 'contacto' en el modelo
        ordenar_por = 'nombre'
    usuarios = usuarios.order_by(ordenar_por)

    # Paginación
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Procesar rol_display
    for usuario in page_obj:
        usuario.rol_display = usuario.rol.nombre_rol if usuario.rol else 'Sin rol'

    # Filtro de roles según permisos
    if request.user.is_superuser:
        roles = Rol.objects.all()
    else:
        roles = Rol.objects.filter(creado_por=request.user)  # Asumiendo que Rol tiene creado_por

    # Contexto
    context = {
        'usuarios': page_obj,
        'roles': roles,
        'search_text': search_text,
        'rol': rol_id,
        'ordenar_por': ordenar_por,
        'alert': alert,
        'alert_type': alert_type,
    }
    return render(request, 'gestion_usuarios.html', context)


@login_required
@user_passes_test(is_admin)
def crear_usuario(request):
    if not request.user.is_superuser:
        errors = []
        if not Rol.objects.filter(creado_por=request.user).exists():
            errors.append("No tienes roles creados. Por favor, crea un rol en la sección de gestión de roles.")
        if errors:
            messages.error(request, " ".join(errors))
            return redirect('gestion_usuarios')

    if request.method == "POST":
        form = UsuarioForm(request.POST, user=request.user)
        if form.is_valid():
            usuario = form.save(commit=False)
            if not request.user.is_superuser:
                usuario.is_staff = False
                usuario.creado_por = request.user
            else:
                usuario.creado_por = request.user
            usuario.save()
            messages.success(request, "Usuario creado exitosamente.")
            return redirect(reverse('gestion_usuarios'))
        else:
            messages.error(request, "Ocurrió un error al crear el usuario.")
    else:
        form = UsuarioForm(user=request.user)
    
    return render(request, 'crear_usuario.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id_usuario=id)
    # Permitir edición solo si el usuario actual es superadmin o es el mismo admin creador
    if not request.user.is_superuser and usuario.creado_por != request.user:
        return HttpResponseForbidden("No tienes permiso para editar este usuario.")
    alert = None

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario, user=request.user)
        if form.is_valid():
            usuario = form.save(commit=False)
            # Forzar is_staff = False para administradores normales, incluso si se enviara un valor (por seguridad)
            if not request.user.is_superuser:
                usuario.is_staff = False
            usuario.save()
            return redirect(f"{reverse('gestion_usuarios')}?alert=Usuario actualizado correctamente.&type=success")
        else:
            # No almacenamos los errores en la sesión ni los pasamos persistentemente
            alert = {"type": "danger", "message": "Ocurrió un error al actualizar el usuario."}
    else:
        form = UsuarioForm(instance=usuario, user=request.user)

    return render(request, 'editar_usuario.html', {'form': form, 'alert': alert})


@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id_usuario=id)
    if request.method == "POST":
        usuario.delete()
        return redirect(f"{reverse('gestion_usuarios')}?alert=Usuario eliminado exitosamente.&type=success")

    return render(request, 'eliminar_usuario.html', {'usuario': usuario})


@login_required
@user_passes_test(is_admin)
def gestion_roles(request):
    # Obtener parámetros de filtro
    search_text = request.GET.get('search_text', '')

    # Filtrado según rol del usuario
    if request.user.is_superuser:
        roles = Rol.objects.all()
    else:
        roles = Rol.objects.filter(creado_por=request.user)  # Asumiendo que Rol tiene creado_por

    # Aplicar filtro de búsqueda
    if search_text:
        roles = roles.filter(Q(nombre_rol__icontains=search_text))

    # Paginación
    paginator = Paginator(roles, 10)  # 10 roles por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto
    context = {
        'roles': page_obj,
        'search_text': search_text,
    }
    return render(request, 'gestion_roles.html', context)


@login_required
@user_passes_test(is_admin)
def crear_rol(request):
    if request.method == "POST":
        form = RolForm(request.POST, user=request.user)
        if form.is_valid():
            rol = form.save(commit=False)
            rol.creado_por = request.user
            rol.save()
            messages.success(request, "Rol creado exitosamente.")
            return redirect(reverse('gestion_roles'))
        else:
            messages.error(request, "Ocurrió un error al crear el rol.")
    else:
        form = RolForm(user=request.user)
    return render(request, 'crear_rol.html', {'form': form})



@login_required
@user_passes_test(is_admin)
def editar_rol(request, id):
    rol = get_object_or_404(Rol, id_rol=id)
    alert = None
    if request.method == 'POST':
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('gestion_roles')}?alert=Rol actualizado correctamente.&type=success")
        else:
            alert = {"type": "danger", "message": "Ocurrió un error al actualizar el rol."}
    else:
        form = RolForm(instance=rol)
    return render(request, 'editar_rol.html', {'form': form, 'alert': alert})

@login_required
@user_passes_test(is_admin)
def eliminar_rol(request, id):
    rol = get_object_or_404(Rol, id_rol=id)
    if request.method == 'POST':
        rol.delete()
        return redirect(f"{reverse('gestion_roles')}?alert=Rol eliminado exitosamente.&type=success")
    return render(request, 'eliminar_rol.html', {'rol': rol})


@login_required
@user_passes_test(is_admin)
def gestionar_palabras_clave(request):
    obj, created = PalabrasClave.objects.get_or_create(admin=request.user)

    if request.method == "POST":
        form = PalabrasClaveForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Palabras clave del administrador actualizadas correctamente.")
            return redirect('gestionar_palabras_admin')
        else:
            messages.error(request, "Error al actualizar las palabras clave del administrador.")
    else:
        form = PalabrasClaveForm(instance=obj)

    return render(request, 'gestionar_palabras_admin.html', {'form': form})

# Vista para usuarios normales
@login_required
def gestionar_palabras_clave_usuario(request):
    obj, created = PalabrasClaveUsuario.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        form = PalabrasClaveUsuarioForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus palabras clave fueron actualizadas correctamente.")
            return redirect('gestionar_palabras_usuarios')
        else:
            messages.error(request, "Error al actualizar tus palabras clave.")
    else:
        form = PalabrasClaveUsuarioForm(instance=obj)

    return render(request, 'gestionar_palabras_usuarios.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def listar_todas_palabras(request):
    # Palabras clave del admin
    admin_keywords = PalabrasClave.objects.select_related('admin').all()

    # Palabras clave de los usuarios
    user_keywords = PalabrasClaveUsuario.objects.select_related('usuario').all()

    return render(request, 'listar_todas.html', {
        'admin_keywords': admin_keywords,
        'user_keywords': user_keywords,
    })


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def subir_clientes_excel(request):
    if request.method == "POST":
        form = SubidaClientesForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            try:
                df = pd.read_excel(archivo)
            except Exception as e:
                messages.error(request, f"Error al leer el archivo: {e}")
                return redirect('gestion_clientes')
            
            columnas_requeridas = [
                'nombre_cliente', 'rut_cliente', 'tipo_cliente', 'contacto_principal',
                'email', 'sector', 'descripcion_rubro', 'estado'
            ]
            if not set(columnas_requeridas).issubset(df.columns):
                messages.error(request, "El archivo no tiene el formato correcto.")
                return redirect('gestion_clientes')

            errores = False  # Variable para rastrear si hubo errores
            
            for _, row in df.iterrows():
                rut_cliente = str(row['rut_cliente']).strip()
                sector_nombre = str(row['sector']).strip()

                try:
                    sector_obj = Sector.objects.get(codigo=sector_nombre)
                except Sector.DoesNotExist:
                    messages.error(
                        request,
                        f"No se encontró el sector '{sector_nombre}'. "
                        f"No se creó el cliente con RUT {rut_cliente}."
                    )
                    errores = True
                    continue

                try:
                    Cliente.objects.create(
                        rut_cliente=rut_cliente,
                        creado_por=request.user,
                        nombre_cliente=row['nombre_cliente'],
                        tipo_cliente=row['tipo_cliente'],
                        contacto_principal=row['contacto_principal'],
                        email=row['email'],
                        sector=sector_obj,
                        descripcion_rubro=row['descripcion_rubro'],
                        estado=row['estado'],
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f"Error al crear el cliente con RUT {rut_cliente}: {e}"
                    )
                    errores = True

            if not errores:
                messages.success(request, "Clientes subidos correctamente.")

            return redirect('gestion_clientes')

    else:
        form = SubidaClientesForm()
    return render(request, 'clientes/subir_excel.html', {'form': form})




@login_required
def descargar_excel_muestra(request):
    # Crear un workbook y seleccionar la hoja activa
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Formato Clientes"
    
    # Definir las columnas requeridas (ajusta según tus necesidades)
    columnas = [
        "nombre_cliente",
        "rut_cliente",
        "tipo_cliente",         # Ejemplo: individual, empresa, institucion
        "contacto_principal",
        "email",
        "sector",               # Utilizando las opciones definidas en TIPO_SECTOR_CHOICES
        "descripcion_rubro",
        "estado",               # Activo, inactivo
    ]
    
    # Escribir la fila de encabezados
    ws.append(columnas)
    
    # (Opcional) Agregar una fila de ejemplo para ilustrar el formato
    ws.append([
        "Ejemplo S.A.",
        "12.345.678-9",
        "empresa",
        "Alberto Delgado",
        "contacto@ejemplo.com",
        "tecnologia",
        "Empresa dedicada a la innovación tecnológica.",
        "activo"
    ])
    
    # Guardar el workbook en un objeto BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Preparar la respuesta HTTP para la descarga
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="formato_clientes.xlsx"'
    return response


@login_required
def gestion_clientes(request):
    # Solo admin y superadmin pueden acceder
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")

    # Obtener parámetros de filtro desde GET
    search_text = request.GET.get('search_text', '')  # Búsqueda unificada
    tipo_cliente = request.GET.get('tipo_cliente', '')
    contacto = request.GET.get('contacto', '')
    email = request.GET.get('email', '')
    sector = request.GET.get('sector', '')
    ordenar_por = request.GET.get('ordenar_por', 'nombre_cliente')

    # Filtrado según rol
    if request.user.is_superuser:
        clientes = Cliente.objects.all()
    else:
        clientes = Cliente.objects.filter(creado_por=request.user)

    # Aplicar filtros
    if search_text:
        clientes = clientes.filter(
            Q(nombre_cliente__icontains=search_text) |
            Q(contacto_principal__icontains=search_text) |
            Q(email__icontains=search_text) |
            Q(rut_cliente__icontains=search_text)
        )
    if tipo_cliente:
        clientes = clientes.filter(tipo_cliente=tipo_cliente)
    if contacto:
        clientes = clientes.filter(contacto_principal__icontains=contacto)
    if email:
        clientes = clientes.filter(email__icontains=email)
    if sector:
        clientes = clientes.filter(sector__codigo=sector)

    # Ordenar
    clientes = clientes.order_by(ordenar_por)

    # Paginación
    paginator = Paginator(clientes, 10)  # 10 clientes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtener todos los sectores para el dropdown
    sectores = Sector.objects.all()

    # Lógica de subida de clientes desde Excel
    if request.method == "POST" and 'archivo' in request.FILES:
        excel_form = SubidaClientesForm(request.POST, request.FILES)
        if excel_form.is_valid():
            archivo = excel_form.cleaned_data['archivo']
            try:
                df = pd.read_excel(archivo)
            except Exception as e:
                messages.error(request, f"Error al leer el archivo: {e}")
                return redirect('gestion_clientes')
            
            columnas_requeridas = [
                'nombre_cliente', 'rut_cliente', 'tipo_cliente', 'contacto_principal',
                'email', 'sector', 'descripcion_rubro', 'estado'
            ]
            if not set(columnas_requeridas).issubset(df.columns):
                messages.error(
                    request,
                    "El archivo no tiene el formato correcto. "
                    + "Se requieren las columnas: " + ", ".join(columnas_requeridas)
                )
                return redirect('gestion_clientes')

            for _, row in df.iterrows():
                rut = str(row['rut_cliente']).strip()
                sector_codigo = str(row['sector']).strip()

                # Intentar obtener la instancia de Sector
                try:
                    sector_obj = Sector.objects.get(codigo=sector_codigo)
                except Sector.DoesNotExist:
                    messages.error(
                        request,
                        f"No se encontró el sector '{sector_codigo}'. "
                        f"No se creó/actualizó el cliente con RUT {rut}."
                    )
                    continue

                # Si el sector existe, actualizamos/creamos el cliente
                Cliente.objects.update_or_create(
                    rut_cliente=rut,
                    defaults={
                        'nombre_cliente': row['nombre_cliente'],
                        'tipo_cliente': row['tipo_cliente'],
                        'contacto_principal': row['contacto_principal'],
                        'email': row['email'],
                        'sector': sector_obj,
                        'descripcion_rubro': row['descripcion_rubro'],
                        'estado': row['estado'],
                        'creado_por': request.user
                    }
                )
            messages.success(request, "Clientes subidos correctamente.")
            return redirect('gestion_clientes')
        else:
            messages.error(request, "Ocurrió un error al procesar el archivo.")
    else:
        excel_form = SubidaClientesForm()

    context = {
        'clientes': page_obj,
        'excel_form': excel_form,
        'search_text': search_text,
        'tipo_cliente': tipo_cliente,
        'contacto': contacto,
        'email': email,
        'sector': sector,
        'ordenar_por': ordenar_por,
        'sectores': sectores,
    }
    return render(request, 'gestion_clientes.html', context)


@login_required
def mis_clientes(request):
    # Filtrar los clientes asignados al usuario actual
    clientes = Cliente.objects.filter(asignado_a=request.user)

    # Obtener parámetros de filtro desde GET
    search_text = request.GET.get('search_text', '')  # Búsqueda unificada
    tipo_cliente = request.GET.get('tipo_cliente', '')  
    contacto = request.GET.get('contacto', '')
    email = request.GET.get('email', '')
    sector = request.GET.get('sector', '')  
    ordenar_por = request.GET.get('ordenar_por', 'nombre_cliente')

    # Aplicar filtros
    if search_text:
        clientes = clientes.filter(
            Q(nombre_cliente__icontains=search_text) |
            Q(contacto_principal__icontains=search_text) |
            Q(email__icontains=search_text) |
            Q(rut_cliente__icontains=search_text)
        )
    if tipo_cliente:
        clientes = clientes.filter(tipo_cliente=tipo_cliente)
    if contacto:
        clientes = clientes.filter(contacto_principal__icontains=contacto)
    if email:
        clientes = clientes.filter(email__icontains=email)
    if sector:
        clientes = clientes.filter(sector__codigo=sector)

    # Ordenar
    clientes = clientes.order_by(ordenar_por)

    # Paginación
    paginator = Paginator(clientes, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtener todos los sectores para el dropdown
    sectores = Sector.objects.all()

    return render(request, 'mis_clientes.html', {
        'clientes': page_obj,
        'search_text': search_text,
        'tipo_cliente': tipo_cliente,
        'contacto': contacto,
        'email': email,
        'sector': sector,
        'ordenar_por': ordenar_por,
        'sectores': sectores,  
    })


@login_required
def lista_sectores(request):
    # Obtener el parámetro de búsqueda desde GET
    search_text = request.GET.get('search_text', '')

    # Todos los usuarios pueden ver todos los sectores
    sectores = Sector.objects.all()

    # Aplicar filtro de búsqueda si existe search_text
    if search_text:
        sectores = sectores.filter(
            Q(codigo__icontains=search_text) |
            Q(descripcion__icontains=search_text)
        )

    # Ordenar por ID (como en la versión original)
    sectores = sectores.order_by('id')

    # Renderizar la plantilla con los sectores filtrados
    return render(request, 'lista_sectores.html', {
        'sectores': sectores,
        'search_text': search_text,
    })


@login_required
def crear_sector(request):
    # Solo el superusuario puede crear
    if not request.user.is_superuser:
        return HttpResponseForbidden("Solo el superadmin puede crear sectores.")

    if request.method == 'POST':
        form = SectorForm(request.POST)
        if form.is_valid():
            sector = form.save(commit=False)
            # Opcional: sector.creado_por = request.user
            sector.save()
            messages.success(request, "Sector creado con éxito.")
            return redirect('lista_sectores')
    else:
        form = SectorForm()

    return render(request, 'crear_sector.html', {'form': form})


@login_required
def editar_sector(request, sector_id):
    # Solo el superusuario puede editar
    if not request.user.is_superuser:
        return HttpResponseForbidden("Solo el superadmin puede editar sectores.")

    sector = get_object_or_404(Sector, pk=sector_id)

    if request.method == 'POST':
        form = SectorForm(request.POST, instance=sector)
        if form.is_valid():
            form.save()
            messages.success(request, "Sector actualizado con éxito.")
            return redirect('lista_sectores')
    else:
        form = SectorForm(instance=sector)

    return render(request, 'editar_sector.html', {
        'form': form,
        'sector': sector
    })


@login_required
def eliminar_sector(request, sector_id):
    # Solo el superusuario puede eliminar
    if not request.user.is_superuser:
        return HttpResponseForbidden("Solo el superadmin puede eliminar sectores.")

    sector = get_object_or_404(Sector, pk=sector_id)

    if request.method == "POST":
        sector.delete()
        messages.success(request, "Sector eliminado con éxito.")
        return redirect('lista_sectores')
    
    return render(request, 'eliminar_sector.html', {'sector': sector})


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def asignar_cliente_usuario(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    
    # Permitir asignar solo si el usuario es superadmin o si es admin y el cliente fue creado por él.
    if not (request.user.is_superuser or (request.user.is_staff and cliente.creado_por == request.user)):
        messages.error(request, "No tienes permiso para asignar este cliente.")
        return redirect(reverse('gestion_clientes'))
    
    if request.method == "POST":
        # Recoger la lista de IDs de usuarios seleccionados (vendedores)
        usuario_ids = request.POST.getlist('usuario_ids')
        if usuario_ids:
            # Actualizamos la asignación con la lista de IDs; esto reemplaza las asignaciones previas.
            cliente.asignado_a.set(usuario_ids)
            messages.success(request, "Cliente asignado correctamente a los usuarios seleccionados.")
            return redirect(reverse('gestion_clientes'))
        else:
            # Si no se selecciona ninguno, se limpian las asignaciones
            cliente.asignado_a.clear()
            messages.success(request, "Se han eliminado todas las asignaciones para este cliente.")
            return redirect(reverse('gestion_clientes'))
    else:
        # Filtrar vendedores según el tipo de usuario que está asignando:
        if request.user.is_superuser:
            # El superadmin ve todos los vendedores
            vendedores = Usuario.objects.filter(is_staff=False)
        else:
            # Un admin solo debe ver los vendedores que él creó
            vendedores = Usuario.objects.filter(creado_por=request.user, is_staff=False)
        context = {
            'cliente': cliente,
            'usuarios': vendedores,
        }
        return render(request, 'asignar_cliente.html', context)



@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    # Solo permitir que:
    # - Superadmin edite cualquier cliente, o
    # - Un admin (is_staff) edite únicamente los clientes que él creó.
    if not (request.user.is_superuser or (request.user.is_staff and cliente.creado_por == request.user)):
        messages.error(request, "No tienes permiso para editar este cliente.")
        return redirect(reverse('gestion_clientes'))
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect(reverse('gestion_clientes'))
        else:
            messages.error(request, "Ocurrió un error al actualizar el cliente.")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'editar_cliente.html', {'form': form})

@login_required
def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    # Solo permitir que:
    # - Superadmin elimine cualquier cliente, o
    # - Un admin elimine solo los clientes que él creó.
    if not (request.user.is_superuser or (request.user.is_staff and cliente.creado_por == request.user)):
        messages.error(request, "No tienes permiso para eliminar este cliente.")
        return redirect(reverse('gestion_clientes'))
    
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, "Cliente eliminado exitosamente.")
        return redirect(reverse('gestion_clientes'))
    
    return render(request, 'eliminar_cliente.html', {'cliente': cliente})


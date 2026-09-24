import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from appone.models import Usuario, Rol, Cliente, Sector, PalabrasClave, PalabrasClaveUsuario



class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre_rol', 'descripcion']
        widgets = {
            'nombre_rol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del rol'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese una descripción (opcional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extraemos el usuario si se pasa
        super().__init__(*args, **kwargs)



class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Ingrese una nueva contraseña si desea cambiarla (deje en blanco para mantener la actual).",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Confirme la nueva contraseña.",
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Formato: +1234567890 (opcional)",
    )
    
    class Meta:
        model = Usuario
        fields = ['rut', 'nombre', 'email', 'phone_number', 'rol', 'is_active', 'is_staff', 'password']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def calcular_digito_verificador(self, rut_sin_dv):
        """
        Calcula el dígito verificador de un RUT chileno
        (sin puntos ni guion).
        Devuelve '0'..'9' o 'K'.
        """
        rut_sin_dv = rut_sin_dv.strip()
        reversed_digits = map(int, reversed(rut_sin_dv))
        
        # Serie de multiplicadores: 2,3,4,5,6,7
        factors = [2, 3, 4, 5, 6, 7]
        total = 0
        i = 0
        
        for d in reversed_digits:
            total += d * factors[i % 6]
            i += 1

        remainder = 11 - (total % 11)
        
        if remainder == 11:
            return '0'
        elif remainder == 10:
            return 'K'
        else:
            return str(remainder)

    def clean_rut(self):
        """
        Limpia y valida el campo 'rut' usando el cálculo de dígito verificador (Módulo 11).
        """
        rut_input = self.cleaned_data.get('rut', '')
        
        # 1) Convertimos a mayúsculas y quitamos espacios
        rut_limpio = rut_input.upper().replace(" ", "")
        # 2) Quitamos puntos
        rut_limpio = rut_limpio.replace(".", "")
        
        # 3) Validamos estructura con regex: números + dígito verificador
        #    Este patrón acepta 'XXXXXXXX' o 'XXXXXXXX-DV'
        pattern = r'^(\d+)-?([\dkK])$'
        match = re.match(pattern, rut_limpio)
        if not match:
            raise ValidationError("Formato de RUT inválido. Use por ejemplo 12345678-9 o 12.345.678-9.")
        
        parte_numerica, dv_ingresado = match.groups()
        
        # 4) Calculamos DV esperado
        dv_calculado = self.calcular_digito_verificador(parte_numerica)
        
        # 5) Comparamos con DV ingresado
        if dv_calculado != dv_ingresado.upper():
            raise ValidationError(f"El dígito verificador no coincide. Debería ser {dv_calculado}.")
        
        # 6) Retornamos un RUT "normalizado": sin puntos y con guion
        return f"{parte_numerica}-{dv_calculado}"
    
    def clean_phone_number(self):
        """
        Valida el número de teléfono para asegurarse de que tenga un formato válido.
        Ejemplo: +1234567890
        """
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Validar formato básico: debe empezar con '+' y tener 10-15 dígitos
            if not phone_number.startswith('+'):
                raise ValidationError("El número de teléfono debe comenzar con '+' (ejemplo: +1234567890)")
            if not phone_number[1:].isdigit() or len(phone_number) < 11 or len(phone_number) > 16:
                raise ValidationError("El número de teléfono debe contener solo dígitos después del '+' y tener entre 10 y 15 dígitos en total.")
        return phone_number

    def clean(self):
        """
        Valida contraseñas (password/confirm_password) usando las validaciones de Django.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Si se ingresó una contraseña, verifica que coincida con la confirmación
        if password or confirm_password:
            if not password:
                self.add_error("password", "Debe ingresar una contraseña.")
            if not confirm_password:
                self.add_error("confirm_password", "Debe confirmar la contraseña.")
            if password != confirm_password:
                self.add_error("confirm_password", "Las contraseñas no coinciden.")

            # Valida la contraseña contra las reglas de AUTH_PASSWORD_VALIDATORS
            if password:
                try:
                    validate_password(password, user=self.instance)
                except ValidationError as e:
                    self.add_error("password", e.messages)

        return cleaned_data

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Cambiar los labels de "is_active" e "is_staff"
        self.fields['is_active'].label = "Activo"
        self.fields['is_staff'].label = "Administrador"

        # Filtrar el campo 'rol' según el usuario
        if current_user and not current_user.is_superuser:
            self.fields['rol'].queryset = Rol.objects.filter(creado_por=current_user)
            if not self.fields['rol'].queryset.exists():
                self.fields['rol'].help_text = "No tienes roles creados. Crea un rol en la sección de gestión de roles."
            # Eliminar el campo is_staff para que no se pueda modificar
            self.fields.pop('is_staff', None)
        elif current_user and current_user.is_superuser:
            # Si se está editando un usuario y tiene un creador asignado (un admin), limitar el queryset a los roles creados por ese admin.
            if self.instance and getattr(self.instance, 'creado_por', None) and not self.instance.creado_por.is_superuser:
                self.fields['rol'].queryset = Rol.objects.filter(creado_por=self.instance.creado_por)
            else:
                self.fields['rol'].queryset = Rol.objects.all()

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        # Si se proporcionó una nueva contraseña y coincide con la confirmación, actualiza la contraseña
        if password and confirm_password and password == confirm_password:
            usuario.set_password(password)
            print(f"Contraseña nueva hasheada y guardada: {usuario.password}")  # Depuración
        # Si no se proporcionó una nueva contraseña, mantén la contraseña original
        elif usuario.pk:
            # Obtener la contraseña actual del usuario desde la base de datos
            current_user = Usuario.objects.get(pk=usuario.pk)
            usuario.password = current_user.password
            print(f"Contraseña original mantenida: {usuario.password}")  # Depuración
        else:
            # Para un nuevo usuario sin contraseña, establecer una contraseña no usable
            usuario.set_unusable_password()
            print("Contraseña no usable establecida para nuevo usuario")

        if commit:
            usuario.save()
        return usuario


class PalabrasClaveForm(forms.ModelForm):
    class Meta:
        model = PalabrasClave
        fields = ['keywords']
        widgets = {
            'keywords': forms.TextInput(attrs={
                'class': 'form-control tagify-input',  # Clase para inicializar Tagify
                'placeholder': 'Ejemplo: construcción, infraestructura, salud',
                'value': ''  # Dejamos el valor inicial vacío, Tagify lo manejará
            }),
        }

    def clean_keywords(self):
        # Asegurarnos de que las palabras clave se guarden como una cadena separada por comas
        keywords = self.cleaned_data.get('keywords')
        if keywords:
            # Si Tagify envía las palabras como una lista (dependiendo de la configuración),
            # las convertimos a una cadena
            if isinstance(keywords, list):
                keywords = ', '.join(keywords)
            return keywords.strip()
        return keywords

class PalabrasClaveUsuarioForm(forms.ModelForm):
    class Meta:
        model = PalabrasClaveUsuario
        fields = ['keywords_usuario']
        widgets = {
            'keywords_usuario': forms.TextInput(attrs={
                'class': 'form-control tagify-input',  # Clase para inicializar Tagify
                'placeholder': 'Ejemplo: construcción, infraestructura, salud',
                'value': ''
            }),
        }

    def clean_keywords_usuario(self):
        # Similar al formulario anterior
        keywords = self.cleaned_data.get('keywords_usuario')
        if keywords:
            if isinstance(keywords, list):
                keywords = ', '.join(keywords)
            return keywords.strip()
        return keywords


class SubidaClientesForm(forms.Form):
    archivo = forms.FileField(label="Selecciona el archivo Excel")


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre_cliente',
            'rut_cliente',
            'tipo_cliente',
            'contacto_principal',
            'email',
            'sector',
            'descripcion_rubro',
            'estado',
        ]
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'rut_cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_cliente': forms.Select(attrs={'class': 'form-select'}),
            'contacto_principal': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sector': forms.Select(attrs={'class': 'form-select'}),
            'descripcion_rubro': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['codigo', 'descripcion']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
        }
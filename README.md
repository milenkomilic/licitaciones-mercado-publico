# Inicializar proyecto

## Instalar python

- Descargar e instalar Python de [python.org](https://www.python.org/)

- Verificar instalación por command line: python --version

## Descargar, instalar y crear nueva base de datos en postgres:

- Descarga e instala: [postgresql.org](https://www.postgresql.org/download/windows/)

- Crear usuario base para postgres desde SQL Shell

```
CREATE ROLE usuariobase WITH LOGIN PASSWORD 'clave';
ALTER ROLE usuariobase WITH CREATEDB;
ALTER ROLE usuariobase WITH CREATEROLE;
CREATE DATABASE mydb OWNER usuariobase;
CREATE DATABASE mydb;
```

- Ve a settings.py y edita rut, nombre y contraseña basado en tu base de datos
```
DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql',
			'NAME': 'mydb',
			'USER': 'usuariobase',
			'PASSWORD': '1234567',
			'HOST': 'localhost',
			'PORT': '5432',
		}
	}
```

## Crear ambiente virtual para las dependencias:

```
cd /path/a/tu/proyecto
python -m venv venv
venv\Scripts\activate
python.exe -m pip install --upgrade pip
cd licitaciones_mercado_publico
pip install -r requirements.txt
```

## Hacer las migraciones:

```
python manage.py makemigrations
python manage.py migrate
```

## Crear Superuser:

```
python manage.py createsuperuser
```


- Sigue los pasos para asignar rut(sin guion ej: 192288389), nombre, y clave


## Inicializar proyecto web:
```
python manage.py runserver
```

## Gestión de Usuarios:
- El superuser puede crear un número ilimitado de administradores (jerarquía: superadmin > admin > usuario).

- Cada administrador puede gestionar un número ilimitado de usuarios bajo su jerarquía.

## Gestión de Roles:
- Cada administrador puede crear y asignar roles a los usuarios.

## Gestión de Clientes:
- Cada administrador puede crear un listado de clientes(Detalles sobre cómo subir clientes están en el botón "Ayuda").

- Los clientes pueden ser asignados a usuarios por el administrador en este módulo.

## Gestión de Sectores:
- El superadmin define un listado de sectores relacionados con los clientes.
- Cada cliente tiene un sector asignado.
- Si un administrador necesita un nuevo sector, debe contactar al superadmin.

### Ejemplos:
- tecnología, salud, finanzas, manufactura, retail, alimentación, construcción, transporte, energía, agricultura, educación, turismo, consultoría, medios, automotriz.

## Gestión de Productos:
- Permite asignar productos a administradores y usuarios para enriquecer el perfil entregado a la IA y mejorar la clasificación.

- Tipos:
#### - Gestión de Productos (Admin)
#### - Gestión de Productos (User)

## Licitaciones Generales
- Extrae diariamente licitaciones de Mercado Público y las muestra en este módulo.

## Licitaciones Priorizadas
- Cada usuario tiene un perfil basado en roles, clientes, productos y sectores.
- La IA compara este perfil con las palabras clave de las licitaciones y retorna true o false.
- Las licitaciones con true se muestran en este módulo.

## Licitaciones Archivadas
- Archiva licitaciones generales y priorizadas de días anteriores.
- Los usuarios pueden acceder a licitaciones priorizadas (asignadas) o generales archivadas.

## Scripts Ejecutables (Diariamente)
Los siguientes scripts se ejecutan una vez al día en el orden indicado para actualizar, procesar, priorizar y archivar licitaciones.

### 1-. actualizar_licitaciones

- Descripción: Actualiza las licitaciones diarias obtenidas desde la API de Mercado Público.

- Funcionamiento:

	1-. Se conecta a la API externa de Mercado Público.
	
	2-. Descarga las licitaciones publicadas en el día actual.
	
	3-. Almacena los datos en la base de datos (tabla correspondiente, LicitacionesGenerales).

- Propósito: Garantiza que el módulo "Licitaciones Generales" muestre las licitaciones más recientes cada día.
- Notas: Requiere una clave de API válida y manejo de errores para fallos de conexión o límites de la API

### 2-. keywords_licitaciones

- Descripción: Extrae palabras clave de cada licitación y agrupa las licitaciones en clusters dinámicos basados en similitud.

- Funcionamiento:

	1-. Analiza el texto de cada licitación (e.j, título, descripción) para extraer palabras clave relevantes usando técnicas de procesamiento de lenguaje natural (NLP).
	
	2-. Aplica clustering jerárquico para agrupar licitaciones según la similitud de sus palabras clave.
	
	3-. Fusiona clusters "singleton" (con una sola licitación) con el cluster más cercano para reducir el número total de clusters.

	4-. Guarda los clusters y sus palabras clave representativas en la base de datos.

- Propósito: Prepara los datos para la priorización al identificar grupos de licitaciones similares.
- Notas: Utiliza bibliotecas como nltk o scikit-learn (presentes en tu requirements.txt) para NLP y clustering.

### 3-. profile_clientes_usuarios

- Descripción: Genera un perfil compacto para cada usuario basado en sus clientes, rol, sectores y palabras clave.

- Funcionamiento(Recopila datos de la base de datos):

	1-. Clientes asignados al usuario (usando iniciales en lugar de nombres completos para compactar).
	
	2-. Rol del usuario (e.j, desde la tabla Rol).
	
	3-. Palabras clave asignadas por el administrador y el usuario (e.j, desde "Gestión de Productos").
	
	4-. Sectores relacionados con los clientes (definidos por el superadmin).
	
	5-. Crea un perfil estructurado (e.j, en formato JSON o texto) para cada usuario.

- Propósito: Proporciona un resumen del usuario que la IA usará para evaluar la relevancia de las licitaciones.
- Notas: Asegura que los sectores estén sincronizados con la tabla gestionada por el superadmin.

### 4-. consulta_priorizacion

- Descripción: Consulta al modelo Mistral 7B Instruct en AWS Bedrock para determinar la relevancia de clusters de licitaciones según el perfil del usuario.

- Funcionamiento:

	- Prepara el cuerpo de la consulta con:
	
	1-. Perfil del usuario (generado por profile_clientes_usuarios).
	
	2-. Palabras clave representativas de cada cluster (de keywords_licitaciones).
	
	3-. Envía la consulta a AWS Bedrock usando el modelo Mistral 7B Instruct.
	
	- Instrucción al modelo:
	
	- "Eres una IA encargada de evaluar la relevancia de clusters de licitaciones en función del perfil de un usuario. El perfil del usuario indica la cantidad de clientes en distintos sectores, su rol y palabras clave asignadas. La información de cada cluster contiene palabras clave representativas. Para cada cluster, determina si la licitación es relevante para el perfil del usuario. Responde únicamente con 'true' o 'false' en el formato 'Cluster <id>: true' o 'Cluster <id>: false'."
	
	- Maneja reintentos en caso de errores (e.j, límites de tasa o fallos de red).
	
	- Guarda los resultados en un archivo JSON (e.j, consulta_priorizacion_resultados.json).
	
- Propósito: Clasifica clusters como relevantes (true) o no relevantes (false) para alimentar el módulo "Licitaciones Priorizadas".
- Notas: Requiere credenciales de AWS configuradas y el paquete boto3 (en tu requirements.txt).

### 5-. licitaciones_priorizadas_bd

- Descripción: Puebla la tabla UsuarioLicitacionPrioridad con los resultados de priorización y respalda los archivos procesados.

- Funcionamiento:

	1-. Lee el archivo JSON generado por consulta_priorizacion (e.j, consulta_priorizacion_resultados.json).
	
	2-. Para cada cluster marcado como true, asocia las licitaciones correspondientes al usuario en la tabla UsuarioLicitacionPrioridad.
	
	3-. Mueve el archivo JSON a una carpeta de respaldos (e.j, backups/) con una marca temporal.

- Propósito: Actualiza la base de datos para reflejar las licitaciones priorizadas en el módulo correspondiente.
- Notas: Asegura que la tabla UsuarioLicitacionPrioridad esté correctamente definida en los modelos de Django.

### 6-. archivar_licitaciones

- Descripción: Archiva licitaciones, ítems y priorizaciones del día anterior (o un día específico).

- Funcionamiento:

	1-. Identifica licitaciones generales y priorizadas del día anterior (o fecha especificada).
	
	2-. Mueve los registros a tablas de archivo (e.j, LicitacionesArchivadas) o marca como archivados en la base de datos.
	
	3-. Incluye ítems relacionados y datos de priorización.

- Propósito: Mantiene el módulo "Licitaciones Archivadas" actualizado y libera espacio en las tablas activas.
- Notas: Puede incluir un parámetro opcional para especificar la fecha de archivo (e.j, python archivar_licitaciones.py --date 2025-03-20).
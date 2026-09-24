# ======================= #
#   DATOS PREDEFINIDOS    #
# ======================= #

# Lista de sectores predefinidos, se usarán para poblar la tabla Sector
TIPO_SECTOR_CHOICES = [
    ('tecnologia', 'Tecnología y Comunicaciones'),
    ('salud', 'Salud y Servicios Médicos'),
    ('finanzas', 'Finanzas y Seguros'),
    ('manufactura', 'Manufactura y Producción'),
    ('retail', 'Retail y Comercio Minorista'),
    ('alimentacion', 'Alimentación y Bebidas'),
    ('construccion', 'Construcción e Inmobiliaria'),
    ('transporte', 'Transporte y Logística'),
    ('energia', 'Energía y Recursos Naturales'),
    ('agricultura', 'Agricultura y Agroindustria'),
    ('educacion', 'Educación y Formación'),
    ('turismo', 'Turismo y Hostelería'),
    ('consultoria', 'Servicios Profesionales y Consultoría'),
    ('medios', 'Medios de Comunicación y Entretenimiento'),
    ('automotriz', 'Industria Automotriz'),
    ('quimica', 'Química y Petroquímica'),
    ('aeronautica', 'Aeronáutica y Aeroespacial'),
    ('deportes', 'Deportes y Recreación'),
    ('arte', 'Arte y Cultura'),
    ('farmaceutico', 'Farmacéutico'),
    ('mineria', 'Minería'),
    ('telecomunicaciones', 'Telecomunicaciones'),
    ('ambiental', 'Ambiental y Sostenibilidad'),
    ('biotecnologia', 'Biotecnología'),
    ('logistica', 'Logística'),
    ('seguridad', 'Seguridad y Defensa'),
    ('inmobiliario', 'Inmobiliario'),
    ('publicidad', 'Publicidad y Marketing'),
    ('servicios', 'Servicios Generales'),
    ('investigacion', 'Investigación y Desarrollo'),
    ('otro', 'Otros'),
]

# Lista de categorías realistas para cada admin
possible_categories = [
    "Finanzas", "Marketing", "Gerencia General", "Tecnología", "Logística", "Recursos Humanos",
    "Salud", "Manufactura", "Retail", "Alimentación", "Construcción", "Transporte", "Energía",
    "Agricultura", "Educación", "Turismo", "Consultoría", "Medios", "Automotriz", "Química",
    "Aeronáutica", "Deportes", "Arte", "Farmacéutico", "Minería", "Telecomunicaciones",
    "Ambiental", "Biotecnología", "Seguridad", "Inmobiliario", "Publicidad", "Servicios", "Investigación"
]

# Mapeo de roles para cada categoría (comienza vacío; complétalo según necesites)
category_roles_map = {
    "Finanzas": [
         "Analista Financiero", "Gerente Financiero", "Auditor Interno",
         "Contador Senior", "Asesor de Inversiones"
    ],
    "Marketing": [
         "Gerente de Marketing", "Especialista en Marketing Digital", "Coordinador de Publicidad",
         "Analista de Mercado", "Estratega de Contenido"
    ],
    "Gerencia General": [
         "Gerente General", "Director Ejecutivo", "Subgerente", "Director de Operaciones"
    ],
    "Tecnología": [
         "Técnico Informático", "Desarrollador de Software", "Arquitecto de Soluciones",
         "Administrador de Sistemas", "Ingeniero de Datos"
    ],
    "Logística": [
         "Encargado de Logística", "Coordinador de Transporte", "Supervisor de Almacén",
         "Planificador Logístico", "Jefe de Distribución"
    ],
    "Recursos Humanos": [
         "Jefe de Recursos Humanos", "Analista de RRHH", "Coordinador de Talento",
         "Especialista en Compensaciones", "Gestor de Capacitación"
    ],
    "Salud": [
         "Gerente de Salud", "Coordinador de Servicios Médicos", "Administrador Hospitalario",
         "Director Clínico", "Especialista en Calidad"
    ],
    "Manufactura": [
         "Ingeniero de Producción", "Supervisor de Planta", "Jefe de Mantenimiento",
         "Analista de Calidad", "Planificador de Producción"
    ],
    "Retail": [
         "Gerente de Tienda", "Coordinador de Ventas", "Especialista en Merchandising",
         "Analista de Inventario", "Jefe de Operaciones Retail"
    ],
    "Alimentación": [
         "Gerente de Alimentos", "Supervisor de Producción", "Controlador de Calidad",
         "Planificador de Distribución de Alimentos"
    ],
    "Construcción": [
         "Ingeniero Civil", "Gerente de Proyectos", "Supervisor de Obra",
         "Coordinador de Seguridad", "Arquitecto de Proyectos"
    ],
    "Transporte": [
         "Gerente de Transporte", "Coordinador de Rutas", "Supervisor de Flota",
         "Planificador de Transporte"
    ],
    "Energía": [
         "Ingeniero de Energía", "Supervisor de Mantenimiento", "Analista de Eficiencia Energética",
         "Técnico en Energía"
    ],
    "Agricultura": [
         "Agrónomo", "Gerente Agrícola", "Técnico en Cultivos", "Especialista en Agroindustria"
    ],
    "Educación": [
         "Director Académico", "Coordinador Pedagógico", "Asesor Educativo", "Jefe de Institución Educativa"
    ],
    "Turismo": [
         "Gerente de Turismo", "Coordinador de Eventos", "Especialista en Operaciones Turísticas",
         "Agente de Viajes"
    ],
    "Consultoría": [
         "Consultor Estratégico", "Analista de Gestión", "Especialista en Transformación Digital",
         "Asesor Empresarial"
    ],
    "Medios": [
         "Productor de Medios", "Director de Contenido", "Especialista en Comunicación",
         "Gestor de Redes Sociales"
    ],
    "Automotriz": [
         "Gerente de Concesionario", "Técnico Automotriz", "Asesor de Ventas de Vehículos",
         "Especialista en Servicio Técnico"
    ],
    "Química": [
         "Ingeniero Químico", "Técnico de Laboratorio", "Gerente de Producción Química",
         "Analista de Procesos Químicos"
    ],
    "Aeronáutica": [
         "Ingeniero Aeronáutico", "Técnico en Mantenimiento Aeronáutico",
         "Coordinador de Operaciones de Vuelo", "Especialista en Seguridad Aérea"
    ],
    "Deportes": [
         "Gerente Deportivo", "Coordinador de Eventos Deportivos", "Especialista en Marketing Deportivo",
         "Entrenador Deportivo"
    ],
    "Arte": [
         "Curador de Arte", "Director de Galería", "Coordinador de Eventos Culturales",
         "Asesor Artístico"
    ],
    "Farmacéutico": [
         "Gerente de Farmacia", "Especialista en Regulación Farmacéutica", "Analista de Calidad Farmacéutica",
         "Asesor Farmacéutico"
    ],
    "Minería": [
         "Ingeniero de Minas", "Supervisor de Extracción", "Analista de Procesos Mineros",
         "Gerente de Operaciones Mineras"
    ],
    "Telecomunicaciones": [
         "Ingeniero de Telecomunicaciones", "Especialista en Redes", "Coordinador de Proyectos de Telecom",
         "Técnico en Comunicaciones"
    ],
    "Ambiental": [
         "Especialista en Medio Ambiente", "Gerente de Sostenibilidad", "Auditor Ambiental",
         "Asesor en Gestión Ambiental"
    ],
    "Biotecnología": [
         "Investigador en Biotecnología", "Gerente de I+D", "Especialista en Bioinformática",
         "Técnico en Bioprocesos"
    ],
    "Seguridad": [
         "Jefe de Seguridad", "Analista de Riesgos", "Coordinador de Seguridad", "Inspector de Seguridad"
    ],
    "Inmobiliario": [
         "Gerente Inmobiliario", "Asesor Inmobiliario", "Coordinador de Proyectos Inmobiliarios",
         "Consultor Inmobiliario"
    ],
    "Publicidad": [
         "Director de Publicidad", "Ejecutivo de Cuentas", "Planificador de Medios",
         "Estratega Creativo"
    ],
    "Servicios": [
         "Gerente de Servicios", "Coordinador de Operaciones de Servicios", "Analista de Calidad de Servicios",
         "Especialista en Atención al Cliente"
    ],
    "Investigación": [
         "Investigador Principal", "Analista de Datos", "Coordinador de Proyectos de Investigación",
         "Especialista en I+D"
    ]
}

# Lista de posibles palabras clave realistas (puedes completarla según necesites)
possible_keywords = [
    "construccion", "logistica", "recursos humanos", "farmacias", "quimica", "tecnologia",
    "innovacion", "finanzas", "marketing", "servicios", "educacion", "turismo", "inmobiliario",
    "publicidad", "investigacion", "ambiental", "salud", "manufactura", "agroindustria", "digital"
]

# Datos de clientes (lista de diccionarios; déjala vacía si lo deseas y se generarán clientes aleatorios)
sample_clients = [
    {
        "nombre_cliente": "TechNova Solutions",
        "rut_cliente": "17.395.678-9",
        "tipo_cliente": "empresa",
        "contacto_principal": "Ana López",
        "email": "contacto@technovasolutions.com",
        "sector": "tecnologia",
        "descripcion_rubro": "Empresa especializada en desarrollo de software y soluciones tecnológicas innovadoras.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Finanzas Seguras",
        "rut_cliente": "15.618.141-2",
        "tipo_cliente": "empresa",
        "contacto_principal": "Pedro Gómez",
        "email": "info@finanzasseguras.com",
        "sector": "finanzas",
        "descripcion_rubro": "Servicio financiero que ofrece seguros y asesoría patrimonial.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "EcoConstrucciones",
        "rut_cliente": "18.123.321-5",
        "tipo_cliente": "empresa",
        "contacto_principal": "María Fernández",
        "email": "ventas@ecoconstrucciones.com",
        "sector": "construccion",
        "descripcion_rubro": "Constructora enfocada en proyectos sostenibles e inmobiliarios ecológicos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Transporte Rápido",
        "rut_cliente": "20.395.654-7",
        "tipo_cliente": "empresa",
        "contacto_principal": "Juan Pérez",
        "email": "soporte@transportesrapidos.com",
        "sector": "transporte",
        "descripcion_rubro": "Logística y transporte de carga a nivel nacional e internacional.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Gourmet Delights",
        "rut_cliente": "23.761.129-0",
        "tipo_cliente": "empresa",
        "contacto_principal": "Sofía Martínez",
        "email": "contacto@gourmetdelights.com",
        "sector": "alimentacion",
        "descripcion_rubro": "Productora y distribuidora de alimentos gourmet y bebidas artesanales.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Energía Verde",
        "rut_cliente": "25.952.544-3",
        "tipo_cliente": "institucion",
        "contacto_principal": "Luis Torres",
        "email": "info@energiaverde.cl",
        "sector": "energia",
        "descripcion_rubro": "Institución dedicada a la generación de energía renovable y sostenible.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "AgroFuturo",
        "rut_cliente": "28.278.221-6",
        "tipo_cliente": "empresa",
        "contacto_principal": "Clara Sánchez",
        "email": "ventas@agrofuturo.com",
        "sector": "agricultura",
        "descripcion_rubro": "Agroindustria enfocada en cultivos orgánicos y exportación de productos agrícolas.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "EducaMás",
        "rut_cliente": "30.876.121-8",
        "tipo_cliente": "institucion",
        "contacto_principal": "Ricardo Díaz",
        "email": "contacto@educamas.cl",
        "sector": "educacion",
        "descripcion_rubro": "Institución educativa que ofrece formación técnica y profesional.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Viajes Épicos",
        "rut_cliente": "32.511.525-1",
        "tipo_cliente": "empresa",
        "contacto_principal": "Laura Gómez",
        "email": "reservas@viajepicos.com",
        "sector": "turismo",
        "descripcion_rubro": "Agencia de viajes especializada en turismo aventura y cultural.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Consultoría Estratégica",
        "rut_cliente": "35.511.941-4",
        "tipo_cliente": "empresa",
        "contacto_principal": "Felipe Rojas",
        "email": "info@consultoriaestrategica.cl",
        "sector": "consultoria",
        "descripcion_rubro": "Servicios de consultoría en estrategia empresarial y transformación digital.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "MediaVision",
        "rut_cliente": "38.412.739-9",
        "tipo_cliente": "empresa",
        "contacto_principal": "Beatriz Vega",
        "email": "contacto@mediavision.com",
        "sector": "medios",
        "descripcion_rubro": "Productora de contenido audiovisual y entretenimiento digital.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "AutoElite",
        "rut_cliente": "40.175.578-0",
        "tipo_cliente": "empresa",
        "contacto_principal": "Javier Morales",
        "email": "ventas@autoelite.cl",
        "sector": "automotriz",
        "descripcion_rubro": "Distribuidora de vehículos premium y servicios de mantenimiento automotriz.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "PharmaHealth",
        "rut_cliente": "42.164.012-3",
        "tipo_cliente": "institucion",
        "contacto_principal": "Patricia Orellana",
        "email": "info@pharmahealth.cl",
        "sector": "farmaceutico",
        "descripcion_rubro": "Laboratorio farmacéutico dedicado a la investigación y producción de medicamentos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Minera del Sur",
        "rut_cliente": "45.375.233-5",
        "tipo_cliente": "empresa",
        "contacto_principal": "Héctor González",
        "email": "contacto@mineradelsur.com",
        "sector": "mineria",
        "descripcion_rubro": "Compañía minera enfocada en la extracción de minerales y metales preciosos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "EcoLogística",
        "rut_cliente": "48.241.386-8",
        "tipo_cliente": "empresa",
        "contacto_principal": "Camila Muñoz",
        "email": "ventas@ecologistica.cl",
        "sector": "logistica",
        "descripcion_rubro": "Servicios de logística sostenible y distribución eficiente.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Salud Vital",
        "rut_cliente": "10.826.192-3",
        "tipo_cliente": "institucion",
        "contacto_principal": "Carlos Rivera",
        "email": "contacto@saludvital.com",
        "sector": "salud",
        "descripcion_rubro": "Institución dedicada a servicios médicos integrales.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Construir S.A.",
        "rut_cliente": "13.275.585-6",
        "tipo_cliente": "empresa",
        "contacto_principal": "Laura Sánchez",
        "email": "info@construir.com",
        "sector": "construccion",
        "descripcion_rubro": "Empresa constructora con proyectos residenciales y comerciales.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "TecuTech Ltda.",
        "rut_cliente": "11.164.233-4",
        "tipo_cliente": "empresa",
        "contacto_principal": "Jose Alberto López",
        "email": "info@tecutech.com",
        "sector": "tecnologia",
        "descripcion_rubro": "Desarrolla soluciones innovadoras en software.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Minería del Norte",
        "rut_cliente": "29.060.111-2",
        "tipo_cliente": "empresa",
        "contacto_principal": "Esteban Vargas",
        "email": "contacto@mineriadelnorte.com",
        "sector": "mineria",
        "descripcion_rubro": "Empresa dedicada a la extracción y comercialización de minerales.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "RetailMax",
        "rut_cliente": "18.999.070-1",
        "tipo_cliente": "empresa",
        "contacto_principal": "Diego Ramírez",
        "email": "ventas@retailmax.com",
        "sector": "retail",
        "descripcion_rubro": "Cadena de tiendas minoristas y distribución.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "AgroPlus",
        "rut_cliente": "17.818.999-0",
        "tipo_cliente": "empresa",
        "contacto_principal": "Ana Pérez",
        "email": "contacto@agroplus.com",
        "sector": "agricultura",
        "descripcion_rubro": "Innovaciones en agroindustria y distribución agrícola.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Turismo Global",
        "rut_cliente": "20.131.222-3",
        "tipo_cliente": "empresa",
        "contacto_principal": "Roberto Castillo",
        "email": "contacto@turismoglobal.com",
        "sector": "turismo",
        "descripcion_rubro": "Agencia de viajes y organización de eventos turísticos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Consultoría Pro",
        "rut_cliente": "21.242.333-4",
        "tipo_cliente": "empresa",
        "contacto_principal": "Verónica Díaz",
        "email": "info@consultoriapro.com",
        "sector": "consultoria",
        "descripcion_rubro": "Consultoría en estrategia y gestión empresarial.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Medios Impacto",
        "rut_cliente": "22.733.444-5",
        "tipo_cliente": "empresa",
        "contacto_principal": "Fernando Ruiz",
        "email": "contacto@mediosimpacto.com",
        "sector": "medios",
        "descripcion_rubro": "Productora y distribuidora de contenido multimedia.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "AutoMundo",
        "rut_cliente": "23.449.555-6",
        "tipo_cliente": "empresa",
        "contacto_principal": "Ricardo Fernández",
        "email": "ventas@automundo.com",
        "sector": "automotriz",
        "descripcion_rubro": "Distribuidora y concesionaria de vehículos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Quimica Nova",
        "rut_cliente": "24.585.666-7",
        "tipo_cliente": "empresa",
        "contacto_principal": "Patricia Morales",
        "email": "info@quimicanova.com",
        "sector": "quimica",
        "descripcion_rubro": "Fábrica de productos químicos y petroquímicos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "AeroEspacio",
        "rut_cliente": "25.616.777-8",
        "tipo_cliente": "institucion",
        "contacto_principal": "Eduardo López",
        "email": "contacto@aeroespacio.com",
        "sector": "aeronautica",
        "descripcion_rubro": "Institución dedicada a la investigación aeroespacial.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Deporte Total",
        "rut_cliente": "26.737.888-9",
        "tipo_cliente": "empresa",
        "contacto_principal": "Gabriela Jiménez",
        "email": "ventas@deportetotal.com",
        "sector": "deportes",
        "descripcion_rubro": "Tienda y distribución de artículos deportivos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "ArteVivo",
        "rut_cliente": "27.888.994-0",
        "tipo_cliente": "individual",
        "contacto_principal": "Luis Martínez",
        "email": "contacto@artevivo.com",
        "sector": "arte",
        "descripcion_rubro": "Galería y producción de arte contemporáneo.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Farmacéutica Vida",
        "rut_cliente": "28.199.000-1",
        "tipo_cliente": "empresa",
        "contacto_principal": "Claudia Rojas",
        "email": "info@farmavida.com",
        "sector": "salud",
        "descripcion_rubro": "Desarrollo y distribución de productos farmacéuticos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Ejemplo S.A.",
        "rut_cliente": "12.345.678-9",
        "tipo_cliente": "empresa",
        "contacto_principal": "Alberto Delgado",
        "email": "contacto@ejemplo.com",
        "sector": "tecnologia",
        "descripcion_rubro": "Empresa dedicada a la innovación tecnológica.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "InnovaTech Ltda.",
        "rut_cliente": "11.212.333-4",
        "tipo_cliente": "empresa",
        "contacto_principal": "Mariana López",
        "email": "info@innovatech.com",
        "sector": "tecnologia",
        "descripcion_rubro": "Desarrolla soluciones innovadoras en software.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Salud Vital",
        "rut_cliente": "10.981.657-3",
        "tipo_cliente": "institucion",
        "contacto_principal": "Carlos Rivera",
        "email": "contacto@saludvital.com",
        "sector": "salud",
        "descripcion_rubro": "Institución dedicada a servicios médicos integrales.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Construir S.A.",
        "rut_cliente": "13.534.555-6",
        "tipo_cliente": "empresa",
        "contacto_principal": "Laura Sánchez",
        "email": "info@construir.com",
        "sector": "construccion",
        "descripcion_rubro": "Empresa constructora con proyectos residenciales y comerciales.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Alimentos del Sur",
        "rut_cliente": "14.555.856-7",
        "tipo_cliente": "empresa",
        "contacto_principal": "José Martínez",
        "email": "ventas@alimentosdelsur.com",
        "sector": "alimentacion",
        "descripcion_rubro": "Productora y distribuidora de alimentos frescos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Transporte Rápido",
        "rut_cliente": "15.116.777-8",
        "tipo_cliente": "empresa",
        "contacto_principal": "Sofía Gómez",
        "email": "contacto@transporterapido.com",
        "sector": "transporte",
        "descripcion_rubro": "Servicios de transporte y logística.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "EcoEnergía",
        "rut_cliente": "16.567.888-9",
        "tipo_cliente": "empresa",
        "contacto_principal": "Miguel Torres",
        "email": "info@ecoenergia.com",
        "sector": "energia",
        "descripcion_rubro": "Genera y distribuye energía renovable.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "AgroPlus",
        "rut_cliente": "17.888.119-0",
        "tipo_cliente": "empresa",
        "contacto_principal": "Ana Pérez",
        "email": "contacto@agroplus.com",
        "sector": "agricultura",
        "descripcion_rubro": "Innovaciones en agroindustria y distribución agrícola.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "RetailMax",
        "rut_cliente": "18.599.000-1",
        "tipo_cliente": "empresa",
        "contacto_principal": "Diego Ramírez",
        "email": "ventas@retailmax.com",
        "sector": "retail",
        "descripcion_rubro": "Cadena de tiendas minoristas y distribución.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "EducAcción",
        "rut_cliente": "19.060.111-2",
        "tipo_cliente": "institucion",
        "contacto_principal": "Isabel Mendoza",
        "email": "info@educaccion.com",
        "sector": "educacion",
        "descripcion_rubro": "Institución educativa con programas de formación continua.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Turismo Global",
        "rut_cliente": "20.179.222-3",
        "tipo_cliente": "empresa",
        "contacto_principal": "Roberto Castillo",
        "email": "contacto@turismoglobal.com",
        "sector": "turismo",
        "descripcion_rubro": "Agencia de viajes y organización de eventos turísticos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Consultoría Pro",
        "rut_cliente": "21.202.333-4",
        "tipo_cliente": "empresa",
        "contacto_principal": "Verónica Díaz",
        "email": "info@consultoriapro.com",
        "sector": "consultoria",
        "descripcion_rubro": "Consultoría en estrategia y gestión empresarial.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Medios Impacto",
        "rut_cliente": "22.319.444-5",
        "tipo_cliente": "empresa",
        "contacto_principal": "Fernando Ruiz",
        "email": "contacto@mediosimpacto.com",
        "sector": "medios",
        "descripcion_rubro": "Productora y distribuidora de contenido multimedia.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "AutoMundo",
        "rut_cliente": "23.958.555-6",
        "tipo_cliente": "empresa",
        "contacto_principal": "Ricardo Fernández",
        "email": "ventas@automundo.com",
        "sector": "automotriz",
        "descripcion_rubro": "Distribuidora y concesionaria de vehículos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Quimica Nova",
        "rut_cliente": "24.152.666-7",
        "tipo_cliente": "empresa",
        "contacto_principal": "Patricia Morales",
        "email": "info@quimicanova.com",
        "sector": "quimica",
        "descripcion_rubro": "Fábrica de productos químicos y petroquímicos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "AeroEspacio",
        "rut_cliente": "25.126.777-8",
        "tipo_cliente": "institucion",
        "contacto_principal": "Eduardo López",
        "email": "contacto@aeroespacio.com",
        "sector": "aeronautica",
        "descripcion_rubro": "Institución dedicada a la investigación aeroespacial.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Deporte Total",
        "rut_cliente": "26.337.888-9",
        "tipo_cliente": "empresa",
        "contacto_principal": "Gabriela Jiménez",
        "email": "ventas@deportetotal.com",
        "sector": "deportes",
        "descripcion_rubro": "Tienda y distribución de artículos deportivos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "ArteVivo",
        "rut_cliente": "27.389.999-0",
        "tipo_cliente": "individual",
        "contacto_principal": "Luis Martínez",
        "email": "contacto@artevivo.com",
        "sector": "arte",
        "descripcion_rubro": "Galería y producción de arte contemporáneo.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Farmacéutica Vida",
        "rut_cliente": "28.159.000-1",
        "tipo_cliente": "empresa",
        "contacto_principal": "Claudia Rojas",
        "email": "info@farmavida.com",
        "sector": "salud",
        "descripcion_rubro": "Desarrollo y distribución de productos farmacéuticos.",
        "estado": "activo",
    },
    {
        "nombre_cliente": "Minería del Norte",
        "rut_cliente": "29.110.111-2",
        "tipo_cliente": "empresa",
        "contacto_principal": "Esteban Vargas",
        "email": "contacto@mineriadelnorte.com",
        "sector": "mineria",
        "descripcion_rubro": "Empresa dedicada a la extracción y comercialización de minerales.",
        "estado": "activo",
    },
]

# ======================= #
# DATOS PREDEFINIDOS FIN  #
# ======================= #

# ================================================================================================= #
#   python manage.py seed_data                                                                      #
#   python manage.py seed_data --num-admins 1 --users-per-admin 5 --clients-per-admin 40            #
#   python manage.py seed_data --num-admins 1 --users-per-admin 10 --clients-per-admin 40           #
#   python manage.py seed_data --num-admins 3 --users-per-admin 15 --clients-per-admin 50           #
# ================================================================================================= #

import random
from django.core.management.base import BaseCommand
from django.db import transaction

# Importa tus modelos (ajusta la ruta según tu proyecto)
from appone.models import (
    Usuario,
    CategoriaRol,
    Rol,
    PalabrasClave,
    Cliente,
    Sector,
)

# ======================= #
# VARIABLES CONFIGURABLES #
# ======================= #



# python manage.py generate_test_data

# Cantidad de elementos para cada sección
NUM_ADMIN_CATEGORIES = 8  # Categorías por admin
NUM_ADMIN_KEYWORDS = 5   # Palabras clave por admin

# Cantidad base de usuarios y clientes por admin (puedes ajustar estos valores)
BASE_USER_COUNT_PER_ADMIN = 10  # Usuarios por admin (puedes cambiarlo o pasarlo como argumento)
BASE_CLIENT_COUNT_PER_ADMIN = 30  # Clientes por admin (puedes cambiarlo o pasarlo como argumento)

class Command(BaseCommand):
    help = 'Genera datos de prueba realistas para superadmin, admins, usuarios, categorías, roles, palabras clave y clientes.'

    def add_arguments(self, parser):
        # Agregar argumento para especificar el número de administradores
        parser.add_argument(
            '--num-admins',
            type=int,
            default=1,
            help='Número de administradores a crear (por defecto 1)',
        )
        # Agregar argumentos opcionales para usuarios y clientes por admin
        parser.add_argument(
            '--users-per-admin',
            type=int,
            default=BASE_USER_COUNT_PER_ADMIN,
            help=f'Número de usuarios por admin (por defecto {BASE_USER_COUNT_PER_ADMIN})',
        )
        parser.add_argument(
            '--clients-per-admin',
            type=int,
            default=BASE_CLIENT_COUNT_PER_ADMIN,
            help=f'Número de clientes por admin (por defecto {BASE_CLIENT_COUNT_PER_ADMIN})',
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        num_admins = kwargs['num_admins']
        users_per_admin = kwargs['users_per_admin']
        clients_per_admin = kwargs['clients_per_admin']

        self.stdout.write(f"Iniciando la creación de datos de prueba con {num_admins} administradores...")

        # 0. Poblar la tabla Sector si está vacía.
        if Sector.objects.count() == 0:
            for codigo, descripcion in TIPO_SECTOR_CHOICES:
                Sector.objects.create(codigo=codigo, descripcion=descripcion)
            self.stdout.write(self.style.SUCCESS("Sectores poblados exitosamente."))
        else:
            self.stdout.write("La tabla Sector ya contiene datos.")

        # 1. Crear superadmin si no existe.
        if not Usuario.objects.filter(is_superuser=True).exists():
            superadmin = Usuario.objects.create_superuser(
                rut='00000000-0',
                nombre='Superadmin',
                email='superadmin@example.com',
                password='password'
            )
            self.stdout.write("Se creó el superadmin.")
        else:
            superadmin = Usuario.objects.filter(is_superuser=True).first()
            self.stdout.write("Ya existe un superadmin, se utilizará el existente.")

        # 2. Crear 'num_admins' admins con datos generados dinámicamente.
        admins = []  # Lista de tuplas: (admin, num_usuarios, num_clientes)
        for i in range(num_admins):
            rut = f"{11111111 + i}-{i}"  # Genera RUTs únicos (ejemplo: 11111111-0, 11111112-1, etc.)
            nombre = f"Admin {i + 1}"
            email = f"admin{i+1}@example.com"
            admin = Usuario.objects.create_user(
                rut=rut,
                nombre=nombre,
                email=email,
                password="password",
                is_staff=True,
                is_superuser=False,
            )
            admins.append((admin, users_per_admin, clients_per_admin))
        self.stdout.write(f"Se crearon {num_admins} admins.")

        # 3. Para cada admin: crear categorías, roles y palabras clave.
        for admin, num_users, num_clients in admins:
            categorias_seleccionadas = random.sample(possible_categories, NUM_ADMIN_CATEGORIES)
            categorias_obj = []
            for cat in categorias_seleccionadas:
                categoria = CategoriaRol.objects.create(
                    nombre_categoria=cat,
                    descripcion=f"Área de {cat}.",
                    creado_por=admin,
                )
                categorias_obj.append(categoria)
            self.stdout.write(f"Se crearon {NUM_ADMIN_CATEGORIES} categorías para {admin.nombre}.")

            for categoria in categorias_obj:
                roles_posibles = category_roles_map.get(categoria.nombre_categoria, ["Rol Genérico 1", "Rol Genérico 2"])
                for rol_nombre in roles_posibles:
                    Rol.objects.create(
                        nombre_rol=rol_nombre,
                        descripcion=f"{rol_nombre} en el área de {categoria.nombre_categoria}.",
                        categoria=categoria,
                        creado_por=admin,
                    )
            self.stdout.write(f"Se crearon roles para cada categoría de {admin.nombre}.")

            keywords = ", ".join(random.sample(possible_keywords, NUM_ADMIN_KEYWORDS))
            PalabrasClave.objects.create(
                admin=admin,
                keywords=keywords,
            )
            self.stdout.write(f"Se asignaron palabras clave a {admin.nombre}.")

        # 4. Para cada admin, crear usuarios asignados a ese admin.
        users_by_admin = {}  # clave: admin.pk, valor: lista de usuarios
        for admin, num_users, num_clients in admins:
            roles = list(Rol.objects.filter(creado_por=admin))
            usuarios = []
            for i in range(num_users):
                rut_usuario = f"{random.randint(10000000, 99999999)}-{i}"
                nombre_usuario = f"Usuario {i+1}"
                email_usuario = f"usuario_{i+1}@{admin.nombre.replace(' ', '').lower()}.com"
                usuario = Usuario.objects.create_user(
                    rut=rut_usuario,
                    nombre=nombre_usuario,
                    email=email_usuario,
                    password="password",
                    creado_por=admin,
                    is_staff=False,
                    is_superuser=False,
                )
                if roles:
                    usuario.rol = random.choice(roles)
                    usuario.save(update_fields=['rol'])
                usuarios.append(usuario)
            users_by_admin[admin.pk] = usuarios
            self.stdout.write(f"Se crearon {num_users} usuarios para {admin.nombre} (con roles asignados).")

        # 5. Para cada admin, crear clientes.
        for admin, num_users, num_clients in admins:
            all_sectores = list(Sector.objects.all())
            if not all_sectores:
                self.stdout.write(self.style.ERROR("No existen sectores en la base de datos. Aborto la creación de clientes."))
                continue

            for i in range(num_clients):
                if i < len(sample_clients):
                    data = sample_clients[i]
                    nombre_cliente = data["nombre_cliente"]
                    rut_cliente = data["rut_cliente"]
                    tipo_cliente = data["tipo_cliente"]
                    contacto_principal = data["contacto_principal"]
                    email_cliente = data["email"]
                    try:
                        sector_instance = Sector.objects.get(codigo=data["sector"])
                    except Sector.DoesNotExist:
                        sector_instance = random.choice(all_sectores)
                    descripcion_rubro = data["descripcion_rubro"]
                    estado = data["estado"]
                else:
                    sector_instance = random.choice(all_sectores)
                    sector_codigo = sector_instance.codigo
                    sector_desc = sector_instance.descripcion
                    nombre_cliente = f"Cliente {i+1} {sector_desc}"
                    rut_cliente = f"{random.randint(1000000, 9999999)}-{i}"
                    tipo_cliente = random.choice(["individual", "empresa", "institucion"])
                    contacto_principal = f"Contacto {i+1}"
                    email_cliente = f"cliente_{i+1}@{sector_codigo}.com"
                    descripcion_rubro = f"Empresa dedicada al sector {sector_desc}."
                    estado = "activo"
                cliente = Cliente.objects.create(
                    nombre_cliente=nombre_cliente,
                    rut_cliente=rut_cliente,
                    tipo_cliente=tipo_cliente,
                    contacto_principal=contacto_principal,
                    email=email_cliente,
                    sector=sector_instance,
                    descripcion_rubro=descripcion_rubro,
                    estado=estado,
                    creado_por=admin,
                )
                usuarios = users_by_admin.get(admin.pk, [])
                if usuarios:
                    num_asignados = random.randint(1, min(3, len(usuarios)))
                    asignados = random.sample(usuarios, num_asignados)
                    cliente.asignado_a.set(asignados)
            self.stdout.write(f"Se crearon {num_clients} clientes para {admin.nombre}.")

        self.stdout.write(self.style.SUCCESS("Datos de prueba generados correctamente."))
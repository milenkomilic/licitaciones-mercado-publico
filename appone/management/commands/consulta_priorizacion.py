import os
import json
import time
import sys
import botocore
import boto3
import tiktoken

from django.core.management.base import BaseCommand
from django.conf import settings
from appone.models import Sector

# Configuración para tiempos de espera y reintentos
TIEMPO_INICIAL_ESPERA = 30  # segundos
REINTENTOS_MAXIMOS = 10
MULTIPLICADOR_BACKOFF = 2

# --- CONSTANTES DE TAMAÑO DE PROMPT ---
MIN_QUERY_TOKENS = 3000
MAX_QUERY_TOKENS = 4000

config = botocore.config.Config(read_timeout=360, connect_timeout=60, retries={"max_attempts": 0})

# Configuración de AWS Bedrock
bedrock_runtime = boto3.client(
    "bedrock-runtime",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    config=config
)

# Configuración de tiktoken
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(texto):
    """Cuenta los tokens del texto usando tiktoken."""
    return len(encoding.encode(texto))

# >>> NUEVO <<<
# Contexto de la tarea en español (se reenvía cada 30000 tokens o en el primer batch)
TAREA_CONTEXT = (
    "Eres una IA encargada de evaluar la relevancia de clusters de licitaciones en función del perfil de un usuario. "
    "El perfil del usuario indica la cantidad de clientes en distintos sectores, su rol y palabras clave asignadas. "
    "La información de cada cluster contiene palabras clave representativas. Para cada cluster, determina si la licitación "
    "es relevante para el perfil del usuario. Responde únicamente con 'true' o 'false' en el formato 'Cluster <id>: true' o 'Cluster <id>: false'."
)

# --- Extracción de sectores desde la base de datos ---
try:
    sectores = Sector.objects.all()
except Exception as e:
    print("Error al obtener los sectores desde la base de datos:", e)
    sys.exit(1)

SECTOR_ID_MAP = {sector.codigo.lower().strip(): sector.id for sector in sectores}
ID_SECTOR_MAP = {str(sector.id): (sector.codigo, sector.descripcion) for sector in sectores}

# >>> NUEVO <<<
# Generamos un texto explicativo de los rubros con su identificador:
RUBROS_CONTEXT = "Rubro y su identificador asociado:\n"
for sector_id, (codigo, descripcion) in ID_SECTOR_MAP.items():
    RUBROS_CONTEXT += f"ID {sector_id}: {descripcion} (Código: {codigo})\n"

# --- Funciones para generar textos en español ---

def get_full_profile_text(user_data):
    """
    Convierte la información del usuario en un texto descriptivo en español.
    Incluye el rol (r), las palabras clave del admin (k_admin), las del usuario (k_usuario)
    y el perfil de clientes por sector (p). En este texto se usan solo los IDs de sector.
    """
    profile = user_data.get("p", {})
    role = user_data.get("r", "")
    keywords_admin = user_data.get("k_admin", [])
    keywords_usuario = user_data.get("k_usuario", [])
    partes = []

    if role:
        partes.append(f"Rol del usuario: {role}.")

    if keywords_admin:
        partes.append("Palabras clave del administrador: " + ", ".join(keywords_admin) + ".")

    if keywords_usuario:
        partes.append("Palabras clave del usuario: " + ", ".join(keywords_usuario) + ".")

    if profile:
        partes_sector = []
        for sector_id, cantidad in profile.items():
            # Aquí se muestran solo los IDs, para no repetir nombres en cada batch
            partes_sector.append(f"Sector {sector_id}: {cantidad}")
        partes.append("Clientes por sector: " + ", ".join(partes_sector) + ".")

    return " ".join(partes)

def get_cluster_text(cluster):
    """
    Convierte la información de un cluster (se espera la clave 'rkw' para palabras clave)
    en un texto descriptivo en español.
    """
    if "rkw" in cluster:
        return "Palabras clave representativas: " + ", ".join(cluster["rkw"]) + "."
    return ""

# >>> NUEVO <<<
# Función para construir el prompt
def build_prompt(profile_text, batch_clusters, tokens_desde_ultimo_contexto, first_batch=False):
    """
    Construye el prompt concatenando:
      - (Opcionalmente) el contexto de la tarea (TAREA_CONTEXT + RUBROS_CONTEXT)
      - El perfil del usuario
      - La lista de clusters (cada uno identificado por su cluster_id)
      - Instrucciones finales para la respuesta.

    Cada 30,000 tokens (o en el primer batch), se envía el contexto completo,
    incluyendo el texto explicativo de rubros.
    """
    partes_prompt = []

    # Si es el primer batch o han pasado más de 30,000 tokens desde el último envío de contexto,
    # agregamos tanto TAREA_CONTEXT como RUBROS_CONTEXT.
    if first_batch or tokens_desde_ultimo_contexto >= 30000:
        partes_prompt.append(TAREA_CONTEXT)
        partes_prompt.append(RUBROS_CONTEXT)

    partes_prompt.append("Perfil del usuario:")
    partes_prompt.append(profile_text)
    partes_prompt.append("Clusters:")

    for (clust, clust_text, _) in batch_clusters:
        cid = clust.get("cluster_id", "?")
        partes_prompt.append(f"Cluster {cid}: {clust_text}")

    partes_prompt.append(
        "Para cada cluster listado, determina si la licitación es relevante para el perfil del usuario. "
        "Responde en una nueva línea para cada cluster en el formato 'Cluster <id>: true' o 'Cluster <id>: false'. "
        "No incluyas explicaciones, comentarios o texto adicional."
    )

    return "\n".join(partes_prompt)

def pad_prompt_to_min_tokens(prompt, min_tokens):
    """
    Agrega líneas de 'relleno' al prompt hasta alcanzar al menos min_tokens.
    """
    linea_relleno = "\nSe proporciona contexto adicional para claridad."
    while count_tokens(prompt) < min_tokens:
        prompt += linea_relleno
    return prompt

def parse_response(response_text):
    """
    Parsea la respuesta del modelo. Se espera que la respuesta tenga líneas en el formato:
       Cluster <id>: true
       Cluster <id>: false
    Retorna un diccionario con {cluster_id: boolean}
    """
    resultados = {}
    for linea in response_text.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if linea.lower().startswith("cluster"):
            try:
                partes = linea.split(":", 1)
                if len(partes) != 2:
                    continue
                cluster_id_parte = partes[0].strip()  # Ejemplo: "Cluster 1"
                valor_parte = partes[1].strip().lower()
                _, cid = cluster_id_parte.split(maxsplit=1)
                if valor_parte == "true":
                    resultados[cid] = True
                elif valor_parte == "false":
                    resultados[cid] = False
            except Exception:
                continue
    return resultados

def get_mistral_response(prompt):
    """
    Consulta al modelo Mistral 7B Instruct usando AWS Bedrock.
    Se ajusta el body de la consulta y se realizan reintentos ante errores o limitaciones.
    """
    body = json.dumps({
        "prompt": f"<s>[INST] {prompt} [/INST>",
        "max_tokens": 4000,
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 50
    })
    kwargs = {
        "modelId": "mistral.mistral-7b-instruct-v0:2",
        "contentType": "application/json",
        "accept": "application/json",
        "body": body,
    }
    espera = TIEMPO_INICIAL_ESPERA
    for intento in range(REINTENTOS_MAXIMOS):
        try:
            response = bedrock_runtime.invoke_model(**kwargs)
            resp_body = json.loads(response['body'].read())
            print("DEBUG: Respuesta completa:", json.dumps(resp_body, indent=2))
            # Buscar distintos campos posibles en la respuesta
            if "outputs" in resp_body and isinstance(resp_body["outputs"], list) and len(resp_body["outputs"]) > 0:
                output = resp_body["outputs"][0]
                if "text" in output:
                    return output["text"]
            elif "generated_text" in resp_body:
                return resp_body["generated_text"]
            elif "outputText" in resp_body:
                return resp_body["outputText"]
            elif "text" in resp_body:
                return resp_body["text"]
            else:
                raise ValueError("Formato de respuesta inesperado: no se encontró una clave de texto reconocida.")
        except botocore.exceptions.ClientError as e:
            if "ThrottlingException" in str(e):
                print(f"Advertencia: Límite de consultas alcanzado. Reintentando en {espera} segundos...")
                time.sleep(espera)
                espera *= MULTIPLICADOR_BACKOFF
            else:
                print("Error al consultar el modelo Mistral:", e)
                sys.exit(1)
        except Exception as ex:
            print("Error procesando la respuesta de Mistral:", ex)
            sys.exit(1)
    print("ERROR CRÍTICO: No se pudo obtener respuesta tras múltiples reintentos.")
    sys.exit(1)

class Command(BaseCommand):
    help = (
        "Consulta y prioriza oportunidades de licitación para cada usuario usando perfiles compactos y clusters de palabras clave. "
        "Para cada usuario, se envía el perfil (incluyendo rol y palabras clave) y los clusters en consultas por lotes al modelo Mistral 7B Instruct, "
        "asegurando que cada consulta tenga entre 7000 y 8000 tokens y que ningún cluster se corte. "
        "El modelo responde con un mapeo de cada código de licitación a true/false según su relevancia."
    )

    def add_arguments(self, parser):
        base_dir = os.path.join(os.path.dirname(__file__), "data")
        parser.add_argument(
            '--perfiles',
            type=str,
            default=os.path.join(base_dir, "profiles_clientes_usuario.json"),
            help="Ruta al archivo JSON (newline-delimited) con los perfiles compactos de los usuarios."
        )
        parser.add_argument(
            '--clusters',
            type=str,
            default=os.path.join(base_dir, "keywords_licitaciones.json"),
            help="Ruta al archivo JSON con los clusters de licitaciones (palabras clave)."
        )
        parser.add_argument(
            '--salida',
            type=str,
            default=os.path.join(base_dir, "consulta_priorizacion_resultados.json"),
            help="Ruta del archivo de salida para los resultados de la consulta."
        )
        parser.add_argument(
            '--limit_users',
            type=int,
            default=0,
            help="Si se establece, solo se utilizarán los primeros N usuarios."
        )
        parser.add_argument(
            '--limit_clusters',
            type=int,
            default=0,
            help="Si se establece, solo se utilizarán los primeros N clusters."
        )

    def handle(self, *args, **options):
        perfiles_path = options['perfiles']
        clusters_path = options['clusters']
        salida = options['salida']
        limit_users = options['limit_users']
        limit_clusters = options['limit_clusters']

        # Leer el archivo de perfiles (newline-delimited JSON)
        try:
            perfiles = {}
            with open(perfiles_path, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea:
                        perfiles.update(json.loads(linea))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al leer el archivo de perfiles: {e}"))
            sys.exit(1)

        # Leer el archivo de clusters (palabras clave de licitaciones)
        try:
            with open(clusters_path, 'r', encoding='utf-8') as f:
                try:
                    clusters_data = json.load(f)
                except json.JSONDecodeError:
                    # Posible caso de JSON newline-delimited
                    f.seek(0)
                    clusters_data = [json.loads(linea) for linea in f if linea.strip()]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al leer el archivo de clusters: {e}"))
            sys.exit(1)

        # Si clusters_data es un diccionario, convertirlo a lista
        if isinstance(clusters_data, dict):
            clusters_list = []
            for cluster_id, data in clusters_data.items():
                data["cluster_id"] = cluster_id
                clusters_list.append(data)
            clusters_data = clusters_list

        # Limitar clusters para pruebas si se especifica
        if limit_clusters and isinstance(clusters_data, list):
            clusters_data = clusters_data[:limit_clusters]

        # Limitar usuarios para pruebas si se especifica
        if limit_users:
            perfiles = dict(list(perfiles.items())[:limit_users])

        resultados = {}

        # Procesar cada usuario
        for user_id, user_data in perfiles.items():
            profile_text = get_full_profile_text(user_data)
            profile_tokens = count_tokens(profile_text)
            self.stdout.write(f"Generando consulta para el usuario {user_id} con perfil ({profile_tokens} tokens)...")
            self.stdout.write(f"Perfil del usuario {user_id}: {profile_text}")

            # Se verifica que exista información en el perfil (p) para procesar clusters
            perfil = user_data.get("p", {})
            if not perfil:
                # No tiene sectores asignados, se omite
                continue

            resultados[user_id] = {}
            total_tokens_usuario = profile_tokens
            tokens_desde_contexto = 0  # Controla cuándo reenviar el contexto completo
            first_batch = True

            batch_clusters = []  # Lista de tuplas: (cluster, texto_cluster, tokens_cluster)

            # Iterar sobre los clusters y agruparlos sin cortar ninguno
            for cluster in clusters_data:
                cluster_text = get_cluster_text(cluster)
                if not cluster_text:
                    continue
                cluster_tokens = count_tokens(cluster_text)

                # Preparar un batch candidato sumando el cluster actual
                candidate_batch = batch_clusters + [(cluster, cluster_text, cluster_tokens)]
                candidate_prompt = build_prompt(profile_text, candidate_batch, tokens_desde_contexto, first_batch=first_batch)

                if count_tokens(candidate_prompt) <= MAX_QUERY_TOKENS:
                    # Se puede agregar el cluster sin superar el límite
                    batch_clusters.append((cluster, cluster_text, cluster_tokens))
                else:
                    # Enviar el batch actual (si no está vacío)
                    if batch_clusters:
                        prompt = build_prompt(profile_text, batch_clusters, tokens_desde_contexto, first_batch=first_batch)
                        prompt = pad_prompt_to_min_tokens(prompt, MIN_QUERY_TOKENS)
                        prompt_tokens = count_tokens(prompt)
                        self.stdout.write(
                            f"Enviando consulta (tokens: {prompt_tokens}) para el usuario {user_id} "
                            f"con {len(batch_clusters)} clusters..."
                        )
                        response_text = get_mistral_response(prompt)
                        self.stdout.write(f"Respuesta: {response_text}")
                        batch_results = parse_response(response_text)
                        for (clust, _, _) in batch_clusters:
                            cid = clust.get("cluster_id", None)
                            if cid in batch_results:
                                relevancia = batch_results[cid]
                                for lic_code in clust.get("lic", []):
                                    resultados[user_id][lic_code] = relevancia

                        total_tokens_usuario += prompt_tokens
                        tokens_desde_contexto += prompt_tokens
                        if tokens_desde_contexto >= 30000:
                            tokens_desde_contexto = 0
                        time.sleep(TIEMPO_INICIAL_ESPERA)
                        first_batch = False
                        batch_clusters = []

                    # Ahora, intentar agregar el cluster en un nuevo batch
                    candidate_prompt = build_prompt(profile_text, [(cluster, cluster_text, cluster_tokens)],
                                                    tokens_desde_contexto, first_batch=first_batch)
                    if count_tokens(candidate_prompt) <= MAX_QUERY_TOKENS:
                        batch_clusters.append((cluster, cluster_text, cluster_tokens))
                    else:
                        # Si el cluster individual excede el límite, se envía de todas formas en un batch propio
                        batch_clusters.append((cluster, cluster_text, cluster_tokens))
                        prompt = build_prompt(profile_text, batch_clusters, tokens_desde_contexto, first_batch=first_batch)
                        prompt = pad_prompt_to_min_tokens(prompt, MIN_QUERY_TOKENS)
                        prompt_tokens = count_tokens(prompt)
                        self.stdout.write(
                            f"Enviando consulta (tokens: {prompt_tokens}) para el usuario {user_id} "
                            f"con 1 cluster (muy extenso)..."
                        )
                        response_text = get_mistral_response(prompt)
                        self.stdout.write(f"Respuesta: {response_text}")
                        batch_results = parse_response(response_text)
                        for (clust, _, _) in batch_clusters:
                            cid = clust.get("cluster_id", None)
                            if cid in batch_results:
                                relevancia = batch_results[cid]
                                for lic_code in clust.get("lic", []):
                                    resultados[user_id][lic_code] = relevancia

                        total_tokens_usuario += prompt_tokens
                        tokens_desde_contexto += prompt_tokens
                        if tokens_desde_contexto >= 30000:
                            tokens_desde_contexto = 0
                        time.sleep(TIEMPO_INICIAL_ESPERA)
                        first_batch = False
                        batch_clusters = []

            # Procesar el batch final (si existe)
            if batch_clusters:
                prompt = build_prompt(profile_text, batch_clusters, tokens_desde_contexto, first_batch=first_batch)
                prompt = pad_prompt_to_min_tokens(prompt, MIN_QUERY_TOKENS)
                prompt_tokens = count_tokens(prompt)
                self.stdout.write(
                    f"Enviando consulta final (tokens: {prompt_tokens}) para el usuario {user_id} "
                    f"con {len(batch_clusters)} clusters..."
                )
                response_text = get_mistral_response(prompt)
                self.stdout.write(f"Respuesta: {response_text}")
                batch_results = parse_response(response_text)
                for (clust, _, _) in batch_clusters:
                    cid = clust.get("cluster_id", None)
                    if cid in batch_results:
                        relevancia = batch_results[cid]
                        for lic_code in clust.get("lic", []):
                            resultados[user_id][lic_code] = relevancia

                total_tokens_usuario += prompt_tokens
                tokens_desde_contexto += prompt_tokens
                if tokens_desde_contexto >= 30000:
                    tokens_desde_contexto = 0
                time.sleep(TIEMPO_INICIAL_ESPERA)

            self.stdout.write(f"Total de tokens utilizados para el usuario {user_id}: {total_tokens_usuario}\n")

        # Guardar resultados en el archivo de salida
        directorio = os.path.dirname(salida)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
        try:
            with open(salida, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Resultados guardados en: {salida}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al escribir el archivo de salida: {e}"))

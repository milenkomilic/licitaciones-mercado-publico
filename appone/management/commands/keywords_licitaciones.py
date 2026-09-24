import json
import os
from django.core.management.base import BaseCommand
from appone.models import LicitacionDiaria
from rake_nltk import Rake
import nltk

# Descargar recursos necesarios para RAKE
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Importar librerías para vectorización y clustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
import numpy as np

class Command(BaseCommand):
    help = (
        "Extrae palabras clave de cada licitación, agrupa las licitaciones en clusters de forma dinámica "
        "(usando clustering jerárquico) según la similitud de keywords, y fuerza la fusión de clusters "
        "singleton (de 1 licitación) con el cluster más cercano, para reducir la cantidad total de clusters."
    )

    def add_arguments(self, parser):
        default_path = os.path.join(os.path.dirname(__file__), 'data', 'keywords_licitaciones.json')
        parser.add_argument(
            '--salida',
            type=str,
            default=default_path,
            help=f'Ruta del archivo JSON de salida. Por defecto: {default_path}'
        )
        parser.add_argument(
            '--num_keywords',
            type=int,
            default=10,
            help='Número máximo de palabras clave a extraer por licitación (por defecto 10).'
        )
        parser.add_argument(
            '--dist_threshold',
            type=float,
            default=0.7,
            help=('Umbral de distancia para formar clusters en el clustering jerárquico. '
                  'Licitaciones con distancia (1 - similitud coseno) menor a este valor se agruparán juntas. '
                  'Aumentar el valor permite clusters menos similares entre sí.')
        )

    def handle(self, *args, **options):
        ruta_salida = options['salida']
        num_keywords = options['num_keywords']
        dist_threshold = options['dist_threshold']

        self.stdout.write("Extrayendo licitaciones desde la base de datos...")
        licitaciones = LicitacionDiaria.objects.filter(codigo_estado=5)
        total_licitaciones = licitaciones.count()
        self.stdout.write(f"Se han encontrado {total_licitaciones} licitaciones publicadas (estado 5).")

        # Inicializamos RAKE (stopwords en español)
        rake_extractor = Rake(language="spanish")

        # Listas para almacenar los "documentos" y los códigos de licitación
        documentos = []
        codigos_licitaciones = []

        for lic in licitaciones:
            texto = f"{lic.nombre} {lic.descripcion} {lic.nombre_organismo}"
            rake_extractor.extract_keywords_from_text(texto)
            ranked_phrases = rake_extractor.get_ranked_phrases()
            keywords = ranked_phrases[:num_keywords]
            documentos.append(" ".join(keywords))
            codigos_licitaciones.append(lic.codigo_externo)
        self.stdout.write(self.style.SUCCESS(f"Total de licitaciones procesadas: {len(documentos)}"))

        if not documentos:
            self.stdout.write(self.style.ERROR("No se han encontrado licitaciones para procesar."))
            return

        # Vectorizamos los documentos usando TF-IDF
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documentos)

        # Calculamos la matriz de distancias (distancia coseno: 1 - similitud coseno)
        distance_matrix = cosine_distances(tfidf_matrix)

        # Aplicamos clustering jerárquico con AgglomerativeClustering
        self.stdout.write("Agrupando licitaciones en clusters con clustering jerárquico...")
        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric='precomputed',
            linkage='average',
            distance_threshold=dist_threshold
        )
        clusters = clustering.fit_predict(distance_matrix)

        # Creamos un mapeo: cluster_id -> lista de índices (índices en nuestros arrays originales)
        cluster_to_indices = {}
        for idx, cluster_id in enumerate(clusters):
            cluster_to_indices.setdefault(cluster_id, []).append(idx)

        # Post-procesamiento: Forzamos la fusión de clusters singleton.
        new_clusters = clusters.copy()
        for cluster_id, indices in cluster_to_indices.items():
            if len(indices) == 1:
                idx_singleton = indices[0]
                vector_singleton = tfidf_matrix[idx_singleton]
                best_cluster = None
                best_distance = float('inf')
                for other_cluster, other_indices in cluster_to_indices.items():
                    if other_cluster == cluster_id:
                        continue
                    distances = cosine_distances(vector_singleton, tfidf_matrix[other_indices])
                    avg_distance = np.mean(distances)
                    if avg_distance < best_distance:
                        best_distance = avg_distance
                        best_cluster = other_cluster
                if best_cluster is not None:
                    new_clusters[idx_singleton] = best_cluster

        # Reconstruir el mapeo con las nuevas asignaciones
        cluster_to_indices = {}
        for idx, cluster_id in enumerate(new_clusters):
            cluster_to_indices.setdefault(cluster_id, []).append(idx)

        # Construir la estructura final de clusters
        clusters_resultado = {}
        for cluster_id, indices in cluster_to_indices.items():
            label = str(cluster_id)
            clusters_resultado[label] = {
                "lic": [codigos_licitaciones[i] for i in indices],
                "documentos": [documentos[i] for i in indices]
            }

        # Generar resumen de keywords para cada cluster
        clusters_resumen = {}
        feature_names = np.array(vectorizer.get_feature_names_out())
        for label, data in clusters_resultado.items():
            indices = [codigos_licitaciones.index(codigo) for codigo in data["lic"]]
            submatrix = tfidf_matrix[indices]
            mean_tfidf = np.asarray(submatrix.mean(axis=0)).flatten()
            top_n = 10
            top_indices = mean_tfidf.argsort()[-top_n:][::-1]
            resumen_keywords = feature_names[top_indices].tolist()
            clusters_resumen[label] = {
                "lic": data["lic"],
                "rkw": resumen_keywords
            }
            self.stdout.write(
                f"Cluster {label}: {len(data['lic'])} licitaciones -> Keywords: {resumen_keywords}"
            )

        clusters_ordenados = dict(
            sorted(clusters_resumen.items(), key=lambda item: len(item[1]["lic"]), reverse=True)
        )

        clusters_final = {}
        for new_idx, (old_label, cluster_data) in enumerate(clusters_ordenados.items(), start=1):
            clusters_final[str(new_idx)] = cluster_data

        directorio = os.path.dirname(ruta_salida)
        if not os.path.exists(directorio):
            os.makedirs(directorio)

        try:
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                json.dump(clusters_final, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Conjuntos guardados en: {ruta_salida}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al escribir el archivo: {e}"))

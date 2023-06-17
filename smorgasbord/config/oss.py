from ..env import env


MINIO_ACCESS_KEY = env.str("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = env.str("MINIO_SECRET_KEY")
MINIO_HOST = env.str("MINIO_HOST")
MINIO_BUCKET = env.str("MINIO_BUCKET")

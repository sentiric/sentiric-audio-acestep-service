import os

class Settings:
    APP_VERSION = "1.0.0"
    ENV = os.getenv("ENV", "production")
    DEVICE = os.getenv("AUDIO_SERVICE_DEVICE", "cuda")
    # Facebook MusicGen (Küçük ve hızlı, 6GB VRAM'e rahat sığar)
    MODEL_ID = os.getenv("MUSIC_MODEL_ID", "facebook/musicgen-small") 
    
    HTTP_PORT = int(os.getenv("ACESTEP_SERVICE_HTTP_PORT", "16310"))
    GRPC_PORT = int(os.getenv("ACESTEP_SERVICE_GRPC_PORT", "16311"))
    
    GRPC_TLS_CA_PATH = os.getenv("GRPC_TLS_CA_PATH", "/sentiric-certificates/certs/ca.crt")
    CERT_PATH = os.getenv("ACESTEP_SERVICE_CERT_PATH", "/sentiric-certificates/certs/audio-acestep-service-chain.crt")
    KEY_PATH = os.getenv("ACESTEP_SERVICE_KEY_PATH", "/sentiric-certificates/certs/audio-acestep-service.key")

    S3_ENDPOINT = os.getenv("BUCKET_ENDPOINT_URL", "http://minio:9000")
    S3_ACCESS_KEY = os.getenv("BUCKET_ACCESS_KEY_ID", "sentiric")
    S3_SECRET_KEY = os.getenv("BUCKET_SECRET_ACCESS_KEY", "sentiric-secret-key")
    S3_BUCKET = os.getenv("BUCKET_NAME", "sentiric")
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://sentiric:sentiric_pass@rabbitmq:5672/%2f")

settings = Settings()

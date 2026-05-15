import torch, uuid, os, boto3, asyncio, structlog, aio_pika, scipy.io.wavfile
from transformers import AutoProcessor, MusicgenForConditionalGeneration
from botocore.config import Config
from app.core.config import settings
from sentiric.event.v1 import event_pb2
from google.protobuf.timestamp_pb2 import Timestamp

logger = structlog.get_logger()

class AudioEngine:
    def __init__(self):
        self.processor = None
        self.model = None
        self.s3 = boto3.client('s3', endpoint_url=settings.S3_ENDPOINT, aws_access_key_id=settings.S3_ACCESS_KEY, aws_secret_access_key=settings.S3_SECRET_KEY, config=Config(signature_version='s3v4'))

    def initialize(self):
        logger.info(f"Loading {settings.MODEL_ID}", event_id="MODEL_INIT")
        try:
            self.processor = AutoProcessor.from_pretrained(settings.MODEL_ID)
            self.model = MusicgenForConditionalGeneration.from_pretrained(settings.MODEL_ID).to(settings.DEVICE)
            logger.info("MusicGen Ready.", event_id="MODEL_READY")
        except Exception as e:
            logger.error(f"Load Fail: {e}", event_id="MODEL_INIT_FAIL")

    async def generate_async(self, prompt: str, duration: int, job_id: str, trace_id: str, tenant_id: str):
        logger.info("Generating music...", event_id="AUDIO_GEN_START", trace_id=trace_id)
        path = f"/tmp/{job_id}.wav"
        
        def render():
            inputs = self.processor(text=[prompt], padding=True, return_tensors="pt").to(settings.DEVICE)
            # max_new_tokens: duration(sec) * 50 (MusicGen approx tokens per sec)
            tokens = min(duration * 50, 1500)
            audio_values = self.model.generate(**inputs, max_new_tokens=tokens)
            sampling_rate = self.model.config.audio_encoder.sampling_rate
            scipy.io.wavfile.write(path, rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())
            
        try:
            await asyncio.to_thread(render)
            object_name = f"audio/{job_id}.wav"
            await asyncio.to_thread(self.s3.upload_file, path, settings.S3_BUCKET, object_name)
            os.remove(path)
            
            s3_uri = f"s3://{settings.S3_BUCKET}/{object_name}"
            logger.info("Audio uploaded", event_id="AUDIO_GEN_SUCCESS", trace_id=trace_id, uri=s3_uri)
            
            # Publish Event
            conn = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            async with conn:
                ch = await conn.channel()
                ex = await ch.declare_exchange("sentiric_events", aio_pika.ExchangeType.TOPIC, durable=True)
                ts = Timestamp(); ts.GetCurrentTime()
                evt = event_pb2.MediaGenerationCompletedEvent(event_type="media.generation.completed", trace_id=trace_id, job_id=job_id, tenant_id=tenant_id, media_type="music", success=True, result_uri=s3_uri, timestamp=ts)
                await ex.publish(aio_pika.Message(body=evt.SerializeToString(), content_type="application/protobuf", delivery_mode=aio_pika.DeliveryMode.PERSISTENT), routing_key="media.generation.completed")
                
        except Exception as e:
            logger.error(f"Render failed: {e}", event_id="AUDIO_GEN_FAIL", trace_id=trace_id)
        finally:
            if settings.DEVICE == "cuda":
                torch.cuda.empty_cache()

audio_engine = AudioEngine()

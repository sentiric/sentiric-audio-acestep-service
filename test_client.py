# test_client.py
import grpc
import os
import sys
import argparse
import time
import uuid
import random
from sentiric.audio_gen.v1 import gateway_pb2, gateway_pb2_grpc

# --- 🎵 PROFESYONEL MUSICGEN (ACE-STEP) YETENEK KATALOĞU ---
EXAMPLES = {
    "lofi": [
        {"p": "Lofi hip hop beat, smooth electric piano chords, dusty vinyl crackle, chill atmosphere, 80bpm", "d": 15},
        {"p": "Mellow jazz hop, warm bassline, rainy day window vibes, soft saxophone", "d": 20}
    ],
    "cinematic": [
        {"p": "Epic cinematic orchestral theme, heroic brass, powerful strings, hybrid electronic elements", "d": 15},
        {"p": "Tense thriller soundtrack, pulsing dark synths, ticking percussion, high stakes", "d": 12}
    ],
    "electronic": [
        {"p": "Cyberpunk synthwave, 80s analog synthesizers, fast driving arpeggio, neon city lights", "d": 15},
        {"p": "Deep melodic techno, hypnotic bassline, clean percussion, underground club vibe", "d": 20}
    ],
    "ambient": [
        {"p": "Deep space ambient, ethereal shimmering pads, no rhythm, vast and cold", "d": 25},
        {"p": "Meditative zen garden music, bamboo flute, soft water ripples, peaceful", "d": 30}
    ]
}

def send_job(stub, prompt, duration, tenant_id):
    trace_id = str(uuid.uuid4())
    request = gateway_pb2.SubmitAudioJobRequest(
        tenant_id=tenant_id,
        trace_id=trace_id,
        prompt=prompt,
        audio_type="music",
        duration_seconds=duration
    )
    
    print(f"📡 [TRACE: {trace_id[:8]}] Gönderiliyor: '{prompt[:60]}...' | Süre: {duration}s")
    try:
        start_time = time.time()
        response = stub.SubmitAudioJob(request)
        elapsed = time.time() - start_time
        if response.accepted:
            print(f"  ✅ KABUL EDİLDİ | Job ID: {response.job_id} | İletim: {elapsed:.2f}s")
    except grpc.RpcError as e:
        print(f"  🚨 gRPC HATASI: {e.code()} - {e.details()}")

def run_test():
    parser = argparse.ArgumentParser(description="Sentiric ACE-Step Music Test Suite")
    parser.add_argument("--prompt", type=str, help="Özel bir müzik açıklaması yazın")
    parser.add_argument("--duration", type=int, help="Müzik süresi (saniye)")
    parser.add_argument("--category", type=str, choices=list(EXAMPLES.keys()) + ["all"], help="Kategorideki tüm müzikleri test et")
    parser.add_argument("--stress", type=int, default=1, help="Stress testi sayısı")
    
    args = parser.parse_args()

    # mTLS Sertifikaları (ACESTEP Port: 16311)
    base_cert_dir = "../sentiric-certificates/certs"
    try:
        with open(os.path.join(base_cert_dir, "ca.crt"), "rb") as f: ca_cert = f.read()
        with open(os.path.join(base_cert_dir, "audio-acestep-service-chain.crt"), "rb") as f: client_cert = f.read()
        with open(os.path.join(base_cert_dir, "audio-acestep-service.key"), "rb") as f: client_key = f.read()
    except FileNotFoundError:
        print(f"❌ Sertifikalar bulunamadı! {base_cert_dir} dizinini kontrol edin.")
        return

    creds = grpc.ssl_channel_credentials(ca_cert, client_key, client_cert)
    
    print("🎸 Sentiric ACE-Step Music Test Operasyonu Başlatılıyor (Port 16311)...")
    print("-" * 75)

    with grpc.secure_channel("localhost:16311", creds) as channel:
        stub = gateway_pb2_grpc.AudioGatewayServiceStub(channel)
        
        if args.prompt:
            dur = args.duration if args.duration else 10
            for _ in range(args.stress):
                send_job(stub, args.prompt, dur, "test-tenant")
        elif args.category:
            target_cats = EXAMPLES.keys() if args.category == "all" else [args.category]
            for cat in target_cats:
                print(f"\n🎼 KATEGORİ: {cat.upper()}")
                for item in EXAMPLES[cat]:
                    dur = args.duration if args.duration else item["d"]
                    for _ in range(args.stress):
                        send_job(stub, item["p"], dur, "test-tenant")
        else:
            cat_name = random.choice(list(EXAMPLES.keys()))
            item = random.choice(EXAMPLES[cat_name])
            print(f"🎲 Rastgele Seçilen Müzik: {cat_name.upper()}")
            send_job(stub, item["p"], item["d"], "test-tenant")

    print("-" * 75)
    print("🏁 İşlemler tamamlandı. Üretim süreci asenkron devam ediyor.")

if __name__ == "__main__":
    run_test()
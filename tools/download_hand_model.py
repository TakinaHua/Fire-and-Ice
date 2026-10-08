"""Download the pinned official MediaPipe model with certificate/hash checks."""
from pathlib import Path
import hashlib
import ssl
import urllib.request
import certifi

URL = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
SHA256 = 'fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1'
TARGET = Path(__file__).resolve().parents[1] / 'models' / 'hand_landmarker.task'


def main():
    if TARGET.exists() and hashlib.sha256(TARGET.read_bytes()).hexdigest() == SHA256:
        print('Hand model already present and verified.')
        return
    with urllib.request.urlopen(URL, context=ssl.create_default_context(cafile=certifi.where()), timeout=60) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise RuntimeError('Model checksum mismatch; existing model was not changed.')
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    temporary = TARGET.with_suffix('.download')
    temporary.write_bytes(data)
    temporary.replace(TARGET)
    print('Downloaded and verified:', TARGET)


if __name__ == '__main__':
    main()

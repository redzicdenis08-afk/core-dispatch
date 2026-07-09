from examples.webhook_handler import verify_signature

def test_signature_verification():
    secret = "test_secret"
    payload = b"test_payload"
    # signature generated with test_secret and test_payload
    sig = "6a5bf965beeb4d4bf597a7e1f44ef71d5b128522d4f23b20757270e59a68fa96"
    assert verify_signature(payload, sig, secret) is True

from PIL import Image
from cryptography.fernet import Fernet
import base64, hashlib


def generate_key(password: str) -> bytes:
    """Generate a Fernet key from password"""
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())


def encrypt_message(message: str, password: str) -> str:
    key = generate_key(password)
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()


def decrypt_message(encrypted_message: str, password: str) -> str:
    key = generate_key(password)
    f = Fernet(key)
    return f.decrypt(encrypted_message.encode()).decode()


def encode_message(image_path, secret_message, output_path):
    """Hide secret_message into image and save to output_path"""
    img = Image.open(image_path)
    encoded = img.copy()
    width, height = img.size
    index = 0

    binary_message = ''.join(format(ord(i), '08b') for i in secret_message)
    binary_message += '1111111111111110'  # EOF marker

    for row in range(height):
        for col in range(width):
            if index < len(binary_message):
                r, g, b = img.getpixel((col, row))
                r = (r & ~1) | int(binary_message[index])
                index += 1
                encoded.putpixel((col, row), (r, g, b))
            else:
                break
        if index >= len(binary_message):
            break

    encoded.save(output_path, "PNG")
    return output_path


def decode_message(image_path):
    """Extract hidden message bits from image"""
    img = Image.open(image_path)
    width, height = img.size
    binary_message = ""
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            binary_message += str(r & 1)

    all_bytes = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    decoded = ""
    for byte in all_bytes:
        decoded += chr(int(byte, 2))
        if decoded.endswith("þ"):  # EOF marker
            break
    return decoded[:-1]
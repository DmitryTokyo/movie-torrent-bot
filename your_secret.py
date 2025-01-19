"""
pip install cryptography
https://cryptography.io/en/latest/installation/
"""
import argparse
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken


def generate_secret_key(password: str):
    hashed_secret_key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hashed_secret_key)


def decrypt_secret(password: str):
    fernet_cipher = Fernet(generate_secret_key(password=password))
    encrypted_data = input('Paste encrypted data: ')
    try:
        return fernet_cipher.decrypt(encrypted_data).decode()
    except InvalidToken:
        exit('Check your password')
    except ValueError as e:
        exit(f'Error decrypting data: {e}')


def encrypt_secret(message: str, password: str | None = None):
    key = generate_secret_key(password=password)
    fernet_cipher = Fernet(key)
    return fernet_cipher.encrypt(message.encode()).decode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='YOUR SECRET')
    parser.add_argument('-m', '--message', type=str, help='Your secret message', default=None)
    parser.add_argument('-p', '--password', type=str, help='Your password')
    parser.print_help()
    args = parser.parse_args()
    if not args.password:
        exit('Password cannot be empty')
    print("""
    1. Encrypt
    2. Decrypt
    """)
    choice = input('Your choice: ')
    if choice == '1':
        if not args.message:
            secret_message = input('Enter your secret message: ')
            if not secret_message:
                exit('Secret cannot be empty')
        else:
            secret_message = args.secret
        encrypt_message = encrypt_secret(message=secret_message, password=args.password)
        print('Encrypted message:')
        print(encrypt_message)
    elif choice == '2':
        decrypting_message = decrypt_secret(args.password)
        print('Decrypted message:')
        print(decrypting_message)

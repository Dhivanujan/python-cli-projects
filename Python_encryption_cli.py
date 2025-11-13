import argparse
import os
import sys
import json
import base64
from getpass import getpass
from pathlib import Path

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend


# ---------------------- Utilities ----------------------

def b64(b: bytes) -> str:
    return base64.b64encode(b).decode('ascii')


def ub64(s: str) -> bytes:
    return base64.b64decode(s.encode('ascii'))


def derive_key_from_password(password: bytes, salt: bytes, iterations: int = 200000, length: int = 32) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password)


# ---------------------- RSA Keygen / Load ----------------------

def generate_rsa_keypair(private_path: Path, public_path: Path, key_size: int = 2048, password: bytes = None):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())

    enc_alg = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc_alg
    )

    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    private_path.write_bytes(priv_pem)
    public_path.write_bytes(pub_pem)
    print(f"Generated RSA keypair: {private_path} (private), {public_path} (public)")


def load_public_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_public_key(data, backend=default_backend())


def load_private_key(path: Path, password: bytes = None):
    data = path.read_bytes()
    return serialization.load_pem_private_key(data, password=password, backend=default_backend())


# ---------------------- Password-based AES-GCM ----------------------

def encrypt_with_password(in_path: Path, out_path: Path, password: bytes):
    salt = os.urandom(16)
    key = derive_key_from_password(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    plaintext = in_path.read_bytes()
    ct = aesgcm.encrypt(nonce, plaintext, None)

    package = {
        'mode': 'pass',
        'salt': b64(salt),
        'nonce': b64(nonce),
        'ct': b64(ct),
        'kdf': 'pbkdf2_sha256',
        'kdf_iters': 200000
    }
    out_path.write_bytes(json.dumps(package).encode('utf-8'))
    print(f"Wrote encrypted package (password) to {out_path}")


def decrypt_with_password(in_path: Path, out_path: Path, password: bytes):
    raw = in_path.read_bytes()
    package = json.loads(raw.decode('utf-8'))
    assert package.get('mode') == 'pass', 'Not a password-encrypted package'
    salt = ub64(package['salt'])
    nonce = ub64(package['nonce'])
    ct = ub64(package['ct'])
    key = derive_key_from_password(password, salt, iterations=package.get('kdf_iters', 200000))
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ct, None)
    out_path.write_bytes(pt)
    print(f"Decrypted to {out_path}")


# ---------------------- Hybrid RSA + AES-GCM ----------------------

def hybrid_encrypt(in_path: Path, out_path: Path, pubkey_path: Path):
    public_key = load_public_key(pubkey_path)
    # generate random AES key
    aes_key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    plaintext = in_path.read_bytes()
    ct = aesgcm.encrypt(nonce, plaintext, None)

    # encrypt AES key with RSA public key using OAEP
    enc_key = public_key.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    package = {
        'mode': 'hybrid',
        'enc_key': b64(enc_key),
        'nonce': b64(nonce),
        'ct': b64(ct),
        'meta': {
            'kdf': None,
            'cipher': 'AESGCM',
            'asymmetric': 'RSA-OAEP-SHA256'
        }
    }
    out_path.write_bytes(json.dumps(package).encode('utf-8'))
    print(f"Wrote hybrid encrypted package to {out_path}")


def hybrid_decrypt(in_path: Path, out_path: Path, privkey_path: Path, priv_password: bytes = None):
    private_key = load_private_key(privkey_path, priv_password)
    raw = in_path.read_bytes()
    package = json.loads(raw.decode('utf-8'))
    assert package.get('mode') == 'hybrid', 'Not a hybrid package'
    enc_key = ub64(package['enc_key'])
    nonce = ub64(package['nonce'])
    ct = ub64(package['ct'])

    aes_key = private_key.decrypt(
        enc_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    aesgcm = AESGCM(aes_key)
    pt = aesgcm.decrypt(nonce, ct, None)
    out_path.write_bytes(pt)
    print(f"Decrypted hybrid package to {out_path}")


# ---------------------- Short text encrypt (password) ----------------------

def encrypt_text_with_password(text: str, password: bytes) -> str:
    salt = os.urandom(16)
    key = derive_key_from_password(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, text.encode('utf-8'), None)
    package = {'salt': b64(salt), 'nonce': b64(nonce), 'ct': b64(ct)}
    token = base64.urlsafe_b64encode(json.dumps(package).encode('utf-8')).decode('ascii')
    return token


def decrypt_text_with_password(token: str, password: bytes) -> str:
    decoded = base64.urlsafe_b64decode(token.encode('ascii'))
    package = json.loads(decoded.decode('utf-8'))
    salt = ub64(package['salt'])
    nonce = ub64(package['nonce'])
    ct = ub64(package['ct'])
    key = derive_key_from_password(password, salt)
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt.decode('utf-8')


# ---------------------- CLI ----------------------

def build_parser():
    p = argparse.ArgumentParser(description='Python Encryption CLI')
    sub = p.add_subparsers(dest='cmd')

    # gen-keys
    g = sub.add_parser('gen-keys', help='Generate RSA keypair')
    g.add_argument('--private', required=True, help='Output private key path (PEM)')
    g.add_argument('--public', required=True, help='Output public key path (PEM)')
    g.add_argument('--password', action='store_true', help='Protect private key with passphrase (will prompt)')

    # enc-pass
    ep = sub.add_parser('enc-pass', help='Encrypt file with password')
    ep.add_argument('--in', dest='infile', required=True)
    ep.add_argument('--out', dest='outfile', required=True)
    ep.add_argument('--password', help='Password (unsafe on CLI). If omitted, will prompt')

    # dec-pass
    dp = sub.add_parser('dec-pass', help='Decrypt file with password')
    dp.add_argument('--in', dest='infile', required=True)
    dp.add_argument('--out', dest='outfile', required=True)
    dp.add_argument('--password', help='Password (unsafe on CLI). If omitted, will prompt')

    # hybrid encrypt (RSA)
    er = sub.add_parser('enc-rsa', help='Encrypt file for recipient (hybrid AES+RSA)')
    er.add_argument('--in', dest='infile', required=True)
    er.add_argument('--out', dest='outfile', required=True)
    er.add_argument('--pubkey', required=True, help='Recipient public key PEM')

    # hybrid decrypt
    dr = sub.add_parser('dec-rsa', help='Decrypt hybrid package with private key')
    dr.add_argument('--in', dest='infile', required=True)
    dr.add_argument('--out', dest='outfile', required=True)
    dr.add_argument('--privkey', required=True, help='Your private key PEM')
    dr.add_argument('--password', help='Private key password if encrypted (will prompt if omitted and needed)')

    # text encrypt/decrypt
    et = sub.add_parser('enc-text', help='Encrypt short text with password')
    et.add_argument('--text', required=True)
    et.add_argument('--password', help='Password (if omitted, will prompt)')

    dt = sub.add_parser('dec-text', help='Decrypt short text with password')
    dt.add_argument('--token', required=True)
    dt.add_argument('--password', help='Password (if omitted, will prompt)')

    return p


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.cmd:
        parser.print_help()
        return 1

    try:
        if args.cmd == 'gen-keys':
            priv_pass = None
            if args.password:
                pw = getpass('Private key passphrase: ')
                pw2 = getpass('Confirm passphrase: ')
                if pw != pw2:
                    print('Passphrases do not match', file=sys.stderr)
                    return 2
                priv_pass = pw.encode('utf-8')
            generate_rsa_keypair(Path(args.private), Path(args.public), password=priv_pass)

        elif args.cmd == 'enc-pass':
            pwd = args.password.encode('utf-8') if args.password else getpass('Encryption password: ').encode('utf-8')
            encrypt_with_password(Path(args.infile), Path(args.outfile), pwd)

        elif args.cmd == 'dec-pass':
            pwd = args.password.encode('utf-8') if args.password else getpass('Decryption password: ').encode('utf-8')
            decrypt_with_password(Path(args.infile), Path(args.outfile), pwd)

        elif args.cmd == 'enc-rsa':
            hybrid_encrypt(Path(args.infile), Path(args.outfile), Path(args.pubkey))

        elif args.cmd == 'dec-rsa':
            privpw = None
            if args.password:
                privpw = args.password.encode('utf-8')
            else:
                # try load without password; if fails, prompt
                try:
                    # quick attempt
                    load_private_key(Path(args.privkey), None)
                except TypeError:
                    # library expects bytes for password param; propagate
                    pass
                except Exception:
                    privpw = getpass('Private key passphrase: ').encode('utf-8')
            hybrid_decrypt(Path(args.infile), Path(args.outfile), Path(args.privkey), privpw)

        elif args.cmd == 'enc-text':
            pwd = args.password.encode('utf-8') if args.password else getpass('Password: ').encode('utf-8')
            token = encrypt_text_with_password(args.text, pwd)
            print('TOKEN:', token)

        elif args.cmd == 'dec-text':
            pwd = args.password.encode('utf-8') if args.password else getpass('Password: ').encode('utf-8')
            text = decrypt_text_with_password(args.token, pwd)
            print('PLAINTEXT:', text)

        else:
            print('Unknown command', file=sys.stderr)
            return 3

    except Exception as e:
        print('Error:', e, file=sys.stderr)
        return 4

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

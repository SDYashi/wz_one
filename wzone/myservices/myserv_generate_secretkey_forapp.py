import os
import secrets
import subprocess
from flask import Flask, jsonify

app = Flask(__name__)

class SecretKeyManager:
    @staticmethod
    def generate_secret_key():
        """Generate a new secret key."""
        return secrets.token_hex(32)

    @staticmethod
    def set_permanent_env_var_windows(var_name, var_value):
        """Set a permanent environment variable on Windows."""
        command = f'setx {var_name} "{var_value}"'
        subprocess.run(command, shell=True, check=True)
        print(f"Permanent environment variable '{var_name}' set to '{var_value}'.")

    @classmethod
    def update_secret_key(cls):
        """Generate a new secret key and set it as a permanent environment variable."""
        secret_key = cls.generate_secret_key()
        cls.set_permanent_env_var_windows('JWT_SECRET_KEY', secret_key)
        return secret_key



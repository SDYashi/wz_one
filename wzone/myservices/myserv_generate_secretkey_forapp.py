import os
import secrets
import subprocess

def generate_secret_key():
    return secrets.token_hex(32) 

def set_permanent_env_var_windows(var_name, var_value):
    command = f'setx {var_name} "{var_value}"'
    subprocess.run(command, shell=True, check=True)
    print(f"Permanent environment variable '{var_name}' set to '{var_value}'.")

def update_secretekey_forapp():
    # Generate a secret key
    secret_key = generate_secret_key()    
    # Set the secret key as a permanent environment variable
    set_permanent_env_var_windows('MY_SECRET_KEY', secret_key)

if __name__ == "__main__":
    update_secretekey_forapp()
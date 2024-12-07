import secrets

class myserv_generate_secretkey_forapp:
    def __init__(self, length=32):
        self.length = length

    def generate_secret_key(self):
        return secrets.token_hex(self.length)
    
if __name__ == "__main__":
    generator = myserv_generate_secretkey_forapp(length=32)
    secret_key = generator.generate_secret_key()
    print("Generated Secret Key for applications:", secret_key)
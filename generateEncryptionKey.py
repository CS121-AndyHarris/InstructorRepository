from cryptography.fernet import Fernet
print(f"Your key is: {Fernet.generate_key().decode()}")
import os

def set_to_practice():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ Archivo .env no encontrado")
        return

    with open(env_path, "r") as f:
        lines = f.readlines()

    with open(env_path, "w") as f:
        for line in lines:
            if line.startswith("ACCOUNT_TYPE="):
                f.write("ACCOUNT_TYPE=PRACTICE\n")
                print("✅ ACCOUNT_TYPE cambiado a PRACTICE")
            else:
                f.write(line)

if __name__ == "__main__":
    set_to_practice()

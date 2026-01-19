import os
import time
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_database_connection():
    print("="*60)
    print("🔬 DIAGNÓSTICO DE BASE DE DATOS (EASYPANEL COMPATIBLE)")
    print("="*60)
    
    # 1. Verificar variables de entorno
    print("\n1. Verificando Variables de Entorno:")
    env_vars = ['DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    found_vars = {}
    for var in env_vars:
        val = os.getenv(var)
        found_vars[var] = "✅ Presente" if val else "❌ Faltante"
        if val:
            # Ocultar contraseña en log
            display_val = "***" if 'PASSWORD' in var else val
            print(f"   - {var}: {display_val}")
        else:
            print(f"   - {var}: [NO DEFINIDO]")

    # 2. Intentar conexión
    print("\n2. Probando conexión a PostgreSQL...")
    
    conn = None
    try:
        # Prioridad: DATABASE_URL -> Variables Individuales
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            print(f"   ℹ️ Usando DATABASE_URL (Formato Easypanel)")
            conn = psycopg2.connect(database_url, connect_timeout=5)
        else:
            print(f"   ℹ️ Usando credenciales individuales")
            # Fallback values default (updated from user image)
            host = os.getenv('DB_HOST', '164.68.122.5')
            port = os.getenv('DB_PORT', '5434')
            dbname = os.getenv('DB_NAME', 'alabanza')
            user = os.getenv('DB_USER', 'postgres')
            password = os.getenv('DB_PASSWORD', '6715320Dvd.')
            
            print(f"   🚀 Conectando a {host}:{port}/{dbname} como {user}...")
            conn = psycopg2.connect(
                host=host, port=port, database=dbname, user=user, password=password, connect_timeout=5
            )

        if conn:
            print("   ✅ ¡CONEXIÓN EXITOSA!")
            
            # 3. Verificar tablas
            print("\n3. Verificando esquema de datos...")
            cursor = conn.cursor()
            
            # Verificar tabla 'trades' o 'experiences'
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            print(f"   📊 Tablas encontradas: {len(tables)}")
            for table in tables:
                # Contar registros
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"      - {table[0]}: {count} registros")
                except:
                    print(f"      - {table[0]}: (Error al leer)")
            
            check_working_data(conn)
            
            conn.close()
            return True
            
    except Exception as e:
        print(f"   ❌ ERROR DE CONEXIÓN: {str(e)}")
        print("\n💡 TIP: Verifica que el servicio de Database esté corriendo y en la misma red de Easypanel.")
        if "timeout" in str(e).lower():
            print("   - El error indica TIMEOUT: Puede ser firewall o dirección IP incorrecta.")
        return False

def check_working_data(conn):
    """Verifica si hay datos recientes para confirmar que 'funciona'"""
    print("\n4. Verificando actividad reciente...")
    cursor = conn.cursor()
    try:
        # Intentar buscar la tabla de experiencias o trades
        tables = ["bot_experiences", "trading_results", "market_data"]
        found = False
        for t in tables:
            try:
                cursor.execute(f"SELECT * FROM {t} ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    print(f"   ✅ Datos recientes encontrados en '{t}': {row}")
                    found = True
                    break
            except:
                pass
        
        if not found:
            print("   ⚠️ No se encontraron datos recientes en las tablas estándar. (La BD puede estar vacía)")
            
    except Exception as e:
        print(f"   ⚠️ Error verificando datos recientes: {e}")

if __name__ == "__main__":
    check_database_connection()

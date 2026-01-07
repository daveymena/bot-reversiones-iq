"""
Script de inicialización de la base de datos
Crea la base de datos, tablas, índices y datos iniciales
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Crear base de datos si no existe"""
    print("=" * 60)
    print("SETUP DE BASE DE DATOS - BOT DE TRADING")
    print("=" * 60)
    
    # Conectar a PostgreSQL (base de datos por defecto)
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database='postgres',  # Base de datos por defecto
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Verificar si la base de datos existe
        db_name = os.getenv('DB_NAME', 'trading_bot')
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"\n1. Creando base de datos '{db_name}'...")
            cur.execute(f'CREATE DATABASE {db_name}')
            print(f"   ✅ Base de datos '{db_name}' creada")
        else:
            print(f"\n1. Base de datos '{db_name}' ya existe")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True

def create_extensions():
    """Crear extensiones necesarias"""
    print("\n2. Creando extensiones...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'trading_bot'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cur = conn.cursor()
        
        # UUID
        cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        print("   ✅ Extensión uuid-ossp creada")
        
        # TimescaleDB (opcional, si está instalado)
        try:
            cur.execute('CREATE EXTENSION IF NOT EXISTS "timescaledb"')
            print("   ✅ Extensión timescaledb creada")
        except:
            print("   ⚠️  TimescaleDB no disponible (opcional)")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True

def create_schema():
    """Crear tablas y estructura"""
    print("\n3. Creando tablas...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'trading_bot'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cur = conn.cursor()
        
        # Leer y ejecutar schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Ejecutar el schema (puede tomar un momento)
            cur.execute(schema_sql)
            conn.commit()
            print("   ✅ Tablas creadas exitosamente")
        else:
            print(f"   ❌ No se encontró {schema_path}")
            return False
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True

def verify_setup():
    """Verificar que todo esté correcto"""
    print("\n4. Verificando instalación...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'trading_bot'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cur = conn.cursor()
        
        # Verificar tablas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        
        expected_tables = [
            'trades',
            'market_conditions',
            'learning_experiences',
            'pattern_performance',
            'model_performance',
            'decision_logs',
            'error_patterns',
            'strategy_evolution',
            'market_regime'
        ]
        
        print(f"\n   Tablas encontradas: {len(tables)}")
        for table in tables:
            status = "✅" if table in expected_tables else "⚠️"
            print(f"   {status} {table}")
        
        # Verificar vistas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
        """)
        
        views = [row[0] for row in cur.fetchall()]
        print(f"\n   Vistas encontradas: {len(views)}")
        for view in views:
            print(f"   ✅ {view}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_connection():
    """Probar conexión con el gestor de BD"""
    print("\n5. Probando conexión con db_manager...")
    
    try:
        from database.db_manager import db
        
        # Probar obtener estadísticas (debería devolver vacío)
        stats = db.get_performance_stats(days=7)
        print(f"   ✅ Conexión exitosa")
        print(f"   📊 Trades en BD: {stats.get('total_trades', 0)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Ejecutar setup completo"""
    
    # Verificar variables de entorno
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\n⚠️  Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nAgrega estas variables a tu archivo .env")
        return
    
    # Ejecutar pasos
    steps = [
        ("Crear base de datos", create_database),
        ("Crear extensiones", create_extensions),
        ("Crear schema", create_schema),
        ("Verificar instalación", verify_setup),
        ("Probar conexión", test_connection)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Falló: {step_name}")
            print("Revisa los errores arriba y vuelve a intentar")
            return
    
    # Éxito
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print("""
La base de datos está lista para usar.

Próximos pasos:
1. Integrar db_manager en core/trader.py
2. Guardar cada trade en la BD
3. Guardar experiencias para re-entrenamiento
4. Analizar patrones y errores

Comandos útiles:
- Ver trades: SELECT * FROM trades ORDER BY entry_time DESC LIMIT 10;
- Ver estadísticas: SELECT * FROM performance_by_asset;
- Ver patrones: SELECT * FROM best_patterns;
- Ver errores: SELECT * FROM costly_errors;

Conectar a la BD:
psql -U {os.getenv('DB_USER')} -d {os.getenv('DB_NAME')}
    """)

if __name__ == "__main__":
    main()

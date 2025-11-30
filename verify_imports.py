import sys
print("Verifying imports...")

try:
    import groq
    print("✅ groq imported")
except ImportError as e:
    print(f"❌ groq failed: {e}")

try:
    import requests
    print("✅ requests imported")
except ImportError as e:
    print(f"❌ requests failed: {e}")

try:
    import pandas
    print("✅ pandas imported")
except ImportError as e:
    print(f"❌ pandas failed: {e}")

try:
    import numpy
    print("✅ numpy imported")
except ImportError as e:
    print(f"❌ numpy failed: {e}")

try:
    import PySide6
    print("✅ PySide6 imported")
except ImportError as e:
    print(f"❌ PySide6 failed: {e}")

try:
    import stable_baselines3
    print("✅ stable_baselines3 imported")
except ImportError as e:
    print(f"❌ stable_baselines3 failed: {e}")

try:
    import iqoptionapi
    print("✅ iqoptionapi imported")
except ImportError as e:
    print(f"❌ iqoptionapi failed: {e}")

try:
    import ollama
    print("✅ ollama imported")
except ImportError as e:
    print(f"❌ ollama failed: {e}")

print("Import verification complete.")

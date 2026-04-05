#!/bin/bash
# Script para preparar el bot para Git

echo "🚀 PREPARANDO BOT PARA GIT..."
echo ""

# Validar deployment
echo "1️⃣ Validando deployment..."
python scripts/validate_deployment.py

if [ $? -ne 0 ]; then
    echo "❌ Validación fallida. Revisar errores."
    exit 1
fi

echo ""
echo "2️⃣ Verificando estado de Git..."
git status

echo ""
echo "3️⃣ Agregando cambios..."
git add .

echo ""
echo "4️⃣ Mostrando cambios a commitear..."
git diff --cached --stat

echo ""
read -p "¿Deseas continuar con el commit? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    git commit -m "Preparar bot para Git y EasyPanel - V5-PRODUCTION"
    
    echo ""
    echo "5️⃣ Mostrando cambios a pushear..."
    git log --oneline -1
    
    echo ""
    read -p "¿Deseas hacer push? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        git push origin main
        echo "✅ Bot subido a Git exitosamente"
    else
        echo "⚠️ Push cancelado. Cambios en local."
    fi
else
    echo "❌ Commit cancelado."
    git reset
fi

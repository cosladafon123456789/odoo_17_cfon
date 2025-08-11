# CFON Read More for Conversations (Odoo 17)

Este módulo acorta automáticamente los mensajes largos en **Conversaciones (Discuss)** y en el **Chatter**, mostrando solo los primeros **50 caracteres** junto a un enlace **"leer más"**. Al pulsarlo, se expande el mensaje completo.

## Instalación
1. Copia la carpeta `cfon_read_more_conversations` dentro de tu ruta de `addons`.
2. En Odoo (modo desarrollador) ve a **Apps → Actualizar lista de aplicaciones**.
3. Busca **CFON Read More for Conversations** e **Instalar**.

> Si ya lo tenías, pulsa **Actualizar** para recompilar los assets. Limpia caché del navegador (Ctrl+F5).

## Cómo cambiar el límite de 50 caracteres
Edita `static/src/js/read_more.js` y cambia `const CHAR_LIMIT = 50;` por el valor que quieras.
# Icono de la Aplicación

Para agregar un icono personalizado:

1. Crea o descarga un archivo `.ico` con tu logo
2. Renómbralo como `icon.ico`
3. Colócalo en la carpeta raíz del proyecto

## Crear un .ico desde una imagen

### Opción 1: Online
- Visita: https://convertio.co/es/png-ico/
- Sube tu imagen PNG/JPG
- Descarga el .ico

### Opción 2: Con Python
```python
from PIL import Image

img = Image.open('tu_imagen.png')
img.save('icon.ico', format='ICO', sizes=[(256, 256)])
```

## Tamaños recomendados
- 16x16, 32x32, 48x48, 256x256 píxeles
- Formato: ICO (Windows Icon)

## Si no tienes icono
- Comenta la línea `SetupIconFile=icon.ico` en `setup.iss`
- El instalador usará el icono por defecto de Windows

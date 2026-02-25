import re

def extraer_importe_iberdrola(texto):
    """
    Busca el total final de la factura de Iberdrola.
    El formato objetivo es: TOTAL IMPORTE FACTURA 170,14 €
    """
    # Buscamos la frase completa para no confundirnos con subtotales o el IVA
    # \s+ maneja espacios o saltos de línea inesperados
    # ([\d.,]+) captura el número con decimales
    patron = r'TOTAL IMPORTE FACTURA\s+([\d.,]+)\s?€'
    
    match = re.search(patron, texto, re.IGNORECASE)
    
    if match:
        importe_str = match.group(1)
        # Limpieza: Iberdrola usa ',' para decimales y a veces '.' para miles (ej: 1.170,14)
        # Primero quitamos el punto de miles (si existiera) y luego cambiamos la coma por punto.
        importe_limpio = importe_str.replace('.', '').replace(',', '.')
        
        try:
            return float(importe_limpio)
        except ValueError:
            print(f"❌ No se pudo convertir {importe_str} a número.")
            return None
            
    return None

def extraer_importe_totalenergies(texto):
    """
    Busca el total final de la factura de TotalEnergies.
    El formato es: línea "Importe", luego fecha, luego tipo de servicio, luego "454,09 €"
    """
    # Buscamos el patrón donde después de "Importe" viene una línea con fecha,
    # luego tipo de servicio, luego el número con €
    # Usamos una búsqueda más flexible: buscamos números seguidos de € que aparezcan
    # después de "Importe" en el contexto de la factura
    
    # Primero intentamos buscar en el contexto de "Importe"
    patron_importe = r'Importe\s*\n\s*[\d.]+\.\d+\.\d+\s*\n\s*[^\n]+\n\s*([\d,]+)\s*€'
    
    match = re.search(patron_importe, texto, re.IGNORECASE | re.DOTALL)
    
    if match:
        importe_str = match.group(1)
        # TotalEnergies usa ',' para decimales
        importe_limpio = importe_str.replace('.', '').replace(',', '.')
        
        try:
            return float(importe_limpio)
        except ValueError:
            print(f"❌ No se pudo convertir {importe_str} a número.")
            return None
    
    # Si el patrón anterior no funciona, buscamos simplemente números con formato "XXX,XX €"
    # y devolvemos el último encontrado (más cercano al final del documento)
    patron_simple = r'([\d,]+)\s*€'
    matches = re.findall(patron_simple, texto)
    
    if matches:
        # Tomamos el último número encontrado (más probable que sea el total)
        importe_str = matches[-1]
        importe_limpio = importe_str.replace('.', '').replace(',', '.')
        
        try:
            return float(importe_limpio)
        except ValueError:
            print(f"❌ No se pudo convertir {importe_str} a número.")
            return None
    
    return None
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
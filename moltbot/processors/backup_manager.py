import json
import os
from database import get_workflows

def backup_n8n_workflows(output_folder="/n8n-workflows"):
    """
    Lee los flujos de la tabla de n8n y los guarda como archivos .json
    """
    # Asegurarnos de que la carpeta existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    try:
        workflows = get_workflows()
        
        if workflows:
            for name, nodes, connections in workflows:
                # Limpiar el nombre para que sea un nombre de archivo válido
                filename = "".join([c for c in name if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
                path = f"{output_folder}/{filename}.json"
                
                workflow_data = {
                    "name": name,
                    "nodes": nodes,
                    "connections": connections
                }
                
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(workflow_data, f, indent=4, ensure_ascii=False)
            
            return len(workflows)
    except Exception as e:
        print(f"❌ Error en backup de workflows: {e}")
        return None
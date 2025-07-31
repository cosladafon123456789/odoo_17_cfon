from odoo import models, api
import requests
import json

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_fill_with_ai(self):
        for record in self:
            if not record.name:
                continue
            prompt = f"Dado el nombre del producto '{record.name}', devuelve un JSON con los siguientes campos: marca, modelo_movil, color_visual, almacenamiento, memoria_ram, capacidad, capacidad_bateria, camara, numero_de_camaras, pantalla, conectividad."
            headers = {
                "Authorization": "Bearer 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",
                "Content-Type": "application/json"
            }
            body = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(body))
            if response.status_code == 200:
                try:
                    content = response.json()["choices"][0]["message"]["content"]
                    data = json.loads(content)
                    record.write({
                        'x_studio_marcas': data.get('marca'),
                        'x_studio_many2one_field_6jm_1il381ia8': data.get('modelo_movil'),
                        'x_studio_color_visual': data.get('color_visual'),
                        'x_almacenamiento': data.get('almacenamiento'),
                        'x_memoria_ram': data.get('memoria_ram'),
                        'x_capacidad': data.get('capacidad'),
                        'x_capacidad_bateria': data.get('capacidad_bateria'),
                        'x_camara': data.get('camara'),
                        'x_numero_de_camaras': data.get('numero_de_camaras'),
                        'x_pantalla': data.get('pantalla'),
                        'x_conectividad': data.get('conectividad'),
                    })
                except Exception as e:
                    raise ValueError("Error al interpretar respuesta de OpenAI: %s" % str(e))
            else:
                raise ValueError("Fallo al conectar con OpenAI: %s" % response.text)

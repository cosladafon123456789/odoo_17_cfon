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

                    update_vals = {}

                    # Marcas (Char or Many2one)
                    if 'x_studio_marcas' in record:
                        update_vals['x_studio_marcas'] = data.get('marca')

                    # Modelo Móvil (Many2one)
                    modelo_nombre = data.get('modelo_movil')
                    if modelo_nombre:
                        modelo_field = 'x_studio_many2one_field_6jm_1il381ia8'
                        if modelo_field in record:
                            modelo_model = record._fields[modelo_field].comodel_name
                            modelo_obj = self.env[modelo_model].search([('name', '=', modelo_nombre)], limit=1)
                            if not modelo_obj:
                                modelo_obj = self.env[modelo_model].create({'name': modelo_nombre})
                            update_vals[modelo_field] = modelo_obj.id

                    # Color Visual
                    if 'x_studio_color_visual' in record:
                        update_vals['x_studio_color_visual'] = data.get('color_visual')

                    # Otros campos normales
                    normal_fields = [
                        'x_almacenamiento', 'x_memoria_ram', 'x_capacidad',
                        'x_capacidad_bateria', 'x_camara', 'x_numero_de_camaras',
                        'x_pantalla', 'x_conectividad'
                    ]
                    for field in normal_fields:
                        if field in record:
                            update_vals[field] = data.get(field.replace('x_', ''))

                    record.write(update_vals)

                except Exception as e:
                    raise ValueError("Error al interpretar respuesta de OpenAI: %s" % str(e))
            else:
                raise ValueError("Fallo al conectar con OpenAI: %s" % response.text)

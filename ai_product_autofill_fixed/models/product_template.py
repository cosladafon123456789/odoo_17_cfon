from odoo import models, api
import openai
import json

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_fill_with_ai(self):
        openai.api_key = "sk-..."  # Sustituir por la clave real del usuario

        for product in self:
            prompt = f"""
Extrae del siguiente nombre de producto los campos:
- Marca
- Modelo
- Color

Ejemplo: "iPhone 13 Pro 128GB Azul"
Devuelve un JSON con estos campos.
Texto: "{product.name}"
"""
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                result = json.loads(response.choices[0].message.content)

                marca = self.env['x_marcas'].search([('name', '=', result.get('Marca'))], limit=1)
                if not marca:
                    marca = self.env['x_marcas'].create({'name': result.get('Marca')})

                modelo = self.env['x_modelos_moviles'].search([('name', '=', result.get('Modelo'))], limit=1)
                if not modelo:
                    modelo = self.env['x_modelos_moviles'].create({'name': result.get('Modelo')})

                product.write({
                    'x_studio_marcas': marca.id,
                    'x_studio_many2one_field_6jm_1il381ia8': modelo.id,
                    'x_studio_color_visual': result.get('Color')
                })
            except Exception as e:
                raise Warning(f"Error al consultar OpenAI: {str(e)}")

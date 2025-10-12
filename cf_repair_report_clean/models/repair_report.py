
from odoo import models, fields, api

class RepairReport(models.Model):
    _name = "repair.report"
    _description = "Informe diario de reparaciones"
    _order = "date desc, id desc"

    technician_id = fields.Many2one("res.users", string="Técnico", required=True, index=True)
    repair_id = fields.Many2one("repair.order", string="Orden de reparación", required=True, ondelete="cascade")
    reason = fields.Selection([
        ('battery_change', 'Cambio de batería'),
        ('battery_connector', 'Reparación conector batería / circuito'),
        ('battery_low_health', 'Batería con baja capacidad'),
        ('screen_change', 'Cambio de pantalla'),
        ('screen_glass', 'Cambio de cristal'),
        ('screen_touch', 'Fallo táctil / touch'),
        ('screen_lcd', 'Pantalla sin imagen / LCD roto'),
        ('earpiece', 'Altavoz auricular'),
        ('loudspeaker', 'Altavoz inferior'),
        ('microphone', 'Micrófono'),
        ('audio_ic', 'Fallo de Audio IC'),
        ('front_camera', 'Cámara frontal'),
        ('rear_camera', 'Cámara trasera'),
        ('camera_glass', 'Cristal cámara roto'),
        ('face_id', 'Face ID / FaceTime no funciona'),
        ('charging_port', 'Conector de carga'),
        ('not_charging', 'No carga / carga intermitente'),
        ('power_ic', 'Fallo PMIC / encendido'),
        ('no_signal', 'Sin señal / red'),
        ('wifi_bt', 'WiFi o Bluetooth'),
        ('sim_reader', 'Lector SIM'),
        ('housing_change', 'Cambio de carcasa'),
        ('button_issue', 'Botón (power, volumen, home, etc.)'),
        ('sensor_issue', 'Sensor de proximidad / luz'),
        ('board_repair', 'Reparación de placa base'),
        ('diagnostic_only', 'Solo diagnóstico'),
        ('software_update', 'Reinstalación / actualización software'),
        ('other', 'Otro motivo'),
    ], string="Motivo", required=True, index=True)
    date = fields.Datetime(string="Fecha", default=fields.Datetime.now, required=True, index=True)

    @api.model
    def create_report(self, repair, reason):
        """Crear entrada de informe asignando SIEMPRE al usuario actual (quien pulsa)."""
        return self.create({
            "technician_id": self.env.user.id,
            "repair_id": repair.id,
            "reason": reason,
            "date": fields.Datetime.now(),
        })

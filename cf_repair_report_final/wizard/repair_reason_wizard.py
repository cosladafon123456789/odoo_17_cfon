
from odoo import models, fields

class RepairReasonWizard(models.TransientModel):
    _name = "repair.reason.wizard"
    _description = "Motivo de la reparación"

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
    ], string="Motivo de la reparación", required=True)

    def action_confirm(self):
        self.ensure_one()
        repair = self.env['repair.order'].browse(self.env.context.get('active_id'))
        self.env['repair.report'].create_report(repair, self.reason)
        repair.action_repair_end()
        return {"type": "ir.actions.act_window_close"}

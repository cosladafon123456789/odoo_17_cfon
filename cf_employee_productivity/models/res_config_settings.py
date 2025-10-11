<odoo>
    <record id="view_cf_employee_productivity_settings" model="ir.ui.view">
        <field name="name">cf.employee.productivity.settings</field>
        <field name="model">res.config.settings</field>
        <field name="arch" type="xml">
            <form string="Configuración de Productividad">
                <sheet>
                    <group name="group_cf_employee_productivity_users">
                        <separator string="Usuarios contabilizados" colspan="2"/>
                        <field name="picking_user_ids" widget="many2many_tags"/>
                        <field name="repair_user_ids" widget="many2many_tags"/>
                        <field name="helpdesk_user_ids" widget="many2many_tags"/>
                    </group>
                    <group name="group_cf_employee_productivity_notifications">
                        <separator string="Notificaciones diarias" colspan="2"/>
                        <field name="send_daily_summary"/>
                        <field name="summary_recipient_ids" widget="many2many_tags"/>
                    </group>
                </sheet>
                <footer>
                    <button string="Guardar" type="object" name="execute" class="btn-primary"/>
                    <button string="Cancelar" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_cf_employee_productivity_settings" model="ir.actions.act_window">
        <field name="name">Configuración de Productividad</field>
        <field name="res_model">res.config.settings</field>
        <field name="view_mode">form</field>
        <field name="view_id" ref="view_cf_employee_productivity_settings"/>
        <field name="target">inline</field>
    </record>

    <menuitem id="menu_cf_employee_productivity_settings"
              name="Configuración"
              parent="menu_productivity_root"
              sequence="50"
              action="action_cf_employee_productivity_settings"/>
</odoo>

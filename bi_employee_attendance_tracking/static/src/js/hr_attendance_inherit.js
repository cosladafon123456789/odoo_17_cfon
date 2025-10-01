/* @odoo-module */

import { ActivityMenu } from "@hr_attendance/components/attendance_menu/attendance_menu"
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { isIosApp } from "@web/core/browser/feature_detection";


patch(ActivityMenu.prototype, {
  
	setup() {
        super.setup(...arguments)
		this.action = useService("action");
	},

    async signInOut() {
       
        const self = this;
        const result = await this.rpc("/hr_attendance/attendance_user_data");
        this.employee_id = result;
        const emp_info = await this.rpc('/bi_employee_company_transfer/emp_attendance_data')
    
        if (result['attendance_state'] != 'checked_in'){

            if (emp_info['attendance_check_in'] > emp_info['hour_from'] || emp_info['attendance_check_in'] >= emp_info['hour_from']  && emp_info['attendance_check_in_min'] > emp_info['hour_from_min'] ){
                await this.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: 'checkin.time.wizard',
                    views: [[false, "form"]],
                    view_mode: "form",
                    target: 'new',
                });
            }

            else {
                if (emp_info['attendance_check_in'] < emp_info['hour_from']) { 
                    if (!isIosApp()) {
                        navigator.geolocation.getCurrentPosition(
                            async ({coords: {latitude, longitude}}) => {
                                await this.rpc("/hr_attendance/systray_check_in_out", {
                                    latitude,
                                    longitude
                                })
                                await this.searchReadEmployee()
                            },
                            async err => {
                                await this.rpc("/hr_attendance/systray_check_in_out")
                                await this.searchReadEmployee()
                            },
                            {
                                enableHighAccuracy: true,
                            }
                        )
                    }
                        
                    else {
                        await this.rpc("/hr_attendance/systray_check_in_out")
                        await this.searchReadEmployee()
                    }
                
                }
            }
           
        }

        if (result['attendance_state'] == 'checked_in'){
            if (emp_info['attendance_check_out'] > emp_info['hour_to'] || emp_info['attendance_check_out'] >= emp_info['hour_to'] && emp_info['attendance_check_out_min'] > emp_info['hour_to_min']){
                await this.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: 'checkout.time.wizard',
                    views: [[false, "form"]],
                    view_mode: "form",
                    target: 'new',
                });
            }

            else {

                if (emp_info['attendance_check_out'] < emp_info['hour_to']) { 
    
                    if (!isIosApp()) {
                        navigator.geolocation.getCurrentPosition(
                            async ({coords: {latitude, longitude}}) => {
                                await this.rpc("/hr_attendance/systray_check_in_out", {
                                    latitude,
                                    longitude
                                })
                                await this.searchReadEmployee()
                            },
                            async err => {
                                await this.rpc("/hr_attendance/systray_check_in_out")
                                await this.searchReadEmployee()
                            },
    
                            {
                                enableHighAccuracy: true,
                            }
                        )
                    }
                    
                    else {
                        await this.rpc("/hr_attendance/systray_check_in_out")
                        await this.searchReadEmployee()
                    }
    
                }
    
            }
       
        }
    }
    
})

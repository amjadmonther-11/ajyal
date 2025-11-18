odoo.define('education_attendances.Dashboard', function (require) {
"use strict";

var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var Model = require('web.Model');
var session = require('web.session');
var utils = require('web.utils');
var web_client = require('web.web_client');
var Widget = require('web.Widget');
var session = require('web.session');
var _t = core._t;
var QWeb = core.qweb;

var HrDashboard = Widget.extend(ControlPanelMixin, {
    template: "AttendDashboardMain",
    events: {
        'click .view_attendances': 'view_attendances',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.school_fees = true;
        this.schools=[];
        this._super(parent,context);

    },

    start: function() {
        var self = this;
	for(var i in self.breadcrumbs){
            self.breadcrumbs[i].title = "Dashboard";
            }
            self.update_control_panel({breadcrumbs: self.breadcrumbs}, {clear: true});
        var hr_emp = new Model('ducation.attendance');
        var model  = new Model('education.attendance').call('get_attendance_details').then(function(result){

            this.school_fees =  result[0];
            $('.o_hr_dashboard').html(QWeb.render('ManagerDashboard', {widget: this}));
            
        });
        var today = new Date().toJSON().slice(0,10).replace(/-/g,'/');
        var school = new Model('school.school').query(['name'])
            .order_by('id').all().then(function(res){
            for (var i = 0; i < res.length; i++) {
                
                    self.schools.push(res[i]);
                    
            }
                
        });
    },

    view_attendances: function(e){
        var self = this;
        $("button").click(function() { 
                var t = $(this).attr('id'); 
                
                $("#school_id").val(t);
               
            }); 
        var school_id =parseInt($("#school_id").val());
        e.stopPropagation();
        e.preventDefault();
         
                
        
       if(school_id>-1){

       
        this.do_action({
            name: _t("Students Attendance"),
            type: 'ir.actions.act_window',
            res_model: 'education.attendance',
            view_mode: 'tree,form,calendar',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context:{'search_default_today': 1},
            domain: [['division_id.school_id','=',school_id]],
            target: 'current',
        })
    }
    },

    
  
});

core.action_registry.add('attendance_dashboard', HrDashboard);

return HrDashboard;

});

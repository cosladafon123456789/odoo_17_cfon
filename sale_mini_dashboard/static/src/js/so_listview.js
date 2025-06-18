/** @odoo-module **/
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { SODashBoard } from '@sale_mini_dashboard/js/so_dashboard';

/**
 * Sale Dashboard Renderer class for list view, extending the base ListRenderer.
 * @extends ListRenderer
 */
export class SODashBoardRenderer extends ListRenderer {};

// Template for the SODashBoardRenderer component
SODashBoardRenderer.template = 'sale_mini_dashboard.SOListView';

// Components used by SODashBoardRenderer
SODashBoardRenderer.components = Object.assign({}, ListRenderer.components, { SODashBoard });

/**
 * Sale Dashboard List View configuration.
 * @type {Object}
 */
export const SODashBoardListView = {
    ...listView,
    // Use the custom SODashBoardRenderer as the renderer for the list view
    Renderer: SODashBoardRenderer,
};

// Register the Sale Dashboard List View in the "views" category of the registry
registry.category("views").add("so_dashboard_list", SODashBoardListView);

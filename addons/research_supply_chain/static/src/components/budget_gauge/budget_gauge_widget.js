/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class BudgetGaugeWidget extends Component {
    static template = "research_supply_chain.BudgetGaugeWidget";
    static props = {
        ...standardFieldProps,
    };

    get percentage() {
        const val = this.props.record.data[this.props.name] || 0;
        return Math.min(Math.max(Math.round(val), 0), 100);
    }

    get progressColorClass() {
        const pct = this.percentage;
        if (pct > 90) {
            return "bg-danger";
        } else if (pct > 75) {
            return "bg-warning";
        }
        return "bg-success";
    }

    get statusLabel() {
        const pct = this.percentage;
        if (pct >= 100) {
            return "Budget Exhausted";
        } else if (pct > 75) {
            return "High Utilization";
        }
        return "On Track";
    }
}

export const budgetGaugeField = {
    component: BudgetGaugeWidget,
    supportedTypes: ["float", "integer"],
};

registry.category("fields").add("research_budget_gauge", budgetGaugeField);

/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ResearchDashboard extends Component {
    static template = "research_supply_chain.ResearchDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            stats: {
                totalProjects: 0,
                activeExperiments: 0,
                totalBudgetAllocated: 0,
                totalBudgetSpent: 0,
                publishedOutputs: 0,
            },
            recentProjects: [],
            isFinanceOfficer: false,
            isManager: false,
        });

        onWillStart(async () => {
            await this.checkPermissions();
            await this.loadDashboardData();
        });
    }

    async checkPermissions() {
        try {
            this.state.isFinanceOfficer = await this.orm.call("res.users", "has_group", ["research_supply_chain.group_research_finance"]);
            this.state.isManager = await this.orm.call("res.users", "has_group", ["research_supply_chain.group_research_manager"]);
        } catch (e) {
            console.warn("Could not check user groups via ORM call, defaulting to broad view.", e);
            this.state.isFinanceOfficer = true;
            this.state.isManager = true;
        }
    }

    async loadDashboardData() {
        this.state.loading = true;
        try {
            // ORM searchCount calls automatically enforce Odoo ACLs and Record Rules
            const [projectsCount, experimentsCount, outputsCount, papersCount] = await Promise.all([
                this.orm.searchCount("research.project", [["project_status", "in", ["proposed", "approved", "in_progress"]]]),
                this.orm.searchCount("research.experiment", [["status", "in", ["running", "planned"]]]),
                this.orm.searchCount("research.output", [["status", "=", "published"]]),
                this.orm.searchCount("research.paper", [["paper_status", "=", "published"]]),
            ]);

            this.state.stats.totalProjects = projectsCount;
            this.state.stats.activeExperiments = experimentsCount;
            this.state.stats.publishedOutputs = outputsCount + papersCount;

            // Fetch financial metrics only if user has access / budget permissions
            if (this.state.isFinanceOfficer || this.state.isManager) {
                const budgets = await this.orm.searchRead(
                    "project.budget",
                    [],
                    ["total_amount", "spent_amount"]
                );
                let allocated = 0;
                let spent = 0;
                for (const b of budgets) {
                    allocated += b.total_amount || 0;
                    spent += b.spent_amount || 0;
                }
                this.state.stats.totalBudgetAllocated = allocated;
                this.state.stats.totalBudgetSpent = spent;
            }

            // Fetch top 5 recent active projects
            this.state.recentProjects = await this.orm.searchRead(
                "research.project",
                [["project_status", "!=", "archived"]],
                ["id", "code", "project_name", "project_status", "lead_researcher_id", "start_date"],
                { limit: 5, order: "create_date desc" }
            );
        } catch (error) {
            console.error("Failed to load Research Dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    openProject(projectId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "research.project",
            res_id: projectId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    createNewProject() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "research.project",
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("research_dashboard_client_action", ResearchDashboard);
from odoo import http  # type: ignore  # pyfly: ignore [missing-import]
from odoo.http import request  # type: ignore  # pyfly: ignore [missing-import]

class ResearchSupplyChainAPIController(http.Controller):

    @http.route('/api/v1/projects', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_projects(self, **kw):
        """Fetch list of research projects with optional domain filtering."""
        domain = kw.get('domain', [])
        limit = kw.get('limit', 80)
        projects = request.env['research.project'].search_read(
            domain=domain,
            fields=['code', 'project_name', 'project_description', 'lead_researcher_id', 'start_date', 'end_date', 'project_status'],
            limit=limit,
        )
        return {'status': 200, 'count': len(projects), 'data': projects}

    @http.route('/api/v1/project/create', type='json', auth='user', methods=['POST'], csrf=False)
    def api_create_project(self, **kw):
        """Create a new research project record."""
        vals = kw.get('vals', {})
        if not vals.get('project_name'):
            return {'status': 400, 'error': 'Field project_name is required.'}
        
        project = request.env['research.project'].create(vals)
        return {
            'status': 201,
            'message': 'Research project created successfully',
            'project': {
                'id': project.id,
                'code': project.code,
                'project_name': project.project_name,
                'project_status': project.project_status,
            }
        }

    @http.route('/api/v1/researchers', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_researchers(self, **kw):
        """Fetch list of active researchers."""
        limit = kw.get('limit', 80)
        researchers = request.env['research.researcher'].search_read(
            domain=[],
            fields=['name', 'email', 'position', 'expertise', 'is_principal'],
            limit=limit,
        )
        return {'status': 200, 'count': len(researchers), 'data': researchers}

    @http.route('/api/v1/experiments', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_experiments(self, **kw):
        """Fetch list of research experiments."""
        limit = kw.get('limit', 80)
        experiments = request.env['research.experiment'].search_read(
            domain=[],
            fields=['name', 'project_id', 'objective', 'methodology', 'status', 'start_date'],
            limit=limit,
        )
        return {'status': 200, 'count': len(experiments), 'data': experiments}

    @http.route('/api/v1/papers', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_papers(self, **kw):
        """Fetch list of research papers & publications."""
        limit = kw.get('limit', 80)
        papers = request.env['research.paper'].search_read(
            domain=[],
            fields=['paper_name', 'paper_author', 'paper_status', 'paper_doi', 'paper_github_url', 'project_id'],
            limit=limit,
        )
        return {'status': 200, 'count': len(papers), 'data': papers}

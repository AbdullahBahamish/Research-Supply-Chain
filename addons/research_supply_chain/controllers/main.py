import itertools
from odoo import http  # type: ignore  # pyfly: ignore [missing-import]
from odoo.http import request  # type: ignore  # pyfly: ignore [missing-import]

class ResearchSupplyChainAPIController(http.Controller):

    @http.route('/api/v1/projects', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_projects(self, **kw):
        """
        Fetch list of research projects.
        Demonstrates FUNCTIONAL PROGRAMMING (filter, map, lambda).
        """
        domain = kw.get('domain', [])
        limit = kw.get('limit', 80)
        raw_projects = request.env['research.project'].search_read(
            domain=domain,
            fields=['code', 'project_name', 'project_description', 'lead_researcher_id', 'start_date', 'end_date', 'project_status'],
            limit=limit,
        )
        
        # 1. filter() + lambda: Exclude archived projects
        active_projects = list(filter(lambda p: p.get('project_status') != 'archived', raw_projects))

        # 2. map() + lambda: Format code and title for API output
        formatted_data = list(map(lambda p: {
            'id': p['id'],
            'code': p['code'],
            'project_name': p['project_name'].strip().title(),
            'lead_researcher': p['lead_researcher_id'][1] if p.get('lead_researcher_id') else 'Unassigned',
            'status': p['project_status'],
            'start_date': p['start_date'],
            'end_date': p['end_date'],
        }, active_projects))

        return {'status': 200, 'count': len(formatted_data), 'data': formatted_data}

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
        """
        Fetch list of research experiments.
        Demonstrates ITERTOOLS (groupby).
        """
        limit = kw.get('limit', 80)
        experiments = request.env['research.experiment'].search_read(
            domain=[],
            fields=['name', 'project_id', 'objective', 'methodology', 'status', 'start_date'],
            limit=limit,
        )
        
        # Sort by status for itertools.groupby
        sorted_exps = sorted(experiments, key=lambda x: x['status'])
        grouped_result = {}
        for status_key, group in itertools.groupby(sorted_exps, key=lambda x: x['status']):
            grouped_result[status_key] = list(group)

        return {'status': 200, 'count': len(experiments), 'grouped_by_status': grouped_result, 'data': experiments}

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


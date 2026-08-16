import itertools
import logging
from odoo import http  # type: ignore  # pyfly: ignore [missing-import]
from odoo.http import request  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import AccessError, ValidationError, UserError  # type: ignore  # pyfly: ignore [missing-import]

_logger = logging.getLogger(__name__)

class ResearchSupplyChainAPIController(http.Controller):

    @http.route('/api/v1/projects', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_projects(self, **kw):
        """
        Fetch list of research projects with pagination and error handling.
        """
        try:
            domain = kw.get('domain', [])
            limit = min(kw.get('limit', 80), 200)
            offset = kw.get('offset', 0)
            raw_projects = request.env['research.project'].search_read(
                domain=domain,
                fields=['code', 'project_name', 'project_description', 'lead_researcher_id', 'start_date', 'end_date', 'project_status'],
                limit=limit,
                offset=offset,
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

            return {'status': 200, 'count': len(formatted_data), 'offset': offset, 'limit': limit, 'data': formatted_data}
        except AccessError as e:
            return {'status': 403, 'error': str(e)}
        except (ValidationError, UserError) as e:
            return {'status': 422, 'error': str(e)}
        except Exception as e:
            _logger.exception("API Error in api_get_projects")
            return {'status': 500, 'error': 'Internal server error'}

    @http.route('/api/v1/project/create', type='json', auth='user', methods=['POST'], csrf=False)
    def api_create_project(self, **kw):
        """Create a new research project record safely."""
        try:
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
        except AccessError as e:
            return {'status': 403, 'error': str(e)}
        except (ValidationError, UserError) as e:
            return {'status': 422, 'error': str(e)}
        except Exception as e:
            _logger.exception("API Error in api_create_project")
            return {'status': 500, 'error': 'Internal server error'}

    @http.route('/api/v1/researchers', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_researchers(self, **kw):
        """Fetch list of active researchers with pagination."""
        try:
            limit = min(kw.get('limit', 80), 200)
            offset = kw.get('offset', 0)
            researchers = request.env['research.researcher'].search_read(
                domain=[],
                fields=['name', 'email', 'position', 'expertise', 'is_principal'],
                limit=limit,
                offset=offset,
            )
            return {'status': 200, 'count': len(researchers), 'offset': offset, 'limit': limit, 'data': researchers}
        except Exception as e:
            _logger.exception("API Error in api_get_researchers")
            return {'status': 500, 'error': 'Internal server error'}

    @http.route('/api/v1/experiments', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_experiments(self, **kw):
        """
        Fetch list of research experiments grouped by status.
        """
        try:
            limit = min(kw.get('limit', 80), 200)
            offset = kw.get('offset', 0)
            experiments = request.env['research.experiment'].search_read(
                domain=[],
                fields=['name', 'project_id', 'objective', 'methodology', 'status', 'start_date'],
                limit=limit,
                offset=offset,
            )
            
            # Sort by status for itertools.groupby
            sorted_exps = sorted(experiments, key=lambda x: x['status'])
            grouped_result = {}
            for status_key, group in itertools.groupby(sorted_exps, key=lambda x: x['status']):
                grouped_result[status_key] = list(group)

            return {'status': 200, 'count': len(experiments), 'offset': offset, 'limit': limit, 'grouped_by_status': grouped_result, 'data': experiments}
        except Exception as e:
            _logger.exception("API Error in api_get_experiments")
            return {'status': 500, 'error': 'Internal server error'}

    @http.route('/api/v1/papers', type='json', auth='user', methods=['POST'], csrf=False)
    def api_get_papers(self, **kw):
        """Fetch list of research papers & publications."""
        try:
            limit = min(kw.get('limit', 80), 200)
            offset = kw.get('offset', 0)
            papers = request.env['research.paper'].search_read(
                domain=[],
                fields=['paper_name', 'paper_author', 'paper_status', 'paper_doi', 'paper_github_url', 'project_id'],
                limit=limit,
                offset=offset,
            )
            return {'status': 200, 'count': len(papers), 'offset': offset, 'limit': limit, 'data': papers}
        except Exception as e:
            _logger.exception("API Error in api_get_papers")
            return {'status': 500, 'error': 'Internal server error'}

    @http.route('/api/v1/papers/public', type='json', auth='public', methods=['POST', 'GET'], csrf=False)
    def api_public_papers(self, **kw):
        """Public endpoint for external citation of published research papers."""
        try:
            limit = min(kw.get('limit', 50), 100)
            papers = request.env['research.paper'].sudo().search_read(
                domain=[('paper_status', '=', 'published')],
                fields=['paper_name', 'paper_author', 'paper_doi', 'paper_publication_date', 'paper_github_url'],
                limit=limit,
            )
            return {'status': 200, 'count': len(papers), 'data': papers}
        except Exception as e:
            _logger.exception("API Error in api_public_papers")
            return {'status': 500, 'error': 'Internal server error'}

import logging
from odoo import models, api  # type: ignore  # pyfly: ignore [missing-import]

_logger = logging.getLogger(__name__)

class ResearchOWLOntologyExporter(models.AbstractModel):
    _name = "research.owl.exporter"
    _description = "Research Supply Chain Semantic Web OWL / RDF Exporter"

    @api.model
    def export_projects_to_owl_xml(self, project_ids=None):
        """
        Generates a W3C Web Ontology Language (OWL/RDF XML) graph for research projects.
        Enforces security checks so users can only export projects they are permitted to read.
        """
        domain = [('id', 'in', project_ids)] if project_ids else []
        projects = self.env['research.project'].search(domain)

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rdf:RDF',
            '    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"',
            '    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"',
            '    xmlns:owl="http://www.w3.org/2002/07/owl#"',
            '    xmlns:rsc="http://github.com/AbdullahBahamish/Research-Supply-Chain/ontology#">',
            '',
            '  <owl:Ontology rdf:about="http://github.com/AbdullahBahamish/Research-Supply-Chain/ontology">',
            '    <rdfs:label>Research Supply Chain Ontology</rdfs:label>',
            '    <rdfs:comment>Formal OWL representation of research projects, experiments, and outputs.</rdfs:comment>',
            '  </owl:Ontology>',
            '',
            '  <!-- Classes -->',
            '  <owl:Class rdf:about="http://github.com/AbdullahBahamish/Research-Supply-Chain/ontology#ResearchProject"/>',
            '  <owl:Class rdf:about="http://github.com/AbdullahBahamish/Research-Supply-Chain/ontology#Researcher"/>',
            '  <owl:Class rdf:about="http://github.com/AbdullahBahamish/Research-Supply-Chain/ontology#Experiment"/>',
            '',
        ]

        for p in projects:
            xml_lines.append(f'  <rsc:ResearchProject rdf:about="http://github.com/AbdullahBahamish/Research-Supply-Chain/project/{p.id}">')
            xml_lines.append(f'    <rsc:code>{p.code or ""}</rsc:code>')
            xml_lines.append(f'    <rsc:name>{p.project_name or ""}</rsc:name>')
            xml_lines.append(f'    <rsc:status>{p.project_status or ""}</rsc:status>')
            if p.lead_researcher_id:
                xml_lines.append(f'    <rsc:leadResearcher rdf:resource="http://github.com/AbdullahBahamish/Research-Supply-Chain/researcher/{p.lead_researcher_id.id}"/>')
            xml_lines.append('  </rsc:ResearchProject>')
            xml_lines.append('')

        xml_lines.append('</rdf:RDF>')
        return "\n".join(xml_lines)

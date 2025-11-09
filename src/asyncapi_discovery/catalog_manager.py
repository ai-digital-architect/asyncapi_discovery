"""
Catalog Manager - Manages the AsyncAPI specification catalog
Saves, organizes, and reports on generated specifications
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CatalogManager:
    """Manages the catalog of AsyncAPI specifications"""
    
    def __init__(self, output_dir: str = './asyncapi_catalog'):
        """
        Initialize catalog manager
        
        Args:
            output_dir: Directory to store catalog files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.specs_dir = self.output_dir / 'specs'
        self.specs_dir.mkdir(exist_ok=True)
        
        self.reports_dir = self.output_dir / 'reports'
        self.reports_dir.mkdir(exist_ok=True)
        
    def save_catalog(self, specs: List[Dict[str, Any]]) -> None:
        """
        Save all generated specifications to catalog
        
        Args:
            specs: List of specification dictionaries
        """
        logger.info(f"Saving {len(specs)} specifications to catalog")
        
        # Save individual specs
        for spec_data in specs:
            service_name = spec_data['service']
            spec = spec_data['spec']
            
            self._save_spec(service_name, spec)
        
        # Save catalog index
        self._save_catalog_index(specs)
        
        logger.info(f"Catalog saved to {self.output_dir}")
    
    def _save_spec(self, service_name: str, spec: Dict[str, Any]) -> None:
        """Save individual specification in both YAML and JSON formats"""
        # Sanitize service name for filename
        safe_name = self._sanitize_filename(service_name)
        
        # Save as YAML (primary format)
        yaml_path = self.specs_dir / f"{safe_name}.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Saved {yaml_path}")
        
        # Save as JSON (backup format)
        json_path = self.specs_dir / f"{safe_name}.json"
        with open(json_path, 'w') as f:
            json.dump(spec, f, indent=2)
    
    def _save_catalog_index(self, specs: List[Dict[str, Any]]) -> None:
        """Save catalog index with metadata about all specs"""
        index = {
            "generated": datetime.utcnow().isoformat() + "Z",
            "totalServices": len(specs),
            "services": []
        }
        
        for spec_data in specs:
            service_name = spec_data['service']
            spec = spec_data['spec']
            
            # Extract metadata
            info = spec.get('info', {})
            channels = spec.get('channels', {})
            operations = spec.get('operations', {})
            servers = spec.get('servers', {})
            
            index['services'].append({
                "name": service_name,
                "version": info.get('version', '1.0.0'),
                "title": info.get('title', ''),
                "channelCount": len(channels),
                "operationCount": len(operations),
                "brokers": list(servers.keys()),
                "specFiles": {
                    "yaml": f"specs/{self._sanitize_filename(service_name)}.yaml",
                    "json": f"specs/{self._sanitize_filename(service_name)}.json"
                }
            })
        
        # Save index
        index_path = self.output_dir / 'catalog-index.json'
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        logger.info(f"Saved catalog index to {index_path}")
    
    def generate_report(
        self,
        events: List[Dict[str, Any]],
        specs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary report of discovery results
        
        Args:
            events: List of discovered events
            specs: List of generated specifications
            
        Returns:
            Report dictionary
        """
        logger.info("Generating discovery report")
        
        # Analyze events
        brokers = {}
        repositories = set()
        frameworks = {}
        
        for event in events:
            broker = event.get('broker', 'unknown')
            framework = event.get('framework', 'unknown')
            repo = event.get('repository', '')
            
            brokers[broker] = brokers.get(broker, 0) + 1
            frameworks[framework] = frameworks.get(framework, 0) + 1
            if repo:
                repositories.add(repo)
        
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_events": len(events),
                "total_services": len(specs),
                "total_repositories": len(repositories)
            },
            "brokers": brokers,
            "frameworks": frameworks,
            "repositories": sorted(list(repositories)),
            "output_directory": str(self.output_dir.absolute())
        }
        
        # Save report
        report_path = self.reports_dir / f"discovery-report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {report_path}")
        
        # Save human-readable summary
        self._save_text_summary(report)
        
        return report
    
    def _save_text_summary(self, report: Dict[str, Any]) -> None:
        """Save human-readable text summary"""
        summary_lines = [
            "=" * 80,
            "AsyncAPI Discovery Summary",
            "=" * 80,
            "",
            f"Generated: {report['timestamp']}",
            "",
            "Overview:",
            f"  Total Events Discovered: {report['summary']['total_events']}",
            f"  Total Services: {report['summary']['total_services']}",
            f"  Total Repositories: {report['summary']['total_repositories']}",
            "",
            "Message Brokers:",
        ]
        
        for broker, count in sorted(report['brokers'].items()):
            summary_lines.append(f"  {broker}: {count} events")
        
        summary_lines.extend([
            "",
            "Frameworks:",
        ])
        
        for framework, count in sorted(report['frameworks'].items()):
            summary_lines.append(f"  {framework}: {count} events")
        
        summary_lines.extend([
            "",
            "Output Location:",
            f"  {report['output_directory']}",
            "",
            "Generated Files:",
            f"  - {report['summary']['total_services']} AsyncAPI specifications",
            "  - Catalog index: catalog-index.json",
            "  - Discovery reports in reports/",
            "",
            "=" * 80
        ])
        
        summary_path = self.output_dir / 'SUMMARY.txt'
        with open(summary_path, 'w') as f:
            f.write('\n'.join(summary_lines))
        logger.info(f"Summary saved to {summary_path}")
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize service name for use as filename"""
        # Replace special characters
        safe = name.replace('/', '_').replace('\\', '_').replace(' ', '_')
        safe = ''.join(c for c in safe if c.isalnum() or c in ('_', '-'))
        return safe.lower()
    
    def list_specifications(self) -> List[Dict[str, Any]]:
        """List all specifications in the catalog"""
        specs = []
        
        for yaml_file in self.specs_dir.glob('*.yaml'):
            with open(yaml_file) as f:
                spec = yaml.safe_load(f)
                specs.append({
                    'filename': yaml_file.name,
                    'service': spec.get('info', {}).get('title', ''),
                    'version': spec.get('info', {}).get('version', ''),
                    'path': str(yaml_file)
                })
        
        return specs
    
    def get_specification(self, service_name: str) -> Dict[str, Any]:
        """Retrieve a specific specification by service name"""
        safe_name = self._sanitize_filename(service_name)
        yaml_path = self.specs_dir / f"{safe_name}.yaml"
        
        if not yaml_path.exists():
            raise FileNotFoundError(f"Specification not found for {service_name}")
        
        with open(yaml_path) as f:
            return yaml.safe_load(f)
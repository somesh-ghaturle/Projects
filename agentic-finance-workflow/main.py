"""
Main Application Entry Point for Agentic Finance Workflow

This module provides the main application interface with multiple execution modes:
1. Interactive CLI mode for workflow execution
2. Web dashboard for monitoring and management
3. API server for programmatic access
4. Batch processing mode for scheduled workflows
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.orchestrator import OrchestratorAgent, WorkflowDefinition
from agents.cleaner import DataCleanerAgent
from agents import AgentContext
from graphql.server import create_graphql_app
from frontend.dashboard import create_dashboard_app
import uvicorn
import yaml


class AgenticFinanceApplication:
    """
    Main application class for the Agentic Finance Workflow system.
    
    Provides multiple interfaces:
    - CLI for direct workflow execution
    - Web dashboard for monitoring
    - GraphQL API for data access
    - Batch processing capabilities
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.orchestrator = OrchestratorAgent()
        self._setup_agents()
        
        self.logger.info("Initialized Agentic Finance Application")

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load application configuration"""
        default_config = {
            'app': {
                'name': 'Agentic Finance Workflow',
                'version': '1.0.0',
                'environment': 'development'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 1
            },
            'graphql': {
                'port': 4000,
                'debug': True
            },
            'dashboard': {
                'port': 8050,
                'debug': True
            },
            'data': {
                'base_path': './data',
                'cache_ttl': 3600
            },
            'workflows': {
                'default_timeout': 600,
                'max_concurrent': 5,
                'auto_cleanup': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config

    def _setup_logging(self) -> logging.Logger:
        """Setup application logging"""
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format=self.config['logging']['format']
        )
        return logging.getLogger(__name__)

    def _setup_agents(self):
        """Setup and register agent types"""
        # Register available agent types with the orchestrator
        from agents import AgentType
        
        # Add more agent types as they are implemented
        self.orchestrator.register_agent_type(AgentType.CLEANER, DataCleanerAgent)
        
        self.logger.info("Registered agent types with orchestrator")

    async def run_workflow(
        self,
        workflow_path: str,
        input_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow from definition file.
        
        Args:
            workflow_path: Path to workflow YAML definition
            input_data: Input parameters for the workflow
            output_path: Optional path to save results
        
        Returns:
            Workflow execution results
        """
        self.logger.info(f"Starting workflow execution: {workflow_path}")
        
        try:
            # Create execution context
            context = AgentContext(
                environment=self.config['app']['environment'],
                timeout_seconds=self.config['workflows']['default_timeout']
            )
            
            # Prepare orchestrator input
            orchestrator_input = {
                'workflow_definition': workflow_path,
                'input_parameters': input_data,
                'execution_config': {
                    'max_concurrent_agents': self.config['workflows']['max_concurrent'],
                    'auto_cleanup': self.config['workflows']['auto_cleanup']
                }
            }
            
            # Execute workflow
            result = await self.orchestrator.execute(orchestrator_input, context)
            
            # Save results if output path specified
            if output_path and result.success:
                await self._save_results(result.data, output_path)
            
            self.logger.info(f"Workflow execution completed: {result.success}")
            return result.data
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            raise

    async def _save_results(self, results: Dict[str, Any], output_path: str):
        """Save workflow results to file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if output_path.endswith('.json'):
            import json
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        elif output_path.endswith('.yaml'):
            with open(output_path, 'w') as f:
                yaml.dump(results, f, default_flow_style=False)
        else:
            # Default to JSON
            import json
            with open(f"{output_path}.json", 'w') as f:
                json.dump(results, f, indent=2, default=str)

    def start_api_server(self):
        """Start the GraphQL API server"""
        self.logger.info(f"Starting GraphQL API server on port {self.config['graphql']['port']}")
        
        app = create_graphql_app(
            debug=self.config['graphql']['debug'],
            orchestrator=self.orchestrator
        )
        
        uvicorn.run(
            app,
            host=self.config['server']['host'],
            port=self.config['graphql']['port'],
            workers=self.config['server']['workers']
        )

    def start_dashboard(self):
        """Start the web dashboard"""
        self.logger.info(f"Starting web dashboard on port {self.config['dashboard']['port']}")
        
        app = create_dashboard_app(
            debug=self.config['dashboard']['debug'],
            orchestrator=self.orchestrator
        )
        
        app.run_server(
            host=self.config['server']['host'],
            port=self.config['dashboard']['port'],
            debug=self.config['dashboard']['debug']
        )

    async def run_interactive_mode(self):
        """Run interactive CLI mode"""
        print("🤖 Agentic Finance Workflow - Interactive Mode")
        print("=" * 50)
        
        while True:
            try:
                print("\nAvailable workflows:")
                workflows = self._list_workflows()
                for i, workflow in enumerate(workflows, 1):
                    print(f"{i}. {workflow['name']} - {workflow['description']}")
                
                print("\nOptions:")
                print("w) Execute workflow")
                print("s) System status")
                print("h) Health check")
                print("q) Quit")
                
                choice = input("\nEnter your choice: ").lower().strip()
                
                if choice == 'q':
                    print("Goodbye!")
                    break
                elif choice == 'w':
                    await self._interactive_workflow_execution()
                elif choice == 's':
                    await self._show_system_status()
                elif choice == 'h':
                    await self._run_health_check()
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

    def _list_workflows(self) -> list:
        """List available workflow definitions"""
        workflows_dir = project_root / 'workflows'
        workflows = []
        
        for workflow_file in workflows_dir.glob('*.yaml'):
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                    workflows.append({
                        'file': str(workflow_file),
                        'name': workflow_data.get('name', workflow_file.stem),
                        'description': workflow_data.get('description', 'No description available')
                    })
            except Exception as e:
                self.logger.warning(f"Failed to load workflow {workflow_file}: {str(e)}")
        
        return workflows

    async def _interactive_workflow_execution(self):
        """Interactive workflow execution"""
        workflows = self._list_workflows()
        if not workflows:
            print("No workflows available.")
            return
        
        print("\nSelect a workflow:")
        for i, workflow in enumerate(workflows, 1):
            print(f"{i}. {workflow['name']}")
        
        try:
            choice = int(input("Enter workflow number: ")) - 1
            if 0 <= choice < len(workflows):
                selected_workflow = workflows[choice]
                
                # Get input parameters
                print(f"\nSelected: {selected_workflow['name']}")
                input_data = self._get_workflow_inputs()
                
                # Execute workflow
                print("Executing workflow...")
                result = await self.run_workflow(
                    selected_workflow['file'],
                    input_data
                )
                
                print("Workflow completed successfully!")
                print(f"Results: {result}")
                
            else:
                print("Invalid workflow number.")
                
        except ValueError:
            print("Please enter a valid number.")
        except Exception as e:
            print(f"Workflow execution failed: {str(e)}")

    def _get_workflow_inputs(self) -> Dict[str, Any]:
        """Get workflow input parameters from user"""
        inputs = {}
        
        # Basic inputs
        symbol = input("Enter stock symbol (default: AAPL): ").strip() or "AAPL"
        inputs['target_symbol'] = symbol
        
        # Ask for data file path
        data_path = input("Enter data file path (optional): ").strip()
        if data_path:
            inputs['raw_stock_data'] = data_path
        
        return inputs

    async def _show_system_status(self):
        """Show system status"""
        print("\n📊 System Status")
        print("-" * 30)
        
        # Orchestrator status
        orchestrator_health = await self.orchestrator.health_check()
        print(f"Orchestrator: {orchestrator_health['status']}")
        
        # Active executions
        active_count = len(self.orchestrator.active_executions)
        print(f"Active workflows: {active_count}")
        
        # System resources
        import psutil
        print(f"CPU usage: {psutil.cpu_percent()}%")
        print(f"Memory usage: {psutil.virtual_memory().percent}%")
        print(f"Disk usage: {psutil.disk_usage('/').percent}%")

    async def _run_health_check(self):
        """Run system health check"""
        print("\n🏥 Health Check")
        print("-" * 20)
        
        # Check orchestrator
        try:
            health = await self.orchestrator.health_check()
            print(f"✅ Orchestrator: {health['status']}")
        except Exception as e:
            print(f"❌ Orchestrator: {str(e)}")
        
        # Check data directory
        data_dir = Path(self.config['data']['base_path'])
        if data_dir.exists():
            print(f"✅ Data directory: {data_dir}")
        else:
            print(f"❌ Data directory not found: {data_dir}")
        
        # Check workflows directory
        workflows_dir = project_root / 'workflows'
        workflow_count = len(list(workflows_dir.glob('*.yaml')))
        print(f"✅ Workflows available: {workflow_count}")

    async def run_batch_mode(self, batch_config: str):
        """Run batch processing mode"""
        self.logger.info(f"Starting batch processing: {batch_config}")
        
        with open(batch_config, 'r') as f:
            batch_data = yaml.safe_load(f)
        
        for job in batch_data.get('jobs', []):
            try:
                await self.run_workflow(
                    job['workflow'],
                    job.get('input_data', {}),
                    job.get('output_path')
                )
                self.logger.info(f"Completed batch job: {job.get('name', 'unnamed')}")
            except Exception as e:
                self.logger.error(f"Batch job failed: {str(e)}")


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Agentic Finance Workflow System')
    parser.add_argument('--mode', choices=['interactive', 'api', 'dashboard', 'batch'], 
                       default='interactive', help='Application mode')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--workflow', help='Workflow file to execute')
    parser.add_argument('--input', help='Input data file (JSON/YAML)')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--batch', help='Batch configuration file')
    
    args = parser.parse_args()
    
    # Initialize application
    app = AgenticFinanceApplication(args.config)
    
    try:
        if args.mode == 'interactive':
            await app.run_interactive_mode()
        elif args.mode == 'api':
            app.start_api_server()
        elif args.mode == 'dashboard':
            app.start_dashboard()
        elif args.mode == 'batch':
            if not args.batch:
                print("Batch mode requires --batch configuration file")
                sys.exit(1)
            await app.run_batch_mode(args.batch)
        
        # Direct workflow execution
        if args.workflow:
            input_data = {}
            if args.input:
                with open(args.input, 'r') as f:
                    if args.input.endswith('.json'):
                        import json
                        input_data = json.load(f)
                    else:
                        input_data = yaml.safe_load(f)
            
            result = await app.run_workflow(args.workflow, input_data, args.output)
            print("Workflow completed successfully!")
            print(f"Results saved to: {args.output}")
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

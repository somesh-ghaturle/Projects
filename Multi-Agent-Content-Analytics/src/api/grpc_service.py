"""
gRPC Service Implementation for Multi-Agent Content Analytics
"""

import grpc
from concurrent import futures
import asyncio
import logging
from typing import Dict, Any, List
import json
from datetime import datetime

# Import generated protobuf files (would be generated from .proto files)
# For this example, we'll define the service interface
from google.protobuf.message import Message
import sys
import os

# Add the project root to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.agent_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

# Define protobuf message classes (normally generated from .proto files)
class ContentAnalysisRequest:
    """Content analysis request message"""
    def __init__(self):
        self.script_text = ""
        self.text_content = ""
        self.social_media_data = []
        self.metadata = {}
        self.options = {}

class ContentAnalysisResponse:
    """Content analysis response message"""
    def __init__(self):
        self.analysis_id = ""
        self.timestamp = ""
        self.success = False
        self.results = {}
        self.error_message = ""

class SystemStatusRequest:
    """System status request message"""
    def __init__(self):
        pass

class SystemStatusResponse:
    """System status response message"""
    def __init__(self):
        self.orchestrator_initialized = False
        self.agents = []
        self.cache_size = 0
        self.active_tasks = 0
        self.system_health = ""

class AgentStatusMessage:
    """Agent status message"""
    def __init__(self):
        self.name = ""
        self.initialized = False
        self.status = ""
        self.last_execution = ""
        self.error_count = 0

# gRPC Service Implementation
class ContentAnalyticsServiceServicer:
    """gRPC service for content analytics"""
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self._initialized = False
        self.loop = None
    
    async def _ensure_initialized(self):
        """Ensure orchestrator is initialized"""
        if not self._initialized:
            await self.orchestrator.initialize()
            self._initialized = True
    
    def _run_async(self, coro):
        """Run async function in event loop"""
        if self.loop is None:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        
        if self.loop.is_running():
            # Create a new task if loop is already running
            task = asyncio.create_task(coro)
            return asyncio.run_coroutine_threadsafe(coro, self.loop).result()
        else:
            return self.loop.run_until_complete(coro)
    
    def AnalyzeContent(self, request, context):
        """Analyze content using multiple agents"""
        try:
            logger.info("Received gRPC content analysis request")
            
            # Convert gRPC request to internal format
            content_data = self._convert_grpc_request(request)
            
            # Run async analysis
            async def run_analysis():
                await self._ensure_initialized()
                return await self.orchestrator.analyze_content(content_data)
            
            results = self._run_async(run_analysis())
            
            # Convert results to gRPC response
            response = ContentAnalysisResponse()
            response.analysis_id = results.get("analysis_id", "")
            response.timestamp = results.get("timestamp", datetime.now().isoformat())
            response.success = True
            response.results = json.dumps(results)  # Serialize results as JSON
            
            logger.info(f"Completed gRPC content analysis: {response.analysis_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in gRPC content analysis: {str(e)}")
            
            response = ContentAnalysisResponse()
            response.analysis_id = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            response.timestamp = datetime.now().isoformat()
            response.success = False
            response.error_message = str(e)
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Analysis failed: {str(e)}")
            return response
    
    def GetSystemStatus(self, request, context):
        """Get system status"""
        try:
            logger.info("Received gRPC system status request")
            
            # Run async status check
            async def get_status():
                await self._ensure_initialized()
                return await self.orchestrator.get_agent_status()
            
            status_data = self._run_async(get_status())
            
            # Convert to gRPC response
            response = SystemStatusResponse()
            response.orchestrator_initialized = status_data.get("orchestrator_initialized", False)
            response.cache_size = status_data.get("cache_size", 0)
            response.active_tasks = status_data.get("active_tasks", 0)
            
            # Convert agent status
            agents_data = status_data.get("agents", {})
            for agent_name, agent_info in agents_data.items():
                agent_status = AgentStatusMessage()
                agent_status.name = agent_name
                agent_status.initialized = agent_info.get("initialized", False)
                agent_status.status = agent_info.get("status", "unknown")
                agent_status.last_execution = agent_info.get("last_execution", "")
                agent_status.error_count = agent_info.get("error_count", 0)
                response.agents.append(agent_status)
            
            # Determine system health
            if not response.orchestrator_initialized:
                response.system_health = "initializing"
            elif any(not agent.initialized for agent in response.agents):
                response.system_health = "degraded"
            elif any(agent.error_count > 5 for agent in response.agents):
                response.system_health = "unstable"
            else:
                response.system_health = "healthy"
            
            logger.info(f"System status: {response.system_health}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            
            response = SystemStatusResponse()
            response.orchestrator_initialized = False
            response.system_health = "error"
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Status check failed: {str(e)}")
            return response
    
    def InitializeSystem(self, request, context):
        """Initialize the system"""
        try:
            logger.info("Received gRPC system initialization request")
            
            async def initialize():
                await self._ensure_initialized()
                return True
            
            success = self._run_async(initialize())
            
            response = SystemStatusResponse()
            response.orchestrator_initialized = success
            response.system_health = "healthy" if success else "error"
            
            return response
            
        except Exception as e:
            logger.error(f"Error initializing system: {str(e)}")
            
            response = SystemStatusResponse()
            response.orchestrator_initialized = False
            response.system_health = "error"
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Initialization failed: {str(e)}")
            return response
    
    def CleanupSystem(self, request, context):
        """Cleanup the system"""
        try:
            logger.info("Received gRPC system cleanup request")
            
            async def cleanup():
                if self._initialized:
                    await self.orchestrator.cleanup()
                    self._initialized = False
                return True
            
            success = self._run_async(cleanup())
            
            response = SystemStatusResponse()
            response.orchestrator_initialized = False
            response.system_health = "shutdown" if success else "error"
            
            return response
            
        except Exception as e:
            logger.error(f"Error cleaning up system: {str(e)}")
            
            response = SystemStatusResponse()
            response.orchestrator_initialized = False
            response.system_health = "error"
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Cleanup failed: {str(e)}")
            return response
    
    def _convert_grpc_request(self, request: ContentAnalysisRequest) -> Dict[str, Any]:
        """Convert gRPC request to internal format"""
        content_data = {}
        
        if hasattr(request, 'script_text') and request.script_text:
            content_data["script_text"] = request.script_text
        
        if hasattr(request, 'text_content') and request.text_content:
            content_data["text_content"] = request.text_content
        
        if hasattr(request, 'social_media_data') and request.social_media_data:
            content_data["social_media_data"] = list(request.social_media_data)
        
        if hasattr(request, 'metadata') and request.metadata:
            try:
                if isinstance(request.metadata, str):
                    content_data["metadata"] = json.loads(request.metadata)
                else:
                    content_data["metadata"] = dict(request.metadata)
            except (json.JSONDecodeError, TypeError):
                content_data["metadata"] = {}
        
        return content_data

class gRPCServer:
    """gRPC server for content analytics"""
    
    def __init__(self, port: int = 50051, max_workers: int = 10):
        self.port = port
        self.max_workers = max_workers
        self.server = None
        self.servicer = None
    
    def start(self):
        """Start the gRPC server"""
        try:
            self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
            self.servicer = ContentAnalyticsServiceServicer()
            
            # Add servicer to server (normally would use add_ContentAnalyticsServiceServicer_to_server)
            # This would be generated from protobuf files
            # add_ContentAnalyticsServiceServicer_to_server(self.servicer, self.server)
            
            listen_addr = f"[::]:{self.port}"
            self.server.add_insecure_port(listen_addr)
            
            self.server.start()
            logger.info(f"gRPC server started on port {self.port}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start gRPC server: {str(e)}")
            return False
    
    def stop(self, grace_period: int = 5):
        """Stop the gRPC server"""
        if self.server:
            logger.info("Stopping gRPC server...")
            self.server.stop(grace_period)
            
            # Cleanup servicer
            if self.servicer and self.servicer._initialized:
                try:
                    async def cleanup():
                        await self.servicer.orchestrator.cleanup()
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(cleanup())
                    loop.close()
                except Exception as e:
                    logger.error(f"Error during servicer cleanup: {str(e)}")
            
            logger.info("gRPC server stopped")
    
    def wait_for_termination(self):
        """Wait for server termination"""
        if self.server:
            self.server.wait_for_termination()

# Example protobuf definition (content_analytics.proto)
PROTO_DEFINITION = """
syntax = "proto3";

package content_analytics;

// Content analysis service
service ContentAnalyticsService {
    rpc AnalyzeContent(ContentAnalysisRequest) returns (ContentAnalysisResponse);
    rpc GetSystemStatus(SystemStatusRequest) returns (SystemStatusResponse);
    rpc InitializeSystem(SystemStatusRequest) returns (SystemStatusResponse);
    rpc CleanupSystem(SystemStatusRequest) returns (SystemStatusResponse);
}

// Request messages
message ContentAnalysisRequest {
    string script_text = 1;
    string text_content = 2;
    repeated string social_media_data = 3;
    string metadata = 4;  // JSON-encoded metadata
    string options = 5;   // JSON-encoded options
}

message SystemStatusRequest {
    // Empty for now
}

// Response messages
message ContentAnalysisResponse {
    string analysis_id = 1;
    string timestamp = 2;
    bool success = 3;
    string results = 4;  // JSON-encoded results
    string error_message = 5;
}

message SystemStatusResponse {
    bool orchestrator_initialized = 1;
    repeated AgentStatus agents = 2;
    int32 cache_size = 3;
    int32 active_tasks = 4;
    string system_health = 5;
}

message AgentStatus {
    string name = 1;
    bool initialized = 2;
    string status = 3;
    string last_execution = 4;
    int32 error_count = 5;
}
"""

def save_proto_definition(proto_dir: str = "proto"):
    """Save the protobuf definition to a file"""
    import os
    
    if not os.path.exists(proto_dir):
        os.makedirs(proto_dir)
    
    proto_file = os.path.join(proto_dir, "content_analytics.proto")
    with open(proto_file, "w") as f:
        f.write(PROTO_DEFINITION)
    
    logger.info(f"Protobuf definition saved to {proto_file}")
    return proto_file

if __name__ == "__main__":
    # Example usage
    import signal
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start server
    server = gRPCServer(port=50051)
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if server.start():
        logger.info("gRPC server running. Press Ctrl+C to stop.")
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            server.stop()
    else:
        logger.error("Failed to start gRPC server")
        sys.exit(1)

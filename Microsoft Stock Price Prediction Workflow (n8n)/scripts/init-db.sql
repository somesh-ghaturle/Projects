-- Initialize the n8n database for production use
-- This script sets up the basic database structure and configurations

-- Create additional indexes for better performance
CREATE INDEX IF NOT EXISTS idx_execution_entity_workflow_id ON execution_entity(workflowId);
CREATE INDEX IF NOT EXISTS idx_execution_entity_finished ON execution_entity(finished);
CREATE INDEX IF NOT EXISTS idx_execution_entity_started_at ON execution_entity(startedAt);

-- Create a view for workflow statistics
CREATE OR REPLACE VIEW workflow_stats AS
SELECT 
    workflowId,
    COUNT(*) as total_executions,
    COUNT(CASE WHEN finished = true AND data::json->>'error' IS NULL THEN 1 END) as successful_executions,
    COUNT(CASE WHEN finished = true AND data::json->>'error' IS NOT NULL THEN 1 END) as failed_executions,
    AVG(EXTRACT(EPOCH FROM (stoppedAt - startedAt))) as avg_execution_time_seconds
FROM execution_entity 
WHERE startedAt IS NOT NULL
GROUP BY workflowId;

-- Insert initial configuration if needed
-- This would be where you'd add any initial settings or credentials

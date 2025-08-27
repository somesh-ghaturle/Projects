-- Initialize Content Analytics Database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database schema
CREATE SCHEMA IF NOT EXISTS content_analytics;

-- Users table
CREATE TABLE IF NOT EXISTS content_analytics.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Content table
CREATE TABLE IF NOT EXISTS content_analytics.content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL, -- 'script', 'synopsis', 'trailer'
    content_text TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS content_analytics.analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_analytics.content(id),
    agent_name VARCHAR(100) NOT NULL,
    analysis_type VARCHAR(100) NOT NULL,
    results JSONB NOT NULL,
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent execution logs
CREATE TABLE IF NOT EXISTS content_analytics.agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(100) NOT NULL,
    execution_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'started', 'completed', 'failed'
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Embeddings table for vector search
CREATE TABLE IF NOT EXISTS content_analytics.embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_analytics.content(id),
    embedding_type VARCHAR(50) NOT NULL, -- 'sentence', 'document', 'semantic'
    vector_data JSONB NOT NULL,
    dimensions INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_content_type ON content_analytics.content(content_type);
CREATE INDEX IF NOT EXISTS idx_analysis_content_id ON content_analytics.analysis_results(content_id);
CREATE INDEX IF NOT EXISTS idx_analysis_agent ON content_analytics.analysis_results(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent ON content_analytics.agent_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_logs_status ON content_analytics.agent_logs(status);
CREATE INDEX IF NOT EXISTS idx_embeddings_content_id ON content_analytics.embeddings(content_id);

-- Insert sample data
INSERT INTO content_analytics.content (title, content_type, content_text, metadata) VALUES
('Sample Movie Script', 'script', 'FADE IN: EXT. HERO''S JOURNEY - DAY. Our hero begins an epic adventure...', '{"genre": "adventure", "duration": "120min"}'),
('Thriller Synopsis', 'synopsis', 'A mysterious thriller about an AI system that becomes self-aware...', '{"genre": "thriller", "target_audience": "adults"}'),
('Comedy Trailer Script', 'trailer', 'In a world where everything goes wrong, one person will make it right...', '{"genre": "comedy", "duration": "30sec"}')
ON CONFLICT DO NOTHING;

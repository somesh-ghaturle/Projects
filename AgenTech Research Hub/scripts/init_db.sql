#!/bin/bash
# Database initialization script for PostgreSQL

set -e

# Wait for PostgreSQL to be ready
until pg_isready -h localhost -p 5432 -U ${POSTGRES_USER:-agentech}; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready. Initializing database..."

# Create database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-agentech}" --dbname postgres <<-EOSQL
    SELECT 'CREATE DATABASE agentech_research_hub'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'agentech_research_hub')\gexec
EOSQL

# Create tables and initial data
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-agentech}" --dbname agentech_research_hub <<-EOSQL
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        is_superuser BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- API Keys table
    CREATE TABLE IF NOT EXISTS api_keys (
        id SERIAL PRIMARY KEY,
        key_hash VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        user_id INTEGER REFERENCES users(id),
        permissions JSONB DEFAULT '[]',
        rate_limit INTEGER DEFAULT 100,
        is_active BOOLEAN DEFAULT TRUE,
        last_used TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    );

    -- Research Queries table
    CREATE TABLE IF NOT EXISTS research_queries (
        id SERIAL PRIMARY KEY,
        query_text TEXT NOT NULL,
        user_id INTEGER REFERENCES users(id),
        status VARCHAR(50) DEFAULT 'pending',
        results JSONB,
        sources_found INTEGER DEFAULT 0,
        quality_score FLOAT DEFAULT 0.0,
        execution_time FLOAT DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    );

    -- Research Sources table
    CREATE TABLE IF NOT EXISTS research_sources (
        id SERIAL PRIMARY KEY,
        query_id INTEGER REFERENCES research_queries(id),
        source_type VARCHAR(100) NOT NULL,
        title TEXT,
        url TEXT,
        content TEXT,
        relevance_score FLOAT DEFAULT 0.0,
        credibility_score FLOAT DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- System Metrics table
    CREATE TABLE IF NOT EXISTS system_metrics (
        id SERIAL PRIMARY KEY,
        metric_name VARCHAR(255) NOT NULL,
        metric_value FLOAT NOT NULL,
        labels JSONB DEFAULT '{}',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_research_queries_user_id ON research_queries(user_id);
    CREATE INDEX IF NOT EXISTS idx_research_queries_status ON research_queries(status);
    CREATE INDEX IF NOT EXISTS idx_research_queries_created_at ON research_queries(created_at);
    CREATE INDEX IF NOT EXISTS idx_research_sources_query_id ON research_sources(query_id);
    CREATE INDEX IF NOT EXISTS idx_research_sources_source_type ON research_sources(source_type);
    CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
    CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
    CREATE INDEX IF NOT EXISTS idx_system_metrics_name_timestamp ON system_metrics(metric_name, timestamp);

    -- Insert default admin user (password: admin123)
    INSERT INTO users (username, email, hashed_password, is_superuser) 
    VALUES ('admin', 'admin@agentech.com', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE)
    ON CONFLICT (username) DO NOTHING;

    -- Insert demo API key
    INSERT INTO api_keys (key_hash, name, user_id, permissions, rate_limit)
    SELECT 
        'demo-key-123',
        'Demo API Key',
        u.id,
        '["read", "research"]'::jsonb,
        100
    FROM users u 
    WHERE u.username = 'admin'
    ON CONFLICT (key_hash) DO NOTHING;

EOSQL

echo "Database initialization completed successfully!"

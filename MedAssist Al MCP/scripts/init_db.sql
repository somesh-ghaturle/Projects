-- Initialize MedAssist AI Database
-- Create database for medical data storage

-- Create medical agents table
CREATE TABLE IF NOT EXISTS medical_agents (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    configuration JSONB
);

-- Create medical sessions table for HIPAA compliance
CREATE TABLE IF NOT EXISTS medical_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    patient_id VARCHAR(255), -- Anonymized patient ID
    agent_used VARCHAR(100),
    query_type VARCHAR(100),
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

-- Create audit log for HIPAA compliance
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    action_type VARCHAR(100),
    agent_name VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    request_data JSONB,
    response_status INTEGER
);

-- Create medical knowledge base
CREATE TABLE IF NOT EXISTS medical_knowledge (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    content TEXT,
    source VARCHAR(255),
    confidence_score DECIMAL(3,2),
    last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Insert initial medical agents
INSERT INTO medical_agents (agent_name, agent_type, configuration) VALUES
('Diagnostic Agent', 'diagnostic', '{"specialties": ["general_medicine", "symptom_analysis"], "max_response_time": 60}'),
('Pharmacy Agent', 'pharmacy', '{"services": ["drug_interactions", "dosage_info", "side_effects"], "max_response_time": 45}'),
('Radiology Agent', 'radiology', '{"imaging_types": ["xray", "mri", "ct_scan", "ultrasound"], "max_response_time": 90}'),
('Treatment Agent', 'treatment', '{"treatment_types": ["medication", "therapy", "surgery_referral"], "max_response_time": 75}'),
('Emergency Agent', 'emergency', '{"priority": "high", "response_time": 15, "escalation": true}'),
('Enterprise Agent', 'enterprise', '{"scope": ["hospital_management", "patient_flow", "resource_optimization"], "max_response_time": 120}');

-- Create indexes for performance
CREATE INDEX idx_medical_sessions_session_id ON medical_sessions(session_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_medical_knowledge_category ON medical_knowledge(category);
CREATE INDEX idx_medical_agents_type ON medical_agents(agent_type);

-- Create medical specialties reference table
CREATE TABLE IF NOT EXISTS medical_specialties (
    id SERIAL PRIMARY KEY,
    specialty_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    agent_compatibility JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO medical_specialties (specialty_name, description, agent_compatibility) VALUES
('Cardiology', 'Heart and cardiovascular system', '{"diagnostic": true, "treatment": true, "emergency": true}'),
('Neurology', 'Nervous system and brain disorders', '{"diagnostic": true, "radiology": true, "treatment": true}'),
('Oncology', 'Cancer diagnosis and treatment', '{"diagnostic": true, "radiology": true, "treatment": true, "pharmacy": true}'),
('Pediatrics', 'Medical care for children', '{"diagnostic": true, "pharmacy": true, "emergency": true}'),
('Emergency Medicine', 'Acute and emergency care', '{"emergency": true, "diagnostic": true, "treatment": true}'),
('Internal Medicine', 'General adult medical care', '{"diagnostic": true, "treatment": true, "pharmacy": true}');

-- Create system health monitoring table
CREATE TABLE IF NOT EXISTS system_health (
    id SERIAL PRIMARY KEY,
    component_name VARCHAR(100),
    status VARCHAR(20),
    response_time INTEGER, -- in milliseconds
    error_count INTEGER DEFAULT 0,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Grant appropriate permissions
-- Note: In production, create specific users with limited permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO medassist_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO medassist_user;

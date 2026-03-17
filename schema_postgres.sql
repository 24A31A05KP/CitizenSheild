-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'user',
    profile_pic VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Emergency contacts table
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    relationship VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SOS alerts table
CREATE TABLE IF NOT EXISTS sos_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address VARCHAR(500),
    message TEXT,
    status VARCHAR(20) DEFAULT 'active',
    alert_type VARCHAR(20) DEFAULT 'manual',
    notified_contacts INTEGER DEFAULT 0,
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Location shares table
CREATE TABLE IF NOT EXISTS location_shares (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    accuracy FLOAT,
    mode VARCHAR(20) DEFAULT 'live',
    recipients JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Helplines table
CREATE TABLE IF NOT EXISTS helplines (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100),
    service_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample helplines
INSERT INTO helplines (country, service_name, phone_number, description) VALUES
('India', 'Police', '100', 'Emergency police assistance'),
('India', 'Women Helpline', '1091', '24/7 women helpline'),
('India', 'Ambulance', '102', 'Emergency medical services'),
('India', 'Child Helpline', '1098', 'Child protection helpline'),
('India', 'National Emergency Number', '112', 'Unified emergency number'),
('USA', 'Police', '911', 'Emergency services'),
('UK', 'Police', '999', 'Emergency services'),
('Australia', 'Police', '000', 'Emergency services')
ON CONFLICT DO NOTHING;
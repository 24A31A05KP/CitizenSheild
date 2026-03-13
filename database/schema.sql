-- Create database
CREATE DATABASE IF NOT EXISTS secureshe_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE secureshe_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    role ENUM('user', 'admin') DEFAULT 'user',
    profile_pic VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Emergency contacts table
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    relationship VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SOS alerts table
CREATE TABLE IF NOT EXISTS sos_alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address VARCHAR(500),
    message TEXT,
    status ENUM('active', 'resolved', 'false_alarm') DEFAULT 'active',
    alert_type ENUM('manual', 'timer', 'shake') DEFAULT 'manual',
    notified_contacts INT DEFAULT 0,
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_status (user_id, status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SOS notifications table
CREATE TABLE IF NOT EXISTS sos_notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sos_id INT NOT NULL,
    contact_name VARCHAR(100),
    contact_phone VARCHAR(20),
    sent_via ENUM('sms', 'email', 'push') DEFAULT 'sms',
    status ENUM('sent', 'delivered', 'failed') DEFAULT 'sent',
    delivered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sos_id) REFERENCES sos_alerts(id) ON DELETE CASCADE,
    INDEX idx_sos (sos_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Incident reports table
CREATE TABLE IF NOT EXISTS reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    is_anonymous BOOLEAN DEFAULT TRUE,
    incident_type ENUM('unsafe_area', 'harassment', 'assault', 'stalking', 'lack_of_streetlight', 'other') NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location_description VARCHAR(500),
    description TEXT,
    incident_time TIMESTAMP NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    status ENUM('pending', 'verified', 'resolved', 'rejected') DEFAULT 'pending',
    verified_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_location (latitude, longitude),
    INDEX idx_status (status),
    INDEX idx_incident_type (incident_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Helplines table
CREATE TABLE IF NOT EXISTS helplines (
    id INT PRIMARY KEY AUTO_INCREMENT,
    country VARCHAR(100),
    service_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_country (country),
    INDEX idx_service (service_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Resources table (safety tips, articles)
CREATE TABLE IF NOT EXISTS resources (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    category VARCHAR(50),
    content TEXT,
    excerpt VARCHAR(500),
    author VARCHAR(100),
    views INT DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample helplines
INSERT INTO helplines (country, service_name, phone_number, description) VALUES
('India', 'Police', '100', 'Emergency police assistance'),
('India', 'Women Helpline', '1091', '24/7 women helpline'),
('India', 'Ambulance', '102', 'Emergency medical services'),
('India', 'Child Helpline', '1098', 'Child protection helpline'),
('India', 'National Emergency Number', '112', 'Unified emergency number'),
('USA', 'Police', '911', 'Emergency services'),
('UK', 'Police', '999', 'Emergency services'),
('Australia', 'Police', '000', 'Emergency services');

-- Insert sample resources
INSERT INTO resources (title, slug, category, excerpt) VALUES
('Personal Safety Tips', 'personal-safety-tips', 'safety', 'Essential tips for personal safety'),
('Cyber Safety Guide', 'cyber-safety-guide', 'cyber', 'Stay safe online'),
('Self Defense Basics', 'self-defense-basics', 'self-defense', 'Basic self-defense techniques'),
('Travel Safety for Women', 'travel-safety', 'travel', 'Stay safe while traveling');

-- Create admin user (password: Admin@123)
INSERT INTO users (name, email, phone, password_hash, role, is_verified) VALUES
('Admin', 'admin@secureshe.com', '9999999999', '$2b$12$LQvBcJfqJcYhxJqJcYhxJqJcYhxJqJcYhxJqJcYhxJqJcYhxJqJc', 'admin', TRUE);
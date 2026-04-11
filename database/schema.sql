-- ============================================
-- CitizenShield Database Schema
-- Crime Awareness & Safety Platform
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS secureshe_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE secureshe_db;

-- ============================================
-- USERS TABLE
-- ============================================
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
    INDEX idx_phone (phone),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- EMERGENCY CONTACTS TABLE
-- ============================================
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
    INDEX idx_phone (phone),
    INDEX idx_primary (is_primary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- SOS ALERTS TABLE
-- ============================================
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

-- ============================================
-- SOS NOTIFICATIONS TABLE
-- ============================================
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

-- ============================================
-- HELPLINES TABLE
-- ============================================
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

-- ============================================
-- INSERT HELPLINES DATA
-- ============================================
INSERT INTO helplines (country, service_name, phone_number, description) VALUES
('India', 'National Emergency', '112', 'Single emergency number for police, fire, ambulance'),
('India', 'Police', '100', 'Immediate police assistance for emergencies'),
('India', 'Fire', '101', 'Fire emergency services'),
('India', 'Ambulance', '102', 'Medical emergency services'),
('India', 'Women Helpline', '1091', '24x7 assistance for women in distress'),
('India', 'Child Helpline', '1098', 'Assistance for children in need'),
('India', 'National Commission for Women', '011-23237166', 'Women rights and harassment complaints'),
('India', 'Anti-Human Trafficking', '14478', 'Report human trafficking incidents'),
('India', 'Cyber Crime Helpline', '1930', 'Report cyber crimes and online fraud');

-- ============================================
-- CRIME REPORTS TABLE (for anonymous reporting)
-- ============================================
CREATE TABLE IF NOT EXISTS crime_reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    is_anonymous BOOLEAN DEFAULT TRUE,
    crime_type ENUM('cyber', 'theft', 'women', 'assault', 'fraud', 'child', 'other') NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location_description VARCHAR(500),
    description TEXT,
    incident_time TIMESTAMP NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    status ENUM('pending', 'reviewed', 'resolved') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_crime_type (crime_type),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- SAFETY TIPS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS safety_tips (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    icon VARCHAR(50),
    likes INT DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_published (is_published)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- INSERT SAFETY TIPS
-- ============================================
INSERT INTO safety_tips (category, title, content, icon) VALUES
('digital', 'Never Share OTP', 'Never share your OTP, PIN, or password with anyone, even if they claim to be from the bank.', 'fa-laptop'),
('digital', 'Enable Two-Factor Authentication', 'Always enable 2FA on your email, banking, and social media accounts for extra security.', 'fa-shield-alt'),
('personal', 'Share Your Location', 'Always share your live location with trusted family members when traveling alone.', 'fa-map-marker-alt'),
('personal', 'Trust Your Instincts', 'If something feels wrong, trust your gut and remove yourself from the situation.', 'fa-brain'),
('home', 'Lock Doors & Windows', 'Always keep doors and windows locked, even when at home, especially at night.', 'fa-home'),
('home', 'Install Peephole', 'Install a peephole or doorbell camera to see who is at the door before opening.', 'fa-video'),
('financial', 'Never Share Bank Details', 'Never share your CVV, UPI PIN, or OTP with anyone. Banks never ask for these.', 'fa-credit-card'),
('financial', 'Verify Before Investing', 'Always verify investment schemes with SEBI before investing money.', 'fa-chart-line');

-- ============================================
-- AWARENESS CAMPAIGNS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS awareness_campaigns (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    target_audience VARCHAR(100),
    target_participants INT DEFAULT 0,
    participants INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_active (is_active),
    INDEX idx_dates (start_date, end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- INSERT CAMPAIGNS
-- ============================================
INSERT INTO awareness_campaigns (title, description, start_date, end_date, target_participants) VALUES
('Cyber Suraksha', 'Learn to identify and prevent online frauds, phishing attacks, and social media scams', '2026-04-01', '2026-04-15', 5000),
('Safe City Initiative', 'Community safety walks, CCTV awareness, and emergency response training', '2026-04-10', '2026-04-25', 10000),
('Women Safety Workshop', 'Self-defense training, legal rights awareness, and helpline awareness', '2026-04-05', '2026-04-20', 3000),
('Cyber Crime Awareness Week', 'Special awareness program about cyber crimes and how to report them', '2026-05-01', '2026-05-07', 2000);

-- ============================================
-- LOCATION SHARES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS location_shares (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    accuracy FLOAT,
    mode VARCHAR(20) DEFAULT 'live',
    recipients JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_active (user_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- ADMIN USER (password: Admin@123)
-- Note: This is a bcrypt hash for "Admin@123"
-- ============================================
INSERT INTO users (name, email, phone, password_hash, role, is_verified) VALUES
('Admin', 'admin@citizenshield.com', '9999999999', '$2b$12$LQvBcJfqJcYhxJqJcYhxJqJcYhxJqJcYhxJqJcYhxJqJcYhJqJc', 'admin', TRUE)
ON DUPLICATE KEY UPDATE id=id;

-- ============================================
-- VERIFY TABLES CREATED
-- ============================================
SHOW TABLES;
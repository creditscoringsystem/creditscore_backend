-- Create databases for all services
CREATE DATABASE user_service_db;
CREATE DATABASE profile_service_db;
CREATE DATABASE alert_service_db;
CREATE DATABASE survey_service_db;
CREATE DATABASE score_service_db;

-- Grant permissions (optional, since we're using postgres user)
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE profile_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE alert_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE survey_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE score_service_db TO postgres;

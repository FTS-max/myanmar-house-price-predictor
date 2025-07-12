-- Database initialization script for Myanmar House Price Predictor
-- This script sets up the PostgreSQL database with proper extensions and initial configuration

-- Create database if it doesn't exist (this would typically be done outside the script)
-- CREATE DATABASE myanmar_house_prices;

-- Connect to the database
\c myanmar_house_prices;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE property_type_enum AS ENUM (
        'apartment', 'house', 'condo', 'townhouse', 'villa', 'commercial', 'land'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE property_condition_enum AS ENUM (
        'new', 'excellent', 'good', 'fair', 'poor', 'renovation_needed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE location_tier_enum AS ENUM (
        'tier_1', 'tier_2', 'tier_3', 'tier_4'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance (these will be created by SQLAlchemy, but we can add custom ones)
-- Full-text search index for property descriptions
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_description_fts 
--     ON properties USING gin(to_tsvector('english', description));

-- Spatial index for location-based queries (if using PostGIS)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_location 
--     ON properties USING gist(ST_Point(longitude, latitude));

-- Composite index for common query patterns
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_search 
--     ON properties (city, township, property_type, size_sqft);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates (will be applied after table creation)
-- CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
--     FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- CREATE TRIGGER update_market_data_updated_at BEFORE UPDATE ON market_data
--     FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial location tier data
-- This would typically be done after the tables are created by the application

-- Create a view for property statistics
-- CREATE OR REPLACE VIEW property_statistics AS
-- SELECT 
--     city,
--     township,
--     property_type,
--     COUNT(*) as total_properties,
--     AVG(size_sqft) as avg_size_sqft,
--     MIN(size_sqft) as min_size_sqft,
--     MAX(size_sqft) as max_size_sqft,
--     AVG(bedrooms) as avg_bedrooms,
--     AVG(bathrooms) as avg_bathrooms
-- FROM properties
-- GROUP BY city, township, property_type;

-- Create a function for calculating distance between two points
CREATE OR REPLACE FUNCTION calculate_distance(
    lat1 FLOAT, lon1 FLOAT, lat2 FLOAT, lon2 FLOAT
) RETURNS FLOAT AS $$
DECLARE
    R FLOAT := 6371; -- Earth's radius in kilometers
    dLat FLOAT;
    dLon FLOAT;
    a FLOAT;
    c FLOAT;
BEGIN
    dLat := radians(lat2 - lat1);
    dLon := radians(lon2 - lon1);
    
    a := sin(dLat/2) * sin(dLat/2) + 
         cos(radians(lat1)) * cos(radians(lat2)) * 
         sin(dLon/2) * sin(dLon/2);
    
    c := 2 * atan2(sqrt(a), sqrt(1-a));
    
    RETURN R * c;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get nearby properties
CREATE OR REPLACE FUNCTION get_nearby_properties(
    target_lat FLOAT, 
    target_lon FLOAT, 
    radius_km FLOAT DEFAULT 5.0,
    limit_count INTEGER DEFAULT 10
) RETURNS TABLE (
    property_id TEXT,
    distance_km FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        calculate_distance(target_lat, target_lon, p.latitude, p.longitude) as distance
    FROM properties p
    WHERE p.latitude IS NOT NULL 
        AND p.longitude IS NOT NULL
        AND calculate_distance(target_lat, target_lon, p.latitude, p.longitude) <= radius_km
    ORDER BY distance
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create a function to calculate property price trends
CREATE OR REPLACE FUNCTION calculate_price_trends(
    target_city TEXT,
    target_township TEXT DEFAULT NULL,
    target_property_type TEXT DEFAULT NULL,
    months_back INTEGER DEFAULT 12
) RETURNS TABLE (
    month_year TEXT,
    avg_price_mmk FLOAT,
    avg_price_usd FLOAT,
    property_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        TO_CHAR(p.created_at, 'YYYY-MM') as month_year,
        AVG(pred.predicted_price_mmk) as avg_price_mmk,
        AVG(pred.predicted_price_usd) as avg_price_usd,
        COUNT(*)::INTEGER as property_count
    FROM properties p
    JOIN predictions pred ON p.id = pred.property_id
    WHERE p.city = target_city
        AND (target_township IS NULL OR p.township = target_township)
        AND (target_property_type IS NULL OR p.property_type = target_property_type)
        AND p.created_at >= CURRENT_DATE - INTERVAL '1 month' * months_back
    GROUP BY TO_CHAR(p.created_at, 'YYYY-MM')
    ORDER BY month_year;
END;
$$ LANGUAGE plpgsql;

-- Create indexes for performance optimization
-- These will be created after the tables exist

-- Grant permissions (adjust as needed for your deployment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_app_user;

-- Create a maintenance function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data(
    days_to_keep INTEGER DEFAULT 365
) RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Clean up old API usage logs
    DELETE FROM api_usage 
    WHERE timestamp < CURRENT_DATE - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Clean up old predictions (keep only recent ones)
    DELETE FROM predictions 
    WHERE created_at < CURRENT_DATE - INTERVAL '1 day' * (days_to_keep * 2)
        AND id NOT IN (
            SELECT DISTINCT prediction_id 
            FROM some_important_table 
            WHERE prediction_id IS NOT NULL
        );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job for data cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * 0', 'SELECT cleanup_old_data(365);');

COMMIT;

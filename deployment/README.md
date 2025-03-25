# VBot EC2 Deployment Configuration

## Current Issues
- Flask-Limiter weakly-referenced object error
- Port conflicts between production and testing environments
- Nginx configuration conflicts
- SSL certificate configuration issues

## Environment Setup
- Production URL: www.vbot.autos (Port 5001)
- Testing URL: testing.vbot.autos (Port 5002)
- Database: PostgreSQL 14
- Nginx: Configured with SSL

## Scripts
- backup.sh: Database backup script
- debug_env.sh: Environment debugging helper
- vbot_debug.sh: Application debugging script
- vbot_start.sh: Application startup script
- update-app.sh: Application update script
- direct_vbot.py: Direct access debugging script

## Known Configuration Changes
1. Modified Docker port mappings
2. Added testing environment configuration
3. Updated Nginx configurations for both domains
4. Added SSL/TLS settings
5. Modified database connections for testing

## TODO
1. Separate production and testing environments
2. Fix Flask-Limiter configuration
3. Resolve port conflicts
4. Update SSL certificate configuration

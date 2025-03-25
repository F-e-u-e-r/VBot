# Change Log

## [Unreleased] - 2025-03-25
### Added
- Testing environment setup (testing.vbot.autos)
- Nginx configurations for both domains
- SSL/TLS configuration
- Database backup scripts
- Debugging tools and scripts

### Changed
- Modified Docker port mappings (5001 -> 5002 for testing)
- Updated database connections for testing environment
- Modified Nginx configurations for dual-domain setup

### Issues
- Flask-Limiter configuration causing errors
- Port conflicts between environments
- Nginx configuration conflicts
- SSL certificate configuration needs review

### TODO
- Separate production and testing environments
- Fix Flask-Limiter configuration
- Resolve port conflicts
- Update SSL certificate configuration

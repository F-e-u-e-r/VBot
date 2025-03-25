# Nginx Configurations

## Current Setup
- vbot.conf: Production site configuration (www.vbot.autos)
- testing.vbot.autos.conf: Testing site configuration

## SSL Certificates
Location: /etc/nginx/ssl/
- cert.pem
- key.pem

## Known Issues
- Port conflicts between production (5001) and testing (5002)
- Duplicate upstream definitions
- SSL certificate configuration needs review

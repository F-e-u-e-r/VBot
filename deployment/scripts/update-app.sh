   #!/bin/bash
   cd /home/ec2-user/VBot
   
   # Pull latest code
   git pull
   
   # Rebuild and restart containers
   docker-compose down
   docker-compose up -d --build
   
   # Run any migrations
   docker-compose exec web flask db upgrade
   
   echo "Update completed on $(date)" >> /home/ec2-user/update-log.txt

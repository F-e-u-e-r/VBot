   #!/bin/bash
   TIMESTAMP=$(date +%Y%m%d%H%M%S)
   BACKUP_DIR=/home/ec2-user/backups
   
   # Create backup directory if it doesn't exist
   mkdir -p $BACKUP_DIR
   
   # Backup PostgreSQL database
   cd /home/ec2-user/VBot
   docker-compose exec -T db pg_dump -U postgres vbot > $BACKUP_DIR/vbot-db-$TIMESTAMP.sql
   
   # Backup uploaded files
   tar -czf $BACKUP_DIR/vbot-uploads-$TIMESTAMP.tar.gz uploads/
   
   # Keep only the last 7 days of backups
   find $BACKUP_DIR -name "vbot-db-*.sql" -type f -mtime +7 -delete
   find $BACKUP_DIR -name "vbot-uploads-*.tar.gz" -type f -mtime +7 -delete
   
   echo "Backup completed on $(date)" >> $BACKUP_DIR/backup.log

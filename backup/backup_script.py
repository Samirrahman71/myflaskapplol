#!/usr/bin/env python3
"""
Automated backup script with scheduling
Simulates database backups by copying data.json with timestamps
"""

import os
import json
import shutil
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path

# Configure logging with flexible path
backup_log_path = os.getenv('BACKUP_LOG_PATH', './backup/backup.log')
os.makedirs(os.path.dirname(backup_log_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(backup_log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, source_file=None, backup_dir=None):
        # Use environment variables or defaults for flexible deployment
        if source_file is None:
            source_file = os.getenv('SOURCE_FILE', './data/data.json')
        if backup_dir is None:
            backup_dir = os.getenv('BACKUP_DIR', './backup')
        self.source_file = Path(source_file)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self):
        """Create a timestamped backup of the data file"""
        try:
            if not self.source_file.exists():
                logger.warning(f"Source file {self.source_file} does not exist")
                return False
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"data_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename
            
            # Copy the file
            shutil.copy2(self.source_file, backup_path)
            
            # Add backup metadata
            self._add_backup_metadata(backup_path, timestamp)
            
            # Clean old backups (keep last 10)
            self._cleanup_old_backups()
            
            logger.info(f"Backup created successfully: {backup_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False
    
    def _add_backup_metadata(self, backup_path, timestamp):
        """Add metadata to the backup file"""
        try:
            with open(backup_path, 'r') as f:
                data = json.load(f)
            
            # Add backup metadata
            if 'backup_metadata' not in data:
                data['backup_metadata'] = {}
            
            data['backup_metadata'].update({
                'backup_timestamp': timestamp,
                'backup_date': datetime.now().isoformat(),
                'original_file': str(self.source_file),
                'backup_version': '1.0'
            })
            
            with open(backup_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Could not add metadata to backup: {str(e)}")
    
    def _cleanup_old_backups(self, keep_count=10):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backup_files = list(self.backup_dir.glob("data_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if len(backup_files) > keep_count:
                for old_backup in backup_files[keep_count:]:
                    old_backup.unlink()
                    logger.info(f"Removed old backup: {old_backup.name}")
                    
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
    
    def list_backups(self):
        """List all available backups"""
        backup_files = list(self.backup_dir.glob("data_backup_*.json"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        logger.info(f"Found {len(backup_files)} backup files:")
        for backup_file in backup_files:
            mod_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            size = backup_file.stat().st_size
            logger.info(f"  {backup_file.name} - {mod_time} ({size} bytes)")
            
        return backup_files
    
    def restore_backup(self, backup_filename):
        """Restore from a specific backup file"""
        try:
            backup_path = self.backup_dir / backup_filename
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_filename}")
                return False
            
            # Create a backup of current file before restore
            current_backup = f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(self.source_file, self.backup_dir / current_backup)
            
            # Restore the backup
            shutil.copy2(backup_path, self.source_file)
            logger.info(f"Restored from backup: {backup_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return False

def run_scheduled_backups():
    """Run the backup scheduler"""
    backup_manager = BackupManager()
    
    # Schedule backups every 15 minutes
    schedule.every(15).minutes.do(backup_manager.create_backup)
    
    # Also schedule a daily cleanup
    schedule.every().day.at("02:00").do(backup_manager._cleanup_old_backups)
    
    logger.info("Backup scheduler started - running every 15 minutes")
    logger.info("Daily cleanup scheduled at 02:00")
    
    # Run initial backup
    backup_manager.create_backup()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    import sys
    
    backup_manager = BackupManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "backup":
            success = backup_manager.create_backup()
            sys.exit(0 if success else 1)
            
        elif command == "list":
            backup_manager.list_backups()
            
        elif command == "restore" and len(sys.argv) > 2:
            backup_filename = sys.argv[2]
            success = backup_manager.restore_backup(backup_filename)
            sys.exit(0 if success else 1)
            
        elif command == "schedule":
            run_scheduled_backups()
            
        else:
            print("Usage: python backup_script.py [backup|list|restore <filename>|schedule]")
            sys.exit(1)
    else:
        # Default: run scheduler
        run_scheduled_backups()

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from backend.database.connection import SessionLocal
from backend.database.models import Reminder, AuditLog

logger = logging.getLogger(__name__)

class ReminderScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._is_running = False

    def start(self):
        if not self._is_running:
            self.scheduler.add_job(self.check_due_reminders, "interval", seconds=30)
            self.scheduler.start()
            self._is_running = True
            logger.info("Reminder scheduler started.")

    def stop(self):
        if self._is_running:
            self.scheduler.shutdown()
            self._is_running = False
            logger.info("Reminder scheduler stopped.")

    def check_due_reminders(self):
        db = SessionLocal()
        try:
            now = datetime.now()
            due_reminders = db.query(Reminder).filter(
                Reminder.due_datetime <= now,
                Reminder.is_completed == False
            ).all()

            for rem in due_reminders:
                logger.info(f"REMINDER DUE: {rem.title}")
                rem.is_completed = True
                
                # Record in audit log
                audit = AuditLog(
                    event_type="REMINDER_TRIGGER",
                    tool_name="reminder_scheduler",
                    details=f"Reminder triggered: '{rem.title}'",
                    status="SUCCESS",
                    timestamp=datetime.utcnow()
                )
                db.add(audit)

            if due_reminders:
                db.commit()
        except Exception as e:
            logger.error(f"Error checking due reminders: {e}")
            db.rollback()
        finally:
            db.close()

reminder_scheduler = ReminderScheduler()

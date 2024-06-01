"""
Scheduler Service for Periodic Tasks
Handles ML model training, weather updates, and pricing optimization
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional
import schedule

from app.core.config import settings
from app.services.weather_service import WeatherService
from app.services.pricing_service import PricingService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks"""

    def __init__(self):
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.weather_service = WeatherService()
        self.pricing_service = PricingService()

    def start(self):
        """Start the scheduler service"""
        if self.is_running:
            logger.warning("Scheduler service is already running")
            return

        self.is_running = True

        # Schedule periodic tasks
        self._schedule_tasks()

        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

        logger.info("Scheduler service started")

    def stop(self):
        """Stop the scheduler service"""
        self.is_running = False

        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        schedule.clear()
        logger.info("Scheduler service stopped")

    def _schedule_tasks(self):
        """Schedule all periodic tasks"""

        # Weather data updates every 30 minutes
        schedule.every(settings.WEATHER_UPDATE_INTERVAL_MINUTES).minutes.do(
            self._safe_run, self.weather_service.update_weather_data
        )

        # Energy consumption predictions every hour
        schedule.every().hour.do(
            self._safe_run, self._run_energy_predictions
        )

        # Renewable energy forecasts every 2 hours
        schedule.every(2).hours.do(
            self._safe_run, self._run_renewable_forecasts
        )

        # Dynamic pricing optimization every 15 minutes
        schedule.every(15).minutes.do(
            self._safe_run, self.pricing_service.optimize_pricing
        )

        # Model retraining daily at 2 AM
        schedule.every().day.at("02:00").do(
            self._safe_run, self._retrain_models
        )

        # Data cleanup weekly on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(
            self._safe_run, self._cleanup_old_data
        )

        # Grid health check every 5 minutes
        schedule.every(5).minutes.do(
            self._safe_run, self._check_grid_health
        )

        # Billing generation daily at 1 AM (will check if it's the 1st of month)
        schedule.every().day.at("01:00").do(
            self._safe_run, self._generate_monthly_bills
        )

        logger.info("Scheduled tasks configured")

    def _run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("Scheduler loop started")

        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)  # Wait before retrying

        logger.info("Scheduler loop stopped")

    def _safe_run(self, func, *args, **kwargs):
        """Safely run a scheduled function with error handling"""
        try:
            logger.debug(f"Running scheduled task: {func.__name__}")
            func(*args, **kwargs)
            logger.debug(f"Completed scheduled task: {func.__name__}")
        except Exception as e:
            logger.error(f"Error in scheduled task {func.__name__}: {e}")

    def _run_energy_predictions(self):
        """Run energy consumption predictions"""
        try:
            from app.ml.lstm_predictor import LSTMPredictor

            predictor = LSTMPredictor()
            predictor.generate_predictions()

            logger.info("Energy predictions completed")

        except Exception as e:
            logger.error(f"Error running energy predictions: {e}")

    def _run_renewable_forecasts(self):
        """Run renewable energy forecasts"""
        try:
            from app.ml.renewable_forecaster import RenewableForecaster

            forecaster = RenewableForecaster()
            forecaster.generate_solar_forecasts()
            forecaster.generate_wind_forecasts()

            logger.info("Renewable energy forecasts completed")

        except Exception as e:
            logger.error(f"Error running renewable forecasts: {e}")

    def _retrain_models(self):
        """Retrain ML models with latest data"""
        try:
            from app.ml.model_trainer import ModelTrainer

            trainer = ModelTrainer()
            trainer.retrain_lstm_model()
            trainer.retrain_renewable_models()

            logger.info("Model retraining completed")

        except Exception as e:
            logger.error(f"Error retraining models: {e}")

    def _cleanup_old_data(self):
        """Clean up old data to manage storage"""
        try:
            from app.services.data_cleanup_service import DataCleanupService

            cleanup_service = DataCleanupService()
            cleanup_service.cleanup_old_readings()
            cleanup_service.cleanup_old_predictions()
            cleanup_service.cleanup_old_forecasts()

            logger.info("Data cleanup completed")

        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")

    def _check_grid_health(self):
        """Check grid health and generate alerts if needed"""
        try:
            from app.services.grid_monitoring_service import GridMonitoringService

            monitoring_service = GridMonitoringService()
            monitoring_service.check_grid_health()

        except Exception as e:
            logger.error(f"Error checking grid health: {e}")

    def _generate_monthly_bills(self):
        """Generate monthly bills for customers (only on 1st of month)"""
        try:
            from datetime import datetime

            # Only run on the 1st day of the month
            if datetime.now().day != 1:
                return

            from app.services.billing_service import BillingService

            billing_service = BillingService()
            billing_service.generate_monthly_bills()

            logger.info("Monthly billing completed")

        except Exception as e:
            logger.error(f"Error generating monthly bills: {e}")

    def run_task_now(self, task_name: str):
        """Run a specific task immediately"""
        task_map = {
            "weather_update": self.weather_service.update_weather_data,
            "energy_predictions": self._run_energy_predictions,
            "renewable_forecasts": self._run_renewable_forecasts,
            "pricing_optimization": self.pricing_service.optimize_pricing,
            "model_retraining": self._retrain_models,
            "data_cleanup": self._cleanup_old_data,
            "grid_health_check": self._check_grid_health,
            "billing_generation": self._generate_monthly_bills
        }

        if task_name in task_map:
            self._safe_run(task_map[task_name])
            logger.info(f"Manually executed task: {task_name}")
        else:
            logger.error(f"Unknown task: {task_name}")

    def get_next_run_times(self):
        """Get next run times for all scheduled jobs"""
        jobs_info = []
        for job in schedule.jobs:
            jobs_info.append({
                "job": str(job.job_func),
                "next_run": job.next_run.isoformat() if job.next_run else None,
                "interval": str(job.interval),
                "unit": job.unit
            })
        return jobs_info

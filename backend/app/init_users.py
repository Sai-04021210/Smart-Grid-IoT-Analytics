"""
Initialize default users for the application
"""

import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


def init_default_users(db: Session):
    """Initialize default users if they don't exist"""

    try:
        # Check if admin user exists
        admin_exists = db.query(User).filter(User.username == "admin").first()

        if admin_exists:
            logger.info("Admin user already exists")
            return

        # Create default admin user
        admin_user = User(
            username="admin",
            email="admin@smartgrid.local",
            full_name="System Administrator",
            hashed_password=get_password_hash("1234"),
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)

        db.commit()

        logger.info("✅ Default admin user created successfully:")
        logger.info("   - Username: admin")
        logger.info("   - Password: 1234")
        logger.info("   ⚠️  IMPORTANT: Change this password in production!")

    except Exception as e:
        logger.error(f"Error initializing default users: {e}")
        db.rollback()
        raise


if __name__ == "__main__":
    # For standalone execution
    logging.basicConfig(level=logging.INFO)
    db = SessionLocal()
    try:
        init_default_users(db)
    finally:
        db.close()


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
        # Check if any users exist
        user_count = db.query(User).count()
        
        if user_count > 0:
            logger.info(f"Users already initialized ({user_count} users found)")
            return
        
        # Create default admin user
        admin_user = User(
            username="admin",
            email="admin@smartgrid.local",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),  # Change this in production!
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        
        # Create default operator user
        operator_user = User(
            username="operator",
            email="operator@smartgrid.local",
            full_name="Grid Operator",
            hashed_password=get_password_hash("operator123"),  # Change this in production!
            role=UserRole.OPERATOR,
            is_active=True,
            is_superuser=False
        )
        db.add(operator_user)
        
        # Create default viewer user
        viewer_user = User(
            username="viewer",
            email="viewer@smartgrid.local",
            full_name="Grid Viewer",
            hashed_password=get_password_hash("viewer123"),  # Change this in production!
            role=UserRole.VIEWER,
            is_active=True,
            is_superuser=False
        )
        db.add(viewer_user)
        
        db.commit()
        
        logger.info("✅ Default users created successfully:")
        logger.info("   - admin (password: admin123) - Administrator")
        logger.info("   - operator (password: operator123) - Operator")
        logger.info("   - viewer (password: viewer123) - Viewer")
        logger.info("   ⚠️  IMPORTANT: Change these passwords in production!")
        
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


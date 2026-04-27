from app.db.session import SessionLocal
from app.db.models.user import User, UserRole
from app.db.models.account import Account
from app.core.security import hash_password


def main():
    db = SessionLocal()
    if not db.query(User).filter_by(email='admin@example.com').first():
        admin = User(email='admin@example.com', full_name='Admin User', password_hash=hash_password('ChangeMe123!'), role=UserRole.admin)
        user = User(email='user@example.com', full_name='Demo User', password_hash=hash_password('ChangeMe123!'), role=UserRole.user)
        db.add_all([admin, user])
        db.flush()
        db.add_all([
            Account(owner_id=admin.id, account_id='ACCT-DEMOADMIN0001', balance=1000, currency='USD'),
            Account(owner_id=user.id, account_id='ACCT-DEMOUSER0001', balance=500, currency='USD'),
        ])
        db.commit()
    db.close()


if __name__ == '__main__':
    main()

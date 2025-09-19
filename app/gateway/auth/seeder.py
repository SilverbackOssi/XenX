import asyncio
import random
from datetime import datetime, timedelta
from faker import Faker
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.gateway.auth.database import AsyncSessionLocal
from app.gateway.auth.models.users import User, SubscriptionPlans
from app.gateway.enterprises.models.enterprises import Staff, StaffRole, Client, Enterprise, EnterpriseType
from app.config import get_settings

fake = Faker()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

async def clear_database(db: AsyncSession):
    """Clear existing data from all tables."""
    try:
        # Delete in order of dependencies
        await db.execute(text("DELETE FROM clients"))
        await db.execute(text("DELETE FROM staff"))
        await db.execute(text("DELETE FROM enterprises"))
        await db.execute(text("DELETE FROM users"))
        await db.commit()
        print("✅ Database cleared successfully")
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        await db.rollback()

async def create_admin_user(db: AsyncSession) -> User:
    """Create the admin/superuser."""
    admin = User(
        email="testadmin@xentoba.com",
        username="testadmin",
        password_hash=hash_password("Admin@123"),
        first_name="Test",
        last_name="Admin",
        phone_number=fake.phone_number(),
        subscription_plan=SubscriptionPlans.BUSINESS,
        is_active=True,
        is_superuser=True,
        email_verified=True,
        created_at=fake.date_time_between(start_date="-1y", end_date="now"),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    print(f"✅ Created admin user: {admin.email}")
    return admin

async def create_regular_users(db: AsyncSession, count: int = 9) -> list[User]:
    """Create regular users (9 users to make total 10 with admin)."""
    users = []
    
    for i in range(count):
        user = User(
            email=fake.unique.email(),
            username=fake.unique.user_name(),
            password_hash=hash_password("Password@123"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            subscription_plan=random.choice(list(SubscriptionPlans)),
            is_active=True,
            is_superuser=False,
            email_verified=random.choice([True, False]),
            last_login=fake.date_time_between(start_date="-30d", end_date="now") if random.choice([True, False]) else None,
            created_at=fake.date_time_between(start_date="-1y", end_date="now"),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        users.append(user)
    
    await db.commit()
    for user in users:
        await db.refresh(user)
    
    print(f"✅ Created {count} regular users")
    return users

async def create_enterprises(db: AsyncSession, users_with_enterprises: list[User]) -> list[Enterprise]:
    """Create enterprises for specified users."""
    enterprises = []
    
    # First 4 users get 1 enterprise each
    for user in users_with_enterprises[:4]:
        enterprise = Enterprise(
            name=fake.company(),
            email=fake.company_email(),
            description=fake.text(max_nb_chars=200),
            website=fake.url(),
            address=fake.address(),
            country=fake.country(),
            city=fake.city(),
            type=random.choice(list(EnterpriseType)),
            tax_year=datetime.now().year,
            owner_id=user.id,
            is_active=True,
            created_at=fake.date_time_between(start_date="-1y", end_date="now"),
            updated_at=datetime.utcnow()
        )
        
        db.add(enterprise)
        enterprises.append(enterprise)
    
    # Last 2 users get 2 enterprises each (more than one)
    for user in users_with_enterprises[4:6]:
        for _ in range(2):
            enterprise = Enterprise(
                name=fake.company(),
                email=fake.company_email(),
                description=fake.text(max_nb_chars=200),
                website=fake.url(),
                address=fake.address(),
                country=fake.country(),
                city=fake.city(),
                type=random.choice(list(EnterpriseType)),
                tax_year=datetime.now().year,
                owner_id=user.id,
                is_active=True,
                created_at=fake.date_time_between(start_date="-1y", end_date="now"),
                updated_at=datetime.utcnow()
            )
            
            db.add(enterprise)
            enterprises.append(enterprise)
    
    await db.commit()
    for enterprise in enterprises:
        await db.refresh(enterprise)
    
    print(f"✅ Created {len(enterprises)} enterprises")
    return enterprises

async def create_additional_users(db: AsyncSession) -> tuple[list[User], list[User]]:
    """Create 5 additional users (2 will be clients, 3 will be staff)."""
    additional_users = []
    
    for i in range(5):
        user = User(
            email=fake.unique.email(),
            username=fake.unique.user_name(),
            password_hash=hash_password("Password@123"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            subscription_plan=SubscriptionPlans.FREE,  # Additional users start with free plan
            is_active=True,
            is_superuser=False,
            email_verified=random.choice([True, False]),
            created_at=fake.date_time_between(start_date="-6m", end_date="now"),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        additional_users.append(user)
    
    await db.commit()
    for user in additional_users:
        await db.refresh(user)
    
    # Split into clients and staff
    client_users = additional_users[:2]  # First 2 become clients
    staff_users = additional_users[2:]   # Last 3 become staff
    
    print(f"✅ Created 5 additional users (2 future clients, 3 future staff)")
    return client_users, staff_users

async def create_staff_associations(db: AsyncSession, staff_users: list[User], enterprises: list[Enterprise], enterprise_owners: list[User]):
    """Create staff associations for 3 users with enterprises."""
    staff_records = []
    
    # Select 3 enterprise owners who will have staff
    selected_owners = random.sample(enterprise_owners, 3)
    
    for i, staff_user in enumerate(staff_users):
        # Get a random enterprise from the selected owners
        owner = selected_owners[i % len(selected_owners)]
        # Get one of the owner's enterprises
        owner_enterprises = [e for e in enterprises if getattr(e, 'owner_id') == getattr(owner, 'id')]
        enterprise = random.choice(owner_enterprises)
        
        staff = Staff(
            user_id=staff_user.id,
            enterprise_id=enterprise.id,
            inviter_id=owner.id,
            role=random.choice(list(StaffRole)),
            is_active=True,
            created_at=fake.date_time_between(start_date="-3m", end_date="now")
        )
        
        db.add(staff)
        staff_records.append(staff)
    
    await db.commit()
    for staff in staff_records:
        await db.refresh(staff)
    
    print(f"✅ Created {len(staff_records)} staff associations")
    return staff_records

async def create_client_associations(db: AsyncSession, client_users: list[User], enterprises: list[Enterprise], enterprise_owners: list[User]):
    """Create client associations for 2 users with enterprises."""
    client_records = []
    
    # Select 3 enterprise owners who will have clients (can overlap with staff owners)
    selected_owners = random.sample(enterprise_owners, min(3, len(enterprise_owners)))
    
    for i, client_user in enumerate(client_users):
        # Get a random enterprise from the selected owners
        owner = selected_owners[i % len(selected_owners)]
        # Get one of the owner's enterprises
        owner_enterprises = [e for e in enterprises if getattr(e, 'owner_id') == getattr(owner, 'id')]
        enterprise = random.choice(owner_enterprises)
        
        client = Client(
            user_id=client_user.id,
            enterprise_id=enterprise.id,
            inviter_id=owner.id,
            is_active=True,
            created_at=fake.date_time_between(start_date="-3m", end_date="now")
        )
        
        db.add(client)
        client_records.append(client)
    
    await db.commit()
    for client in client_records:
        await db.refresh(client)
    
    print(f"✅ Created {len(client_records)} client associations")
    return client_records

async def seed_database():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Clear existing data
            await clear_database(db)
            
            # Create admin user
            admin = await create_admin_user(db)
            
            # Create 9 regular users (total 10 with admin)
            regular_users = await create_regular_users(db, 9)
            
            # Select 6 users to have enterprises (excluding admin for this example)
            users_with_enterprises = random.sample(regular_users, 6)
            
            # Create enterprises
            enterprises = await create_enterprises(db, users_with_enterprises)
            
            # Create additional 5 users (2 clients, 3 staff)
            client_users, staff_users = await create_additional_users(db)
            
            # Create staff associations
            await create_staff_associations(db, staff_users, enterprises, users_with_enterprises)
            
            # Create client associations
            await create_client_associations(db, client_users, enterprises, users_with_enterprises)
            
            print("🎉 Database seeding completed successfully!")
            print(f"📊 Summary:")
            print(f"   - Total users: 15 (1 admin + 9 regular + 5 additional)")
            print(f"   - Admin user: testadmin@xentoba.com (password: Admin@123)")
            print(f"   - Users with enterprises: 6")
            print(f"   - Total enterprises: {len(enterprises)}")
            print(f"   - Staff members: 3")
            print(f"   - Clients: 2")
            
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await db.rollback()
            raise

async def main():
    """Run the seeder."""
    await seed_database()

if __name__ == "__main__":
    asyncio.run(main())

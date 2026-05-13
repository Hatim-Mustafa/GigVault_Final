import datetime
from auth import hash_password
from database import get_db, init_db
from models import ClientProfile, GigListing, GigStatus, MusicianProfile, User, UserRole

def seed_demo_data() -> None:
    init_db()
    with get_db() as db:
        if db.query(User).filter(User.username == "seniya").first():
            print("Demo data already exists."); return
        client = User(username="seniya", email="seniya@example.com", password_hash=hash_password("seniya"), role=UserRole.CLIENT, city="Karachi", is_active=True)
        musician = User(username="lucky", email="lucky@example.com", password_hash=hash_password("lucky123"), role=UserRole.MUSICIAN, city="Karachi", bio="Session guitarist and vocalist available for live shows.", is_active=True)
        db.add_all([client, musician]); db.flush()
        db.add(ClientProfile(user_id=client.id, venue_name="GigVault Demo Venue", venue_type="Club", genre_specialization="Jazz, Pop, Rock", city="Karachi", capacity=200, description="A demo venue profile for testing GigVault."))
        db.add(MusicianProfile(user_id=musician.id, stage_name="Lucky Live", genres="Jazz, Pop, Rock", instruments="Guitar, Vocals", hourly_rate=75, years_experience=4))
        today = datetime.date.today()
        db.add_all([
            GigListing(client_id=client.id, title="Friday Jazz Night", description="Need a smooth jazz performer for a dinner crowd.", genre="Jazz", city="Karachi", performance_date=today + datetime.timedelta(days=10), start_time=datetime.time(20, 0), duration_hours=3, budget=500, status=GigStatus.OPEN),
            GigListing(client_id=client.id, title="Acoustic Rooftop Set", description="Chill acoustic set for a private event.", genre="Folk", city="Karachi", performance_date=today + datetime.timedelta(days=18), start_time=datetime.time(19, 0), duration_hours=2, budget=350, status=GigStatus.OPEN),
        ])
        print("Demo data seeded. Login: seniya / seniya or lucky / lucky123")

if __name__ == "__main__": seed_demo_data()

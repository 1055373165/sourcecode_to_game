"""
Populate database with sample data for testing and demonstration
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.project import Project, AnalysisStatus
from app.models.level import Level, Challenge
from app.models.achievement import Achievement
from app.core.security import get_password_hash


def populate_sample_data():
    """Populate database with sample data"""
    print("🔧 Initializing database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("⚠️  Database already contains data. Skipping population.")
            return
        
        print("📝 Creating sample users...")
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            total_xp=5000,
            current_level=6
        )
        db.add(admin)
        
        # Create test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("test123"),
            total_xp=1500,
            current_level=2
        )
        db.add(test_user)
        
        db.commit()
        print(f"✅ Created users: admin, testuser")
        
        # Create sample project: Mini-Flask
        print("📚 Creating sample project...")
        
        mini_flask = Project(
            name="Mini-Flask Framework",
            description="Learn how a minimal Flask-like web framework works by exploring its internals",
            language="python",
            github_url="https://github.com/example/mini-flask",
            difficulty=2,
            analysis_status=AnalysisStatus.COMPLETED
        )
        db.add(mini_flask)
        db.commit()
        db.refresh(mini_flask)
        print(f"✅ Created project: {mini_flask.name}")
        
        # Create sample levels
        print("🎯 Creating sample levels...")
        
        level1 = Level(
            project_id=mini_flask.id,
            name="Understanding Request Handling",
            description="Learn how the MiniFlask class handles incoming HTTP requests",
            difficulty=1,
            entry_function="MiniFlask.__call__",
            call_chain=["__call__", "match_route", "Request.__init__"],
            code_snippet="def __call__(self, environ, start_response):\n    request = Request(environ)\n    handler = self.match_route(request.path)\n    ...",
            xp_reward=100,
            estimated_time=10
        )
        db.add(level1)
        
        level2 = Level(
            project_id=mini_flask.id,
            name="Route Decorator Pattern",
            description="Understand how the @app.route decorator registers URL handlers",
            difficulty=2,
            entry_function="MiniFlask.route",
            call_chain=["route", "decorator", "register_route"],
            code_snippet="def route(self, path):\n    def decorator(f):\n        self.routes[path] = f\n        return f\n    return decorator",
            xp_reward=150,
            estimated_time=15
        )
        db.add(level2)
        
        db.commit()
        db.refresh(level1)
        db.refresh(level2)
        print(f"✅ Created {2} levels")
        
        # Create sample challenges for level 1
        print("❓ Creating sample challenges...")
        
        challenge1 = Challenge(
            level_id=level1.id,
            type="multiple_choice",
            question={
                "text": "What is the purpose of the `environ` parameter in the __call__ method?",
                "options": [
                    "A) To store environment variables",
                    "B) To provide HTTP request information",
                    "C) To configure the application",
                    "D) To manage database connections"
                ]
            },
            answer={"correct_option": "B"},
            hints=["Think about WSGI specification", "It contains request headers and path"],
            points=25
        )
        db.add(challenge1)
        
        challenge2 = Challenge(
            level_id=level1.id,
            type="code_tracing",
            question={
                "text": "If a request comes to path '/hello', what function is called first?",
                "code": "app = MiniFlask()\n@app.route('/hello')\ndef hello():\n    return 'Hi'"
            },
            answer={"expected_output": "__call__"},
            hints=["Look at the WSGI entry point"],
            points=25
        )
        db.add(challenge2)
        
        db.commit()
        print(f"✅ Created {2} challenges for level 1")
        
        # Create sample achievements
        print("🏆 Creating sample achievements...")
        
        achievements = [
            Achievement(
                id="first_steps",
                name="First Steps",
                description="Complete your first level",
                icon="🚀",
                category="progression",
                xp_reward=50,
                condition={"type": "levels_completed", "count": 1}
            ),
            Achievement(
                id="perfect_score",
                name="Perfectionist",
                description="Get a perfect score on any level",
                icon="💯",
                category="performance",
                xp_reward=100,
                condition={"type": "perfect_score", "count": 1}
            ),
            Achievement(
                id="project_master",
                name="Project Master",
                description="Complete all levels in a project",
                icon="🎓",
                category="progression",
                xp_reward=200,
                condition={"type": "project_completed", "count": 1}
            )
        ]
        
        for achievement in achievements:
            db.add(achievement)
        
        db.commit()
        print(f"✅ Created {len(achievements)} achievements")
        
        print("\n✨ Sample data populated successfully!")
        print(f"\n📊 Summary:")
        print(f"   Users: 2 (admin/admin123, testuser/test123)")
        print(f"   Projects: 1 (Mini-Flask)")
        print(f"   Levels: 2")
        print(f"   Challenges: 2")
        print(f"   Achievements: {len(achievements)}")
        
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_sample_data()

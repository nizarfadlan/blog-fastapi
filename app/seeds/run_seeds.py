from .seed_roles import seed_roles
from .seed_users import seed_users
from .seed_articles import seed_articles

def run_seeds():
    print("Running all seeds...")
    seed_roles()
    seed_users()
    seed_articles()
    print("All seeds completed.")

if __name__ == "__main__":
    run_seeds()
from .core.config import settings
from .core.setup import create_application
from .routes import routers

app = create_application(routers, settings)
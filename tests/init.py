"""Used for code that should be run before any other test setup code."""

import os

# Used to set the port in the os environment for the postgres container
POSTGRES_CONTAINER_PORT = 5439
os.environ.setdefault("POSTGRES_PORT", str(POSTGRES_CONTAINER_PORT))

os.environ["DISABLE_DOTENV"] = "1"
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("SKIP_PORT_CHECK", "1")

import os
os.environ["LANGFUSE_DEBUG"] = "true"
from langfuse import Langfuse
client = Langfuse(public_key="pk-lf-local-dev", secret_key="sk-lf-local-dev", host="http://langfuse:3000")
trace = client.trace(name="test-trace")
client.flush()

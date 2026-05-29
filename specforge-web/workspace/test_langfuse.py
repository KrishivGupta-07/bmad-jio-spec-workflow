import os
import logging
logging.basicConfig(level=logging.DEBUG)
os.environ["LANGFUSE_DEBUG"] = "true"
os.environ["OTEL_LOG_LEVEL"] = "debug"
from langfuse import Langfuse
client = Langfuse(public_key="pk-lf-local-dev", secret_key="sk-lf-local-dev", host="http://langfuse:3000")
trace_id = client.create_trace_id()
root = client.start_observation(trace_context={"trace_id": trace_id}, name="test")
root.end()
client.flush()

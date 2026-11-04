"""Deprecated compatibility note.

The API Edition no longer generates random packets. Use api_client.fetch_flow_records()
through NetworkSimulation.fetch_from_api() instead.
"""

# Intentionally contains no random traffic generator. This file remains only so
# an older local project folder does not keep a misleading random generator.

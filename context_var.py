import contextvars

wallet_context = contextvars.ContextVar("wallet", default="unknown")
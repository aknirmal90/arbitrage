import os
import importlib


def load_local_variables():
    if os.getenv('SERVER_ENV', None) != 'production':
        try:
            module = importlib.import_module('bin.local_variables')
            env_vars = getattr(module, 'env_vars')
        except Exception:
            return

        for v in env_vars:
            os.environ.setdefault(v, env_vars[v])

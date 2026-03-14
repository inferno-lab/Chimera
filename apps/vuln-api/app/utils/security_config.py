import os
import json
import fcntl

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'security_config.json')

class SecurityConfig:
    """
    Global security configuration for the Chimera API.
    Used to toggle defensive layers for educational purposes.
    Persisted to disk to handle multi-worker Gunicorn deployments.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityConfig, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _get_defaults(self):
        return {
            "sqli_protection": False,
            "csrf_protection": False,
            "ssrf_protection": False,
            "xss_protection": False,
            "bola_protection": False,
            "debug_mode": True
        }

    def _load(self):
        if not os.path.exists(CONFIG_PATH):
            self.update(self._get_defaults())
            return

        try:
            with open(CONFIG_PATH, 'r') as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                data = json.load(f)
                for key, value in data.items():
                    setattr(self, key, value)
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            print(f"Error loading security config: {e}")
            # Fallback to defaults if file is corrupt
            for key, value in self._get_defaults().items():
                setattr(self, key, value)

    def _save(self):
        try:
            data = self.to_dict()
            with open(CONFIG_PATH, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(data, f, indent=2)
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            print(f"Error saving security config: {e}")

    def update(self, config_dict):
        # Reload before update to catch changes from other workers
        self._load()
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._save()

    def to_dict(self):
        # Reload to ensure we have the latest state from other workers
        # This is slightly inefficient but necessary for consistency
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    fcntl.flock(f, fcntl.LOCK_SH)
                    data = json.load(f)
                    fcntl.flock(f, fcntl.LOCK_UN)
                    return data
        except:
            pass
            
        return {
            "sqli_protection": getattr(self, 'sqli_protection', False),
            "csrf_protection": getattr(self, 'csrf_protection', False),
            "ssrf_protection": getattr(self, 'ssrf_protection', False),
            "xss_protection": getattr(self, 'xss_protection', False),
            "bola_protection": getattr(self, 'bola_protection', False),
            "debug_mode": getattr(self, 'debug_mode', True)
        }

    # Add property-style getters to force a reload on every access
    # This ensures consistency across workers without manual _load() calls everywhere
    @property
    def sqli_active(self):
        return self.to_dict().get('sqli_protection', False)

    @property
    def bola_active(self):
        return self.to_dict().get('bola_protection', False)

# Global singleton instance
security_config = SecurityConfig()

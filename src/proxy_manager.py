import asyncio
import random
import time
from typing import Optional, Dict, List
from dataclasses import dataclass
import httpx

@dataclass
class ProxyConfig:
    """Configuration for a single proxy"""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    max_failures: int = 3
    timeout: int = 30

class ProxyRotationManager:
    """Manages proxy rotation with failure tracking and fallback"""
    
    def __init__(self, proxy_configs: List[ProxyConfig]):
        # Ensure all configs are ProxyConfig objects
        self.proxy_configs = []
        for config in proxy_configs:
            if isinstance(config, dict):
                # Convert dictionary to ProxyConfig object
                self.proxy_configs.append(ProxyConfig(
                    url=config.get("url", ""),
                    username=config.get("username"),
                    password=config.get("password"),
                    max_failures=config.get("max_failures", 3),
                    timeout=config.get("timeout", 30)
                ))
            else:
                self.proxy_configs.append(config)
                
        self.proxy_failures = {}  # Track failures per proxy
        self.proxy_last_used = {}  # Track last usage time
        self.current_proxy_index = 0
        self.lock = asyncio.Lock()
        
        # Initialize failure tracking
        for i, config in enumerate(self.proxy_configs):
            self.proxy_failures[i] = 0
            self.proxy_last_used[i] = 0
    
    def get_proxy_dict(self, config: ProxyConfig) -> Dict[str, str]:
        """Convert ProxyConfig to httpx proxy dictionary format"""
        # Handle case where config might be a dictionary instead of ProxyConfig object
        if isinstance(config, dict):
            url = config.get("url", "")
            username = config.get("username")
            password = config.get("password")
        else:
            # Standard ProxyConfig object
            url = config.url
            username = config.username
            password = config.password
            
        # Check if URL already contains credentials (user:pass@host format)
        has_credentials = '@' in url and ':' in url.split('@', 1)[0]
        
        if username and password and not has_credentials:
            # Format: http://username:password@host:port
            proxy_url = url
            if not proxy_url.startswith('http'):
                proxy_url = f"http://{proxy_url}"
            
            # Parse the URL to insert credentials
            if '@' not in proxy_url:
                # Insert credentials before the host
                if '://' in proxy_url:
                    protocol, rest = proxy_url.split('://', 1)
                    proxy_url = f"{protocol}://{username}:{password}@{rest}"
                else:
                    proxy_url = f"http://{username}:{password}@{proxy_url}"
        else:
            # Use URL as-is (either no credentials or already has them)
            proxy_url = url
            if not proxy_url.startswith('http'):
                proxy_url = f"http://{proxy_url}"
        
        return {
            "http://": proxy_url,
            "https://": proxy_url
        }
    
    async def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next available proxy, rotating through the list"""
        async with self.lock:
            if not self.proxy_configs:
                return None
            
            # Try to find a working proxy
            for attempt in range(len(self.proxy_configs)):
                proxy_index = self.current_proxy_index
                config = self.proxy_configs[proxy_index]
                
                # Skip if proxy has too many failures
                if self.proxy_failures[proxy_index] >= config.max_failures:
                    self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_configs)
                    continue
                
                # Skip if proxy was used very recently (rate limiting)
                current_time = time.time()
                time_since_last_use = current_time - self.proxy_last_used[proxy_index]
                if time_since_last_use < 1.0:  # Wait at least 1 second between uses
                    self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_configs)
                    continue
                
                # Mark this proxy as used
                self.proxy_last_used[proxy_index] = current_time
                self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_configs)
                
                return self.get_proxy_dict(config)
            
            # No working proxies found, reset failures and try again
            for i in range(len(self.proxy_configs)):
                self.proxy_failures[i] = 0
            
            # Return the first proxy as fallback
            if self.proxy_configs:
                config = self.proxy_configs[0]
                self.proxy_last_used[0] = time.time()
                return self.get_proxy_dict(config)
            
            return None
    
    async def mark_proxy_failed(self, proxy_dict: Dict[str, str]):
        """Mark a proxy as failed"""
        async with self.lock:
            # Find which proxy this corresponds to
            for i, config in enumerate(self.proxy_configs):
                expected_dict = self.get_proxy_dict(config)
                if expected_dict == proxy_dict:
                    # Handle case where config might be a dictionary
                    if isinstance(config, dict):
                        max_failures = config.get("max_failures", 3)
                    else:
                        max_failures = config.max_failures
                    self.proxy_failures[i] += 1
                    debug_print(f"❌ Proxy {i} marked as failed ({self.proxy_failures[i]}/{max_failures} failures)")
                    break
    
    async def mark_proxy_success(self, proxy_dict: Dict[str, str]):
        """Mark a proxy as successful (reset failures)"""
        async with self.lock:
            # Find which proxy this corresponds to
            for i, config in enumerate(self.proxy_configs):
                expected_dict = self.get_proxy_dict(config)
                if expected_dict == proxy_dict:
                    if self.proxy_failures[i] > 0:
                        debug_print(f"✅ Proxy {i} marked as successful (resetting failures)")
                        self.proxy_failures[i] = 0
                    break
    
    def get_stats(self) -> Dict:
        """Get statistics about proxy usage"""
        total_proxies = len(self.proxy_configs)
        working_proxies = 0
        for i in range(total_proxies):
            # Handle case where config might be a dictionary
            if isinstance(self.proxy_configs[i], dict):
                max_failures = self.proxy_configs[i].get("max_failures", 3)
            else:
                max_failures = self.proxy_configs[i].max_failures
            if self.proxy_failures[i] < max_failures:
                working_proxies += 1
        failed_proxies = total_proxies - working_proxies
        
        return {
            "total_proxies": total_proxies,
            "working_proxies": working_proxies,
            "failed_proxies": failed_proxies,
            "failure_counts": {i: self.proxy_failures[i] for i in range(total_proxies)},
            "last_used": {i: self.proxy_last_used[i] for i in range(total_proxies)}
        }

# Global proxy manager instance
proxy_manager: Optional[ProxyRotationManager] = None

def init_proxy_manager(proxy_configs: List[ProxyConfig]):
    """Initialize the global proxy manager"""
    global proxy_manager
    proxy_manager = ProxyRotationManager(proxy_configs)
    debug_print(f"✅ Proxy manager initialized with {len(proxy_configs)} proxies")

def get_proxy_manager() -> Optional[ProxyRotationManager]:
    """Get the global proxy manager"""
    return proxy_manager

# Import debug_print from main
def debug_print(*args, **kwargs):
    """Import debug_print from main module"""
    try:
        from main import debug_print as main_debug_print
        main_debug_print(*args, **kwargs)
    except ImportError:
        # Fallback if main module not available
        print(*args, **kwargs)

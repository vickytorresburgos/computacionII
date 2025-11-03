from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import base64
from typing import Dict, Any

def take_screenshot_and_performance(url: str, timeout: int = 20000) -> Dict[str, Any]:
    """
    Captura pantalla completa y métricas de rendimiento usando Playwright.
    Reemplaza a screenshot.py y performance.py.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            response = page.goto(url, timeout=timeout, wait_until='load')
            status_code = response.status if response else 0

            timing = page.evaluate("() => window.performance.timing.toJSON()")
            resources = page.evaluate("() => window.performance.getEntriesByType('resource')")
            
            performance_data = {}
            if timing and resources is not None:
                load_ms = timing['loadEventEnd'] - timing['navigationStart']
                
                performance_data['load_time_ms'] = max(load_ms, 0)
                                
                total_size = sum(r.get('transferSize', 0) for r in resources)
                performance_data['total_size_kb'] = round(total_size / 1024, 2)

                performance_data['num_requests'] = len(resources) + 1 

            else:
                performance_data = {
                    'load_time_ms': 0,
                    'total_size_kb': 0,
                    'num_requests': 0,
                }

            performance_data['status_code'] = status_code
            
            buf = page.screenshot(full_page=True)
            screenshot_b64 = base64.b64encode(buf).decode('ascii')
            
            browser.close()
            
            return {
                "screenshot": screenshot_b64,
                "performance": performance_data
            }
            
        except PlaywrightTimeoutError:
            browser.close()
            print(f"[Playwright] Timeout para {url}")
            raise Exception(f"Timeout ({timeout}ms) al cargar la URL: {url}")
        except Exception as e:
            browser.close()
            print(f"[Playwright] Error para {url}: {e}")
            raise Exception(f"Error de Playwright: {str(e)}")
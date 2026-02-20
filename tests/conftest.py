import pytest
import os
import base64
from datetime import datetime

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Extends the PyTest Plugin to take and embed screenshot in html report,
    whenever test fails or after specific stages.
    """
    pytest_html = item.config.pluginmanager.get_plugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    if report.when == 'call':
        driver = item.funcargs.get('driver')
        if driver:
            # Capture screenshot
            screenshot_bin = driver.get_screenshot_as_base64()
            # Embed image in HTML report
            extra.append(pytest_html.extras.image(screenshot_bin, 'Screenshot'))
        
        report.extra = extra

import pytest
import sys

sys.path.append("..")
from ppsctrl.ppsctrl_phrases import PPSCtrl_Phrases
from ppsctrl.traceclient import TraceClient

DEFAULT_TARGET_HOST = "127.0.0.1"


# Add custom Pytest command line options
def pytest_addoption(parser):
    parser.addoption(
        "--target-host",
        action="store",
        default=DEFAULT_TARGET_HOST,
        help=f"Address of the target host. Default is {DEFAULT_TARGET_HOST}.",
    )


@pytest.fixture(scope="session")
def ppsctrl_dut(request):
    """Create a device-under-test (dut) instance, for interface remotely with the dut over the TraceClientProtocol.
    The default target address can be overridden by using the --target-host Pytest command line option.
    """
    traceclient = TraceClient.get_trace_client(request)
    assert not traceclient is None
    return PPSCtrl_Phrases(traceclient)

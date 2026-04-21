import sys
from pathlib import Path

import pytest


ALGORITHM_CHOICES = (
    "backtracking",
    "brute_force",
    "a_star",
    "forward_chaining",
    "backward_chaining",
    "sat",
    "all",
)

SUPPORTED_ALGORITHMS = (
    "backtracking",
    "brute_force",
    "a_star",
    "forward_chaining",
    "backward_chaining",
    "sat",
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--algo",
        action="store",
        default="backtracking",
        choices=ALGORITHM_CHOICES,
        help=(
            "Algorithm to test: backtracking, brute_force, a_star, "
            "forward_chaining, backward_chaining, sat, all"
        ),
    )


@pytest.fixture
def selected_algo(request: pytest.FixtureRequest) -> str:
    return str(request.config.getoption("--algo"))


@pytest.fixture
def selected_algorithms(selected_algo: str) -> tuple[str, ...]:
    if selected_algo == "all":
        return SUPPORTED_ALGORITHMS
    return (selected_algo,)


def _format_case_label(nodeid: str) -> str:
    if "[" in nodeid and "]" in nodeid:
        label = nodeid.split("[", 1)[1].rsplit("]", 1)[0]
    else:
        label = nodeid.rsplit("::", 1)[-1]

    if label.endswith(".txt"):
        label = Path(label).stem

    return label.replace("-", "_")


def pytest_report_teststatus(report: pytest.TestReport, config: pytest.Config):
    if report.when == "call" and report.passed:
        # Hide the default green-dot progress marker for passed test calls.
        return "passed", "", "passed"
    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    terminal_reporter = item.config.pluginmanager.get_plugin("terminalreporter")
    if terminal_reporter is None:
        return

    case_label = _format_case_label(item.nodeid)
    if report.passed:
        terminal_reporter.write_line(f"finish {case_label}")

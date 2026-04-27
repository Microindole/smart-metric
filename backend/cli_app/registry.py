from __future__ import annotations

from .commands.ai_review_command import AIReviewCommand
from .commands.cfg_graph_command import CfgGraphCommand
from .commands.cfg_source_command import CfgSourceCommand
from .commands.estimate_command import EstimateCommand
from .commands.fp_command import FunctionPointCommand
from .commands.help_command import HelpCommand
from .commands.oo_diagram_command import OoDiagramCommand
from .commands.oo_source_command import OoSourceCommand
from .commands.project_command import ProjectCommand
from .commands.project_report_command import ProjectReportCommand
from .commands.report_command import ReportCommand
from .commands.serve_command import ServeCommand
from .commands.test_backend_command import TestBackendCommand
from .commands.test_path_command import TestPathCommand


def build_command_registry():
    return {
        "help": HelpCommand(),
        "serve": ServeCommand(),
        "ai-review": AIReviewCommand(),
        "oo-source": OoSourceCommand(),
        "oo-diagram": OoDiagramCommand(),
        "fp": FunctionPointCommand(),
        "project-scan": ProjectCommand(),
        "project-report": ProjectReportCommand(),
        "report": ReportCommand(),
        "cfg-source": CfgSourceCommand(),
        "cfg-graph": CfgGraphCommand(),
        "estimate": EstimateCommand(),
        "test.backend": TestBackendCommand(),
        "test.path": TestPathCommand(),
    }

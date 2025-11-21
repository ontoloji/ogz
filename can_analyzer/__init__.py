"""
CAN Bus Analyzer Package
Windows için Python tabanl1 CAN Bus veri analiz arac1
"""

__version__ = "1.0.0"
__author__ = "CAN Tools Developer"
__description__ = "Windows CAN Bus Data Analysis Tool with Kvaser Support"

# Core modüller
from .core.can_handler import CANHandler
from .core.dbc_parser import DBCParser
from .core.log_reader import LogReader
from .core.data_exporter import DataExporter

# GUI modülleri
from .gui.main_window import MainWindow
from .gui.plot_widget import PlotWidget

__all__ = [
    'CANHandler',
    'DBCParser',
    'LogReader',
    'DataExporter',
    'MainWindow',
    'PlotWidget',
]

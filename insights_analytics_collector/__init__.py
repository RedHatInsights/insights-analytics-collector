from .collector import Collector
from .package import Package
from .file_splitter import FileSplitter
from .decorators import register, slicing

__all__ = ['Collector', 'Package', 'FileSplitter', 'register', 'slicing']

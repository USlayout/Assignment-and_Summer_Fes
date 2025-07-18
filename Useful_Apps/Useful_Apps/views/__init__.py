# views/__init__.py - 各機能のビューをまとめてインポート

from .base_views import top_page
from .image_views import image_combine
from .qr_views import qr_generator, download_qr
from .color_views import color_tools

# 将来追加予定の機能
# from .password_views import password_generator
# from .dictionary_views import dictionary_search
# from .text_views import text_converter
# from .data_views import data_visualizer

__all__ = [
    'top_page',
    'image_combine', 
    'qr_generator',
    'download_qr',
    'color_tools',
]

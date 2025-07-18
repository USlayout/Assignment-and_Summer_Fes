# views.py - メインビューファイル（モジュール化されたビューをインポート）

# 各機能別のビューをインポート
from .views.base_views import top_page
from .views.image_views import image_combine, resize_images, combine_images_by_direction
from .views.qr_views import qr_generator, download_qr, get_data_capacity
from .views.color_views import color_tools

# 後方互換性のために全ての関数をこのモジュールで利用可能にする
__all__ = [
    'top_page',
    'image_combine', 
    'resize_images', 
    'combine_images_by_direction',
    'qr_generator', 
    'download_qr', 
    'get_data_capacity',
    'color_tools'
]

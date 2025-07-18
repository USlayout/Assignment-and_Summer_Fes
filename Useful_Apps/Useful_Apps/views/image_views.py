"""
image_views.py - 画像処理関連のビュー（画像結合機能）
"""

from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image
import io
import base64
import math


def image_combine(request):
    """画像結合機能のメインビュー"""
    if request.method == 'POST':
        try:
            # アップロードされた画像を取得
            images = request.FILES.getlist('images')
            if not images:
                return JsonResponse({'success': False, 'error': '画像が選択されていません'})
            
            # 設定を取得
            direction = request.POST.get('direction', 'horizontal')
            resize_method = request.POST.get('resize_method', 'min')
            grid_cols = int(request.POST.get('grid_cols', 2))
            fixed_width = int(request.POST.get('fixed_width', 300))
            fixed_height = int(request.POST.get('fixed_height', 300))
            is_preview = request.POST.get('is_preview', 'false').lower() == 'true'
            
            # PIL Imageオブジェクトに変換
            pil_images = []
            for img_file in images:
                try:
                    img = Image.open(img_file)
                    # RGBモードに変換（JPEGで保存するため）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    pil_images.append(img)
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'画像の読み込みに失敗しました: {str(e)}'})
            
            # 画像をリサイズ
            resized_images = resize_images(pil_images, direction, resize_method, fixed_width, fixed_height, grid_cols)
            if not resized_images:
                return JsonResponse({'success': False, 'error': '画像のリサイズに失敗しました'})
            
            # 画像を結合
            combined_image = combine_images_by_direction(resized_images, direction, grid_cols)
            if not combined_image:
                return JsonResponse({'success': False, 'error': '画像の結合に失敗しました'})
            
            # 画像をBase64エンコード
            img_buffer = io.BytesIO()
            combined_image.save(img_buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            return JsonResponse({
                'success': True,
                'image_data': img_str,
                'width': combined_image.width,
                'height': combined_image.height,
                'is_preview': is_preview
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'処理中にエラーが発生しました: {str(e)}'})
    
    return render(request, 'image_combine.html')


def resize_images(images, direction, resize_method, fixed_width, fixed_height, grid_cols):
    """設定に応じて画像をリサイズ"""
    try:
        if resize_method == "fixed":
            # 固定サイズ
            return [img.resize((fixed_width, fixed_height), Image.Resampling.LANCZOS) for img in images]
        
        elif resize_method == "min":
            if direction == "horizontal":
                # 横並びの場合は高さを統一
                min_height = min(img.height for img in images)
                return [img.resize((int(img.width * min_height / img.height), min_height), Image.Resampling.LANCZOS) 
                       for img in images]
            elif direction == "vertical":
                # 縦並びの場合は幅を統一
                min_width = min(img.width for img in images)
                return [img.resize((min_width, int(img.height * min_width / img.width)), Image.Resampling.LANCZOS) 
                       for img in images]
            else:  # grid
                # グリッドの場合は最小の寸法に統一
                min_width = min(img.width for img in images)
                min_height = min(img.height for img in images)
                size = min(min_width, min_height)
                return [img.resize((size, size), Image.Resampling.LANCZOS) for img in images]
        
        elif resize_method == "max":
            if direction == "horizontal":
                # 横並びの場合は高さを統一
                max_height = max(img.height for img in images)
                return [img.resize((int(img.width * max_height / img.height), max_height), Image.Resampling.LANCZOS) 
                       for img in images]
            elif direction == "vertical":
                # 縦並びの場合は幅を統一
                max_width = max(img.width for img in images)
                return [img.resize((max_width, int(img.height * max_width / img.width)), Image.Resampling.LANCZOS) 
                       for img in images]
            else:  # grid
                # グリッドの場合は最大の寸法に統一
                max_width = max(img.width for img in images)
                max_height = max(img.height for img in images)
                size = max(max_width, max_height)
                return [img.resize((size, size), Image.Resampling.LANCZOS) for img in images]
        
        return images
    except Exception:
        return None


def combine_images_by_direction(images, direction, grid_cols):
    """結合方向に応じて画像を結合"""
    try:
        if direction == "horizontal":
            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)
            combined = Image.new('RGB', (total_width, max_height), 'white')
            
            x_offset = 0
            for img in images:
                combined.paste(img, (x_offset, 0))
                x_offset += img.width
        
        elif direction == "vertical":
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)
            combined = Image.new('RGB', (max_width, total_height), 'white')
            
            y_offset = 0
            for img in images:
                combined.paste(img, (0, y_offset))
                y_offset += img.height
        
        else:  # grid
            rows = math.ceil(len(images) / grid_cols)
            
            img_width = images[0].width
            img_height = images[0].height
            
            grid_width = grid_cols * img_width
            grid_height = rows * img_height
            
            combined = Image.new('RGB', (grid_width, grid_height), 'white')
            
            for i, img in enumerate(images):
                row = i // grid_cols
                col = i % grid_cols
                x = col * img_width
                y = row * img_height
                combined.paste(img, (x, y))
        
        return combined
        
    except Exception:
        return None

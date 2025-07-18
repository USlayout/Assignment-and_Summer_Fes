from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from PIL import Image
import io
import base64
import math
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

def top_page(request):
    return render(request, 'top_page.html')

def image_combine(request):
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


def qr_generator(request):
    """QRコード生成機能のメインビュー"""
    if request.method == 'POST':
        try:
            # フォームデータを取得
            text = request.POST.get('text', '').strip()
            qr_type = request.POST.get('qr_type', 'text')
            size = int(request.POST.get('size', 10))
            border = int(request.POST.get('border', 4))
            error_correction = request.POST.get('error_correction', 'M')
            fill_color = request.POST.get('fill_color', 'black')
            back_color = request.POST.get('back_color', 'white')
            
            # 入力チェック
            if not text:
                return JsonResponse({'success': False, 'error': 'テキストを入力してください'})
            
            # QRコードタイプに応じてテキストを処理
            if qr_type == 'url':
                if not text.startswith(('http://', 'https://')):
                    text = 'https://' + text
            elif qr_type == 'email':
                if '@' in text:
                    text = f'mailto:{text}'
            elif qr_type == 'phone':
                text = f'tel:{text}'
            elif qr_type == 'sms':
                text = f'sms:{text}'
            elif qr_type == 'wifi':
                # WiFi形式: WIFI:T:WPA;S:ネットワーク名;P:パスワード;;
                parts = text.split(',')
                if len(parts) >= 2:
                    ssid = parts[0].strip()
                    password = parts[1].strip()
                    security = parts[2].strip() if len(parts) > 2 else 'WPA'
                    text = f'WIFI:T:{security};S:{ssid};P:{password};;'
            
            # エラー訂正レベルの設定
            error_levels = {
                'L': ERROR_CORRECT_L,  # 約7%
                'M': ERROR_CORRECT_M,  # 約15%
                'Q': ERROR_CORRECT_Q,  # 約25%
                'H': ERROR_CORRECT_H   # 約30%
            }
            error_correct_level = error_levels.get(error_correction, ERROR_CORRECT_M)
            
            # QRコード生成
            qr = qrcode.QRCode(
                version=1,  # 自動サイズ調整
                error_correction=error_correct_level,
                box_size=size,
                border=border,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # 画像生成
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # Base64エンコード
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # QRコード情報
            qr_info = {
                'version': qr.version,
                'data_capacity': get_data_capacity(qr.version, error_correct_level),
                'error_correction': error_correction,
                'size': f'{img.size[0]}x{img.size[1]}',
                'data_length': len(text)
            }
            
            return JsonResponse({
                'success': True,
                'qr_image': f'data:image/png;base64,{img_base64}',
                'qr_info': qr_info,
                'original_text': text
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'QRコード生成エラー: {str(e)}'})
    
    # GET リクエストの場合はテンプレートを表示
    return render(request, 'qr_generator.html')


def download_qr(request):
    """QRコード画像のダウンロード"""
    if request.method == 'POST':
        try:
            # パラメータ取得
            text = request.POST.get('text', '').strip()
            qr_type = request.POST.get('qr_type', 'text')
            size = int(request.POST.get('size', 10))
            border = int(request.POST.get('border', 4))
            error_correction = request.POST.get('error_correction', 'M')
            fill_color = request.POST.get('fill_color', 'black')
            back_color = request.POST.get('back_color', 'white')
            
            if not text:
                return JsonResponse({'success': False, 'error': 'テキストを入力してください'})
            
            # QRコードタイプに応じてテキストを処理（qr_generator関数と同じロジック）
            if qr_type == 'url':
                if not text.startswith(('http://', 'https://')):
                    text = 'https://' + text
            elif qr_type == 'email':
                if '@' in text:
                    text = f'mailto:{text}'
            elif qr_type == 'phone':
                text = f'tel:{text}'
            elif qr_type == 'sms':
                text = f'sms:{text}'
            elif qr_type == 'wifi':
                parts = text.split(',')
                if len(parts) >= 2:
                    ssid = parts[0].strip()
                    password = parts[1].strip()
                    security = parts[2].strip() if len(parts) > 2 else 'WPA'
                    text = f'WIFI:T:{security};S:{ssid};P:{password};;'
            
            # エラー訂正レベルの設定
            error_levels = {
                'L': ERROR_CORRECT_L,
                'M': ERROR_CORRECT_M,
                'Q': ERROR_CORRECT_Q,
                'H': ERROR_CORRECT_H
            }
            error_correct_level = error_levels.get(error_correction, ERROR_CORRECT_M)
            
            # QRコード生成
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_correct_level,
                box_size=size,
                border=border,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # 画像生成
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # HTTPレスポンスとして画像を返す
            response = HttpResponse(content_type='image/png')
            response['Content-Disposition'] = 'attachment; filename="qrcode.png"'
            img.save(response, format='PNG')
            
            return response
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'ダウンロードエラー: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': '無効なリクエスト'})


def get_data_capacity(version, error_correction):
    """QRコードバージョンとエラー訂正レベルに基づくデータ容量を取得"""
    # 簡略化された容量テーブル（数値モードの場合）
    capacities = {
        1: {'L': 41, 'M': 34, 'Q': 27, 'H': 17},
        2: {'L': 77, 'M': 63, 'Q': 48, 'H': 34},
        3: {'L': 127, 'M': 101, 'Q': 77, 'H': 58},
        4: {'L': 187, 'M': 149, 'Q': 111, 'H': 82},
        5: {'L': 255, 'M': 202, 'Q': 144, 'H': 106},
    }
    
    error_level_map = {
        ERROR_CORRECT_L: 'L',
        ERROR_CORRECT_M: 'M',
        ERROR_CORRECT_Q: 'Q',
        ERROR_CORRECT_H: 'H'
    }
    
    level = error_level_map.get(error_correction, 'M')
    return capacities.get(version, {}).get(level, 'Unknown')

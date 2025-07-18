"""
qr_views.py - QRコード生成関連のビュー
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import io
import base64

# QRコードライブラリを安全にインポート
try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


def qr_generator(request):
    """QRコード生成機能のメインビュー"""
    if request.method == 'POST':
        # QRライブラリが利用できない場合のエラーハンドリング
        if not QR_AVAILABLE:
            return JsonResponse({
                'success': False,
                'error': 'QRコードライブラリがインストールされていません。pip install qrcode[pil] を実行してください。'
            })
            
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
            processed_text = process_qr_text(text, qr_type)
            
            # エラー訂正レベルの設定
            error_correct_level = get_error_correction_level(error_correction)
            
            # QRコード生成
            qr = qrcode.QRCode(
                version=1,  # 自動サイズ調整
                error_correction=error_correct_level,
                box_size=size,
                border=border,
            )
            qr.add_data(processed_text)
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
                'data_length': len(processed_text)
            }
            
            return JsonResponse({
                'success': True,
                'qr_image': f'data:image/png;base64,{img_base64}',
                'qr_info': qr_info,
                'original_text': processed_text
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
            
            # QRコードタイプに応じてテキストを処理
            processed_text = process_qr_text(text, qr_type)
            
            # エラー訂正レベルの設定
            error_correct_level = get_error_correction_level(error_correction)
            
            # QRコード生成
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_correct_level,
                box_size=size,
                border=border,
            )
            qr.add_data(processed_text)
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


def process_qr_text(text, qr_type):
    """QRコードタイプに応じてテキストを処理"""
    if qr_type == 'url':
        if not text.startswith(('http://', 'https://')):
            return 'https://' + text
    elif qr_type == 'email':
        if '@' in text:
            return f'mailto:{text}'
    elif qr_type == 'phone':
        return f'tel:{text}'
    elif qr_type == 'sms':
        return f'sms:{text}'
    elif qr_type == 'wifi':
        # WiFi形式: WIFI:T:WPA;S:ネットワーク名;P:パスワード;;
        parts = text.split(',')
        if len(parts) >= 2:
            ssid = parts[0].strip()
            password = parts[1].strip()
            security = parts[2].strip() if len(parts) > 2 else 'WPA'
            return f'WIFI:T:{security};S:{ssid};P:{password};;'
    
    return text


def get_error_correction_level(error_correction):
    """エラー訂正レベルを取得"""
    error_levels = {
        'L': ERROR_CORRECT_L,  # 約7%
        'M': ERROR_CORRECT_M,  # 約15%
        'Q': ERROR_CORRECT_Q,  # 約25%
        'H': ERROR_CORRECT_H   # 約30%
    }
    return error_levels.get(error_correction, ERROR_CORRECT_M)


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

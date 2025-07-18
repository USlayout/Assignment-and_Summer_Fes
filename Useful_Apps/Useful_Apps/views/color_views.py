from django.shortcuts import render
from django.http import JsonResponse
import colorsys
import math
from PIL import Image
import io
import base64

# OpenCVと機械学習ライブラリを安全にインポート
try:
    import cv2
    import numpy as np
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # バックエンド設定
    ADVANCED_LIBS_AVAILABLE = True
except ImportError:
    ADVANCED_LIBS_AVAILABLE = False

def color_tools(request):
    """色彩ツールのメインビュー"""
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            
            if action == 'generate_palette':
                return generate_color_palette(request)
            elif action == 'convert_color':
                return convert_color_format(request)
            elif action == 'simulate_colorblind':
                return simulate_color_blindness(request)
            elif action == 'extract_colors':
                return extract_colors_from_image(request)
            elif action == 'analyze_histogram':
                return analyze_color_histogram(request)
            elif action == 'convert_colorspace':
                return convert_color_space(request)
            else:
                return JsonResponse({'success': False, 'error': '無効なアクションです'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'エラーが発生しました: {str(e)}'})
    
    return render(request, 'color_tools.html')

def generate_color_palette(request):
    """カラーパレット生成"""
    try:
        base_color = request.POST.get('base_color', '#FF0000')
        palette_type = request.POST.get('palette_type', 'complementary')
        
        # HEXカラーをRGBに変換
        rgb = hex_to_rgb(base_color)
        if not rgb:
            return JsonResponse({'success': False, 'error': '無効な色形式です'})
        
        # HSVに変換
        hsv = rgb_to_hsv(rgb)
        
        # パレットタイプに応じて色を生成
        palette = []
        
        if palette_type == 'complementary':
            # 補色（180度回転）
            palette = [
                base_color,
                hsv_to_hex(((hsv[0] + 0.5) % 1.0, hsv[1], hsv[2]))
            ]
            
        elif palette_type == 'triadic':
            # トライアド（120度ずつ）
            palette = [
                base_color,
                hsv_to_hex(((hsv[0] + 1/3) % 1.0, hsv[1], hsv[2])),
                hsv_to_hex(((hsv[0] + 2/3) % 1.0, hsv[1], hsv[2]))
            ]
            
        elif palette_type == 'analogous':
            # 類似色（30度ずつ）
            palette = [
                hsv_to_hex(((hsv[0] - 1/12) % 1.0, hsv[1], hsv[2])),
                base_color,
                hsv_to_hex(((hsv[0] + 1/12) % 1.0, hsv[1], hsv[2])),
                hsv_to_hex(((hsv[0] + 2/12) % 1.0, hsv[1], hsv[2]))
            ]
            
        elif palette_type == 'monochromatic':
            # 明度違いの同色相
            palette = [
                hsv_to_hex((hsv[0], hsv[1], max(0.2, hsv[2] - 0.4))),
                hsv_to_hex((hsv[0], hsv[1], max(0.4, hsv[2] - 0.2))),
                base_color,
                hsv_to_hex((hsv[0], max(0.2, hsv[1] - 0.3), min(1.0, hsv[2] + 0.2))),
                hsv_to_hex((hsv[0], max(0.1, hsv[1] - 0.5), min(1.0, hsv[2] + 0.4)))
            ]
            
        elif palette_type == 'tetradic':
            # 4色相補（90度ずつ）
            palette = [
                base_color,
                hsv_to_hex(((hsv[0] + 0.25) % 1.0, hsv[1], hsv[2])),
                hsv_to_hex(((hsv[0] + 0.5) % 1.0, hsv[1], hsv[2])),
                hsv_to_hex(((hsv[0] + 0.75) % 1.0, hsv[1], hsv[2]))
            ]
        
        # パレット情報を生成
        palette_info = []
        for color in palette:
            rgb = hex_to_rgb(color)
            hsl = rgb_to_hsl(rgb)
            palette_info.append({
                'hex': color,
                'rgb': f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})',
                'hsl': f'hsl({int(hsl[0] * 360)}, {int(hsl[1] * 100)}%, {int(hsl[2] * 100)}%)'
            })
        
        return JsonResponse({
            'success': True,
            'palette': palette_info,
            'palette_type': palette_type
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'パレット生成エラー: {str(e)}'})

def convert_color_format(request):
    """色形式変換"""
    try:
        input_color = request.POST.get('input_color', '').strip()
        input_format = request.POST.get('input_format', 'hex')
        
        if not input_color:
            return JsonResponse({'success': False, 'error': '色を入力してください'})
        
        # 入力形式に応じてRGBに変換
        if input_format == 'hex':
            rgb = hex_to_rgb(input_color)
        elif input_format == 'rgb':
            # "rgb(255, 0, 0)" または "255, 0, 0" 形式
            rgb = parse_rgb(input_color)
        elif input_format == 'hsl':
            # "hsl(0, 100%, 50%)" または "0, 100, 50" 形式
            hsl = parse_hsl(input_color)
            rgb = hsl_to_rgb(hsl) if hsl else None
        else:
            return JsonResponse({'success': False, 'error': '無効な入力形式です'})
        
        if not rgb:
            return JsonResponse({'success': False, 'error': '色の変換に失敗しました'})
        
        # 各形式に変換
        hex_color = rgb_to_hex(rgb)
        hsl = rgb_to_hsl(rgb)
        hsv = rgb_to_hsv(rgb)
        
        return JsonResponse({
            'success': True,
            'conversions': {
                'hex': hex_color,
                'rgb': f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})',
                'hsl': f'hsl({int(hsl[0] * 360)}, {int(hsl[1] * 100)}%, {int(hsl[2] * 100)}%)',
                'hsv': f'hsv({int(hsv[0] * 360)}, {int(hsv[1] * 100)}%, {int(hsv[2] * 100)}%)',
                'rgb_values': rgb,
                'hsl_values': [hsl[0] * 360, hsl[1] * 100, hsl[2] * 100],
                'hsv_values': [hsv[0] * 360, hsv[1] * 100, hsv[2] * 100]
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'色変換エラー: {str(e)}'})

def simulate_color_blindness(request):
    """色覚異常シミュレーション"""
    try:
        input_color = request.POST.get('input_color', '#FF0000')
        simulation_type = request.POST.get('simulation_type', 'protanopia')
        
        rgb = hex_to_rgb(input_color)
        if not rgb:
            return JsonResponse({'success': False, 'error': '無効な色形式です'})
        
        # 正規化（0-1の範囲）
        r, g, b = [x / 255.0 for x in rgb]
        
        # 色覚異常シミュレーション行列
        if simulation_type == 'protanopia':  # 赤色盲
            matrix = [
                [0.567, 0.433, 0.000],
                [0.558, 0.442, 0.000],
                [0.000, 0.242, 0.758]
            ]
        elif simulation_type == 'deuteranopia':  # 緑色盲
            matrix = [
                [0.625, 0.375, 0.000],
                [0.700, 0.300, 0.000],
                [0.000, 0.300, 0.700]
            ]
        elif simulation_type == 'tritanopia':  # 青色盲
            matrix = [
                [0.950, 0.050, 0.000],
                [0.000, 0.433, 0.567],
                [0.000, 0.475, 0.525]
            ]
        else:
            return JsonResponse({'success': False, 'error': '無効なシミュレーションタイプです'})
        
        # 行列変換
        new_r = matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b
        new_g = matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b
        new_b = matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b
        
        # 0-255の範囲に戻す
        simulated_rgb = [
            max(0, min(255, int(new_r * 255))),
            max(0, min(255, int(new_g * 255))),
            max(0, min(255, int(new_b * 255)))
        ]
        
        simulated_hex = rgb_to_hex(simulated_rgb)
        
        return JsonResponse({
            'success': True,
            'original': {
                'hex': input_color,
                'rgb': f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'
            },
            'simulated': {
                'hex': simulated_hex,
                'rgb': f'rgb({simulated_rgb[0]}, {simulated_rgb[1]}, {simulated_rgb[2]})'
            },
            'simulation_type': simulation_type
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'色覚シミュレーションエラー: {str(e)}'})

# ヘルパー関数
def hex_to_rgb(hex_color):
    """HEXをRGBに変換"""
    try:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return None
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except:
        return None

def rgb_to_hex(rgb):
    """RGBをHEXに変換"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def rgb_to_hsl(rgb):
    """RGBをHSLに変換"""
    r, g, b = [x / 255.0 for x in rgb]
    return colorsys.rgb_to_hls(r, g, b)

def hsl_to_rgb(hsl):
    """HSLをRGBに変換"""
    r, g, b = colorsys.hls_to_rgb(hsl[0], hsl[1], hsl[2])
    return tuple(int(x * 255) for x in (r, g, b))

def rgb_to_hsv(rgb):
    """RGBをHSVに変換"""
    r, g, b = [x / 255.0 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

def hsv_to_hex(hsv):
    """HSVをHEXに変換"""
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    rgb_int = tuple(int(x * 255) for x in rgb)
    return rgb_to_hex(rgb_int)

def parse_rgb(rgb_str):
    """RGB文字列をパース"""
    try:
        # "rgb(255, 0, 0)" または "255, 0, 0" 形式
        rgb_str = rgb_str.replace('rgb(', '').replace(')', '').replace(' ', '')
        values = [int(x) for x in rgb_str.split(',')]
        if len(values) == 3 and all(0 <= x <= 255 for x in values):
            return tuple(values)
        return None
    except:
        return None

def parse_hsl(hsl_str):
    """HSL文字列をパース"""
    try:
        # "hsl(0, 100%, 50%)" または "0, 100, 50" 形式
        hsl_str = hsl_str.replace('hsl(', '').replace(')', '').replace('%', '').replace(' ', '')
        values = [float(x) for x in hsl_str.split(',')]
        if len(values) == 3:
            h = (values[0] % 360) / 360.0  # 0-1の範囲に正規化
            s = max(0, min(100, values[1])) / 100.0
            l = max(0, min(100, values[2])) / 100.0
            return (h, l, s)  # colorsysはHLSの順序
        return None
    except:
        return None

def extract_colors_from_image(request):
    """OpenCV + KMeansで画像から主要色を抽出"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': '画像がアップロードされていません'})
        
        image_file = request.FILES['image']
        num_colors = int(request.POST.get('num_colors', 5))
        
        # 画像を読み込み
        img_data = image_file.read()
        img_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return JsonResponse({'success': False, 'error': '画像の読み込みに失敗しました'})
        
        # BGRからRGBに変換
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # リサイズ（処理速度向上のため）
        height, width = img_rgb.shape[:2]
        if width > 300:
            scale = 300 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_rgb = cv2.resize(img_rgb, (new_width, new_height))
        
        # ピクセルデータを1次元に変換
        data = img_rgb.reshape((-1, 3))
        
        # KMeansクラスタリングで主要色を抽出
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(data)
        
        # 主要色とその割合を計算
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        counts = np.bincount(labels)
        percentages = counts / len(labels) * 100
        
        # 結果を整理
        extracted_colors = []
        for i, (color, percentage) in enumerate(zip(colors, percentages)):
            r, g, b = color
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            extracted_colors.append({
                'hex': hex_color,
                'rgb': f'rgb({r}, {g}, {b})',
                'percentage': round(percentage, 1),
                'rank': i + 1
            })
        
        # 割合でソート
        extracted_colors.sort(key=lambda x: x['percentage'], reverse=True)
        
        # 元画像のBase64エンコード（プレビュー用）
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
        img_base64 = base64.b64encode(buffer).decode()
        
        return JsonResponse({
            'success': True,
            'colors': extracted_colors,
            'image_preview': f'data:image/jpeg;base64,{img_base64}',
            'total_colors': len(extracted_colors)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'色抽出エラー: {str(e)}'})

def analyze_color_histogram(request):
    """OpenCVで色ヒストグラムを解析"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': '画像がアップロードされていません'})
        
        image_file = request.FILES['image']
        
        # 画像を読み込み
        img_data = image_file.read()
        img_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return JsonResponse({'success': False, 'error': '画像の読み込みに失敗しました'})
        
        # BGRからRGBに変換
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # ヒストグラムを計算
        hist_r = cv2.calcHist([img_rgb], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img_rgb], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([img_rgb], [2], None, [256], [0, 256])
        
        # ヒストグラムをプロット
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 3, 1)
        plt.plot(hist_r, color='red', alpha=0.7)
        plt.title('Red Channel')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        
        plt.subplot(1, 3, 2)
        plt.plot(hist_g, color='green', alpha=0.7)
        plt.title('Green Channel')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        
        plt.subplot(1, 3, 3)
        plt.plot(hist_b, color='blue', alpha=0.7)
        plt.title('Blue Channel')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        
        plt.tight_layout()
        
        # プロットをBase64エンコード
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # 統計情報を計算
        stats = {
            'red': {
                'mean': float(np.mean(img_rgb[:, :, 0])),
                'std': float(np.std(img_rgb[:, :, 0])),
                'median': float(np.median(img_rgb[:, :, 0]))
            },
            'green': {
                'mean': float(np.mean(img_rgb[:, :, 1])),
                'std': float(np.std(img_rgb[:, :, 1])),
                'median': float(np.median(img_rgb[:, :, 1]))
            },
            'blue': {
                'mean': float(np.mean(img_rgb[:, :, 2])),
                'std': float(np.std(img_rgb[:, :, 2])),
                'median': float(np.median(img_rgb[:, :, 2]))
            }
        }
        
        return JsonResponse({
            'success': True,
            'histogram_plot': f'data:image/png;base64,{plot_base64}',
            'statistics': stats
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'ヒストグラム解析エラー: {str(e)}'})

def convert_color_space(request):
    """OpenCVで色空間変換"""
    try:
        input_color = request.POST.get('input_color', '#FF0000')
        target_space = request.POST.get('target_space', 'hsv')
        
        # HEXをRGBに変換
        rgb = hex_to_rgb(input_color)
        if not rgb:
            return JsonResponse({'success': False, 'error': '無効な色形式です'})
        
        # NumPy配列に変換（OpenCV用）
        bgr_array = np.uint8([[[rgb[2], rgb[1], rgb[0]]]])  # BGRの順序
        
        conversions = {}
        
        if target_space == 'hsv':
            hsv_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2HSV)
            h, s, v = hsv_array[0, 0]
            conversions['hsv'] = {
                'h': int(h * 2),  # OpenCVでは0-179
                's': int(s),
                'v': int(v),
                'formatted': f'hsv({int(h * 2)}, {int(s)}, {int(v)})'
            }
            
        elif target_space == 'lab':
            lab_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2LAB)
            l, a, b = lab_array[0, 0]
            conversions['lab'] = {
                'l': int(l),
                'a': int(a) - 128,  # aとbは-128～127の範囲
                'b': int(b) - 128,
                'formatted': f'lab({int(l)}, {int(a) - 128}, {int(b) - 128})'
            }
            
        elif target_space == 'yuv':
            yuv_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2YUV)
            y, u, v = yuv_array[0, 0]
            conversions['yuv'] = {
                'y': int(y),
                'u': int(u),
                'v': int(v),
                'formatted': f'yuv({int(y)}, {int(u)}, {int(v)})'
            }
            
        elif target_space == 'hls':
            hls_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2HLS)
            h, l, s = hls_array[0, 0]
            conversions['hls'] = {
                'h': int(h * 2),  # OpenCVでは0-179
                'l': int(l),
                's': int(s),
                'formatted': f'hls({int(h * 2)}, {int(l)}, {int(s)})'
            }
        
        # 元の色情報も含める
        conversions['original'] = {
            'hex': input_color,
            'rgb': f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})',
            'bgr': f'bgr({rgb[2]}, {rgb[1]}, {rgb[0]})'
        }
        
        return JsonResponse({
            'success': True,
            'conversions': conversions,
            'target_space': target_space
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'色空間変換エラー: {str(e)}'})


# 既存のヘルパー関数は変更なし

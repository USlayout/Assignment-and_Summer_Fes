# OpenCV色彩ツール - 必要なライブラリのインストール

## 必要なパッケージ
以下のコマンドを仮想環境で実行してください：

```bash
# OpenCVのインストール
pip install opencv-python

# scikit-learnのインストール（KMeansクラスタリング用）
pip install scikit-learn

# matplotlib/numpyのインストール（ヒストグラム描画用）
pip install matplotlib numpy

# 全て一括でインストール
pip install opencv-python scikit-learn matplotlib numpy
```

## インストール後の確認
```python
import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
print("全てのライブラリが正常にインストールされました！")
```

## 新機能の概要

### 1. 画像色抽出 (OpenCV + KMeans)
- 画像をアップロードして主要色を自動抽出
- K-Meansクラスタリングで色を分析
- 各色の占める割合を表示

### 2. ヒストグラム解析 (OpenCV + matplotlib)
- RGB各チャンネルのヒストグラムを生成
- 統計情報（平均、中央値、標準偏差）を表示
- 色分布の可視化

### 3. 色空間変換 (OpenCV)
- HSV、LAB、YUV、HLS色空間への変換
- より高精度な色変換
- 専門的な色空間での分析

## 使用ライブラリ数
これで以下のライブラリを活用：
1. Django - Webフレームワーク
2. Pillow - 画像処理
3. colorsys - 色空間変換
4. qrcode - QRコード生成
5. **opencv-python** - 画像解析・色空間変換
6. **scikit-learn** - 機械学習（KMeans）
7. **matplotlib** - グラフ描画
8. **numpy** - 数値計算

**合計8つのライブラリで課題要件をクリア！**

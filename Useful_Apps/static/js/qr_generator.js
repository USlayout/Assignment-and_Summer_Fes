// QRコード生成ページ専用JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM要素の取得
    const qrForm = document.getElementById('qrForm');
    const qrTypeSelect = document.getElementById('qrType');
    const qrTextArea = document.getElementById('qrText');
    const textInputArea = document.getElementById('textInputArea');
    const inputHint = document.getElementById('inputHint');
    const generateBtn = document.getElementById('generateBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');
    
    const previewPlaceholder = document.getElementById('previewPlaceholder');
    const qrResult = document.getElementById('qrResult');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const qrImage = document.getElementById('qrImage');
    const qrInfo = document.getElementById('qrInfo');

    // 現在のQRコードデータを保存
    let currentQRData = null;

    // QRコードタイプ変更時の処理
    qrTypeSelect.addEventListener('change', function() {
        updateInputInterface(this.value);
    });

    // フォーム送信処理
    qrForm.addEventListener('submit', function(e) {
        e.preventDefault();
        generateQRCode();
    });

    // ダウンロードボタン
    downloadBtn.addEventListener('click', function() {
        downloadQRCode();
    });

    // 再生成ボタン
    regenerateBtn.addEventListener('click', function() {
        showPreviewPlaceholder();
    });

    // QRコードタイプに応じた入力インターフェースの更新
    function updateInputInterface(type) {
        const hints = {
            'text': 'テキストを入力してください（改行可能）',
            'url': 'Webサイトのアドレスを入力してください（例: https://example.com）',
            'email': 'メールアドレスを入力してください（例: user@example.com）',
            'phone': '電話番号を入力してください（例: 090-1234-5678）',
            'sms': 'SMS送信先の電話番号を入力してください',
            'wifi': 'WiFi情報を入力してください（ネットワーク名,パスワード,セキュリティタイプ）'
        };

        const placeholders = {
            'text': 'ここにテキストを入力...',
            'url': 'https://example.com',
            'email': 'user@example.com',
            'phone': '090-1234-5678',
            'sms': '090-1234-5678',
            'wifi': 'MyWiFi,password123,WPA'
        };

        inputHint.textContent = hints[type];
        qrTextArea.placeholder = placeholders[type];

        // WiFi用の特別な入力フィールド
        if (type === 'wifi') {
            createWiFiInputs();
        } else {
            restoreTextArea();
        }
    }

    // WiFi用入力フィールドの作成
    function createWiFiInputs() {
        textInputArea.innerHTML = `
            <div class="input-group mb-2">
                <span class="input-group-text">ネットワーク名</span>
                <input type="text" class="form-control" id="wifiSSID" placeholder="WiFiネットワーク名">
            </div>
            <div class="input-group mb-2">
                <span class="input-group-text">パスワード</span>
                <input type="password" class="form-control" id="wifiPassword" placeholder="WiFiパスワード">
            </div>
            <div class="input-group mb-2">
                <span class="input-group-text">セキュリティ</span>
                <select class="form-select" id="wifiSecurity">
                    <option value="WPA">WPA/WPA2</option>
                    <option value="WEP">WEP</option>
                    <option value="nopass">なし</option>
                </select>
            </div>
        `;

        // WiFi入力フィールドのイベントリスナー
        ['wifiSSID', 'wifiPassword', 'wifiSecurity'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', updateWiFiText);
            }
        });
    }

    // WiFi情報の更新
    function updateWiFiText() {
        const ssid = document.getElementById('wifiSSID')?.value || '';
        const password = document.getElementById('wifiPassword')?.value || '';
        const security = document.getElementById('wifiSecurity')?.value || 'WPA';
        
        qrTextArea.value = `${ssid},${password},${security}`;
    }

    // 通常のテキストエリアに戻す
    function restoreTextArea() {
        textInputArea.innerHTML = `
            <textarea class="form-control" id="qrText" name="text" rows="4" 
                      placeholder="QRコードに変換するテキストを入力してください"></textarea>
        `;
    }

    // QRコード生成
    function generateQRCode() {
        const formData = new FormData(qrForm);
        
        // WiFiの場合は特別処理
        if (qrTypeSelect.value === 'wifi') {
            const ssid = document.getElementById('wifiSSID')?.value || '';
            const password = document.getElementById('wifiPassword')?.value || '';
            const security = document.getElementById('wifiSecurity')?.value || 'WPA';
            formData.set('text', `${ssid},${password},${security}`);
        }

        // バリデーション
        const text = formData.get('text');
        if (!text || text.trim() === '') {
            showError('テキストを入力してください');
            return;
        }

        showLoading();

        fetch('/qr-generator/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                showQRResult(data);
            } else {
                showError(data.error || 'QRコード生成に失敗しました');
            }
        })
        .catch(error => {
            hideLoading();
            showError('ネットワークエラー: ' + error.message);
        });
    }

    // QRコード結果の表示
    function showQRResult(data) {
        currentQRData = data;
        
        qrImage.src = data.qr_image;
        qrImage.alt = 'Generated QR Code';
        
        // QRコード情報の表示
        qrInfo.innerHTML = `
            <div class="info-item">
                <span class="info-label">バージョン</span>
                <span class="info-value">${data.qr_info.version}</span>
            </div>
            <div class="info-item">
                <span class="info-label">エラー訂正</span>
                <span class="info-value">${data.qr_info.error_correction}</span>
            </div>
            <div class="info-item">
                <span class="info-label">画像サイズ</span>
                <span class="info-value">${data.qr_info.size}px</span>
            </div>
            <div class="info-item">
                <span class="info-label">データ長</span>
                <span class="info-value">${data.qr_info.data_length}文字</span>
            </div>
            <div class="info-item">
                <span class="info-label">最大容量</span>
                <span class="info-value">${data.qr_info.data_capacity}文字</span>
            </div>
        `;

        hideAllStates();
        qrResult.style.display = 'block';
        qrResult.classList.add('success-animation');
        
        // アニメーション終了後にクラスを削除
        setTimeout(() => {
            qrResult.classList.remove('success-animation');
        }, 1000);
    }

    // QRコードダウンロード
    function downloadQRCode() {
        if (!currentQRData) {
            showError('ダウンロードするQRコードがありません');
            return;
        }

        const formData = new FormData(qrForm);
        
        // WiFiの場合は特別処理
        if (qrTypeSelect.value === 'wifi') {
            const ssid = document.getElementById('wifiSSID')?.value || '';
            const password = document.getElementById('wifiPassword')?.value || '';
            const security = document.getElementById('wifiSecurity')?.value || 'WPA';
            formData.set('text', `${ssid},${password},${security}`);
        }

        fetch('/download-qr/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('ダウンロードに失敗しました');
        })
        .then(blob => {
            // ダウンロードリンクを作成
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `qrcode_${Date.now()}.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // 成功メッセージ
            showSuccessMessage('QRコードをダウンロードしました');
        })
        .catch(error => {
            showError('ダウンロードエラー: ' + error.message);
        });
    }

    // UI状態管理
    function showLoading() {
        qrForm.classList.add('generating');
        generateBtn.disabled = true;
        hideAllStates();
        loadingSpinner.style.display = 'block';
    }

    function hideLoading() {
        qrForm.classList.remove('generating');
        generateBtn.disabled = false;
        loadingSpinner.style.display = 'none';
    }

    function showError(message) {
        hideAllStates();
        errorText.textContent = message;
        errorMessage.style.display = 'block';
    }

    function showPreviewPlaceholder() {
        hideAllStates();
        previewPlaceholder.style.display = 'block';
        currentQRData = null;
    }

    function hideAllStates() {
        previewPlaceholder.style.display = 'none';
        qrResult.style.display = 'none';
        loadingSpinner.style.display = 'none';
        errorMessage.style.display = 'none';
    }

    function showSuccessMessage(message) {
        // 一時的な成功メッセージ表示
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alert, container.firstChild);
        
        // 3秒後に自動削除
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 3000);
    }

    // CSRFトークン取得
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // プリセット機能
    function addPresetButtons() {
        const presets = {
            'url': [
                { label: 'Google', value: 'https://www.google.com' },
                { label: 'YouTube', value: 'https://www.youtube.com' },
                { label: 'GitHub', value: 'https://github.com' }
            ],
            'text': [
                { label: '名刺情報', value: '山田太郎\n090-1234-5678\nyamada@example.com' },
                { label: 'Hello World', value: 'Hello, World!' }
            ]
        };

        qrTypeSelect.addEventListener('change', function() {
            const type = this.value;
            const existingPresets = document.querySelector('.preset-buttons');
            if (existingPresets) {
                existingPresets.remove();
            }

            if (presets[type]) {
                const presetDiv = document.createElement('div');
                presetDiv.className = 'preset-buttons';
                
                presets[type].forEach(preset => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'btn btn-outline-secondary btn-preset';
                    btn.textContent = preset.label;
                    btn.onclick = () => {
                        qrTextArea.value = preset.value;
                    };
                    presetDiv.appendChild(btn);
                });

                inputHint.parentNode.appendChild(presetDiv);
            }
        });
    }

    // 初期化
    updateInputInterface(qrTypeSelect.value);
    addPresetButtons();
    showPreviewPlaceholder();
});

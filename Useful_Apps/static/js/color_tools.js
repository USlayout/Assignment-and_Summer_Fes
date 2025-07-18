// 色彩ツール JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // カラーピッカーとテキスト入力の同期
    syncColorInputs();
    
    // フォームイベントリスナー
    setupFormListeners();
    
    // 初期パレット生成
    generateInitialPalette();
});

function syncColorInputs() {
    // ベースカラーの同期
    const baseColor = document.getElementById('baseColor');
    const baseColorText = document.getElementById('baseColorText');
    
    if (baseColor && baseColorText) {
        baseColor.addEventListener('input', function() {
            baseColorText.value = this.value.toUpperCase();
        });
        
        baseColorText.addEventListener('input', function() {
            if (isValidHexColor(this.value)) {
                baseColor.value = this.value;
            }
        });
    }
    
    // シミュレーションカラーの同期
    const simulationColor = document.getElementById('simulationColor');
    const simulationColorText = document.getElementById('simulationColorText');
    
    if (simulationColor && simulationColorText) {
        simulationColor.addEventListener('input', function() {
            simulationColorText.value = this.value.toUpperCase();
        });
        
        simulationColorText.addEventListener('input', function() {
            if (isValidHexColor(this.value)) {
                simulationColor.value = this.value;
            }
        });
    }
}

function setupFormListeners() {
    // パレット生成フォーム
    const paletteForm = document.getElementById('paletteForm');
    if (paletteForm) {
        paletteForm.addEventListener('submit', handlePaletteGeneration);
    }
    
    // 色形式変換フォーム
    const converterForm = document.getElementById('converterForm');
    if (converterForm) {
        converterForm.addEventListener('submit', handleColorConversion);
        
        // 入力形式変更時のプレースホルダー更新
        const inputFormat = document.getElementById('inputFormat');
        const inputColor = document.getElementById('inputColor');
        
        if (inputFormat && inputColor) {
            inputFormat.addEventListener('change', function() {
                updateInputPlaceholder(this.value, inputColor);
            });
        }
    }
    
    // 色覚異常シミュレーションフォーム
    const colorblindForm = document.getElementById('colorblindForm');
    if (colorblindForm) {
        colorblindForm.addEventListener('submit', handleColorblindSimulation);
    }
    
    // 画像色抽出フォーム
    const extractForm = document.getElementById('extractForm');
    if (extractForm) {
        extractForm.addEventListener('submit', handleColorExtraction);
        
        // 色数スライダーの値更新
        const numColors = document.getElementById('numColors');
        const numColorsValue = document.getElementById('numColorsValue');
        if (numColors && numColorsValue) {
            numColors.addEventListener('input', function() {
                numColorsValue.textContent = this.value;
            });
        }
    }
    
    // ヒストグラム解析フォーム
    const histogramForm = document.getElementById('histogramForm');
    if (histogramForm) {
        histogramForm.addEventListener('submit', handleHistogramAnalysis);
    }
    
    // 色空間変換フォーム
    const colorspaceForm = document.getElementById('colorspaceForm');
    if (colorspaceForm) {
        colorspaceForm.addEventListener('submit', handleColorspaceConversion);
    }
}

function handlePaletteGeneration(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // ローディング状態
    submitBtn.innerHTML = '<span class="loading"></span> 生成中...';
    submitBtn.disabled = true;
    
    fetch('/color-tools/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayPalette(data.palette, data.palette_type);
        } else {
            showAlert('paletteResult', data.error, 'error');
        }
    })
    .catch(error => {
        showAlert('paletteResult', 'ネットワークエラーが発生しました', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function handleColorConversion(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // ローディング状態
    submitBtn.innerHTML = '<span class="loading"></span> 変換中...';
    submitBtn.disabled = true;
    
    fetch('/color-tools/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayConversionResult(data.conversions);
        } else {
            showAlert('converterResult', data.error, 'error');
        }
    })
    .catch(error => {
        showAlert('converterResult', 'ネットワークエラーが発生しました', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function handleColorblindSimulation(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // ローディング状態
    submitBtn.innerHTML = '<span class="loading"></span> 実行中...';
    submitBtn.disabled = true;
    
    fetch('/color-tools/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayColorblindResult(data.original, data.simulated, data.simulation_type);
        } else {
            showAlert('colorblindResult', data.error, 'error');
        }
    })
    .catch(error => {
        showAlert('colorblindResult', 'ネットワークエラーが発生しました', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function displayPalette(palette, paletteType) {
    const resultDiv = document.getElementById('paletteResult');
    
    let html = `
        <div class="palette-info mb-3">
            <h6 class="text-primary">生成されたパレット（${getPaletteTypeName(paletteType)}）</h6>
        </div>
        <div class="palette-container">
    `;
    
    palette.forEach((color, index) => {
        html += `
            <div class="color-swatch" style="background-color: ${color.hex};" onclick="copyToClipboard('${color.hex}')">
                <div class="color-info">
                    <div>${color.hex}</div>
                    <div>${color.rgb}</div>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="mt-3">
            <small class="text-muted">
                <i class="fas fa-info-circle me-1"></i>
                色をクリックするとHEXコードがクリップボードにコピーされます
            </small>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

function displayConversionResult(conversions) {
    const resultDiv = document.getElementById('converterResult');
    
    const html = `
        <div class="conversion-result">
            <div class="conversion-item">
                <div class="conversion-color-preview" style="background-color: ${conversions.hex};"></div>
                <div class="conversion-details">
                    <div class="conversion-label">HEX</div>
                    <div class="conversion-value">${conversions.hex}</div>
                </div>
                <button class="copy-btn" onclick="copyToClipboard('${conversions.hex}')" title="コピー">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            
            <div class="conversion-item">
                <div class="conversion-color-preview" style="background-color: ${conversions.hex};"></div>
                <div class="conversion-details">
                    <div class="conversion-label">RGB</div>
                    <div class="conversion-value">${conversions.rgb}</div>
                </div>
                <button class="copy-btn" onclick="copyToClipboard('${conversions.rgb}')" title="コピー">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            
            <div class="conversion-item">
                <div class="conversion-color-preview" style="background-color: ${conversions.hex};"></div>
                <div class="conversion-details">
                    <div class="conversion-label">HSL</div>
                    <div class="conversion-value">${conversions.hsl}</div>
                </div>
                <button class="copy-btn" onclick="copyToClipboard('${conversions.hsl}')" title="コピー">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            
            <div class="conversion-item">
                <div class="conversion-color-preview" style="background-color: ${conversions.hex};"></div>
                <div class="conversion-details">
                    <div class="conversion-label">HSV</div>
                    <div class="conversion-value">${conversions.hsv}</div>
                </div>
                <button class="copy-btn" onclick="copyToClipboard('${conversions.hsv}')" title="コピー">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

function displayColorblindResult(original, simulated, simulationType) {
    const resultDiv = document.getElementById('colorblindResult');
    
    const html = `
        <div class="colorblind-comparison">
            <div class="colorblind-sample">
                <div class="colorblind-color" style="background-color: ${original.hex};"></div>
                <div class="colorblind-label">通常視覚</div>
                <div class="colorblind-value">${original.hex}</div>
                <div class="colorblind-value">${original.rgb}</div>
            </div>
            
            <div class="arrow-separator">
                <i class="fas fa-arrow-right"></i>
            </div>
            
            <div class="colorblind-sample">
                <div class="colorblind-color" style="background-color: ${simulated.hex};"></div>
                <div class="colorblind-label">${getSimulationTypeName(simulationType)}</div>
                <div class="colorblind-value">${simulated.hex}</div>
                <div class="colorblind-value">${simulated.rgb}</div>
            </div>
        </div>
        
        <div class="mt-3 text-center">
            <small class="text-muted">
                <i class="fas fa-info-circle me-1"></i>
                ${getSimulationDescription(simulationType)}
            </small>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

function generateInitialPalette() {
    // ページ読み込み時に初期パレットを生成
    const paletteForm = document.getElementById('paletteForm');
    if (paletteForm) {
        const formData = new FormData(paletteForm);
        
        fetch('/color-tools/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPalette(data.palette, data.palette_type);
            }
        })
        .catch(error => {
            console.error('Initial palette generation error:', error);
        });
    }
}

function updateInputPlaceholder(format, inputElement) {
    const placeholders = {
        'hex': '#FF0000',
        'rgb': 'rgb(255, 0, 0) または 255, 0, 0',
        'hsl': 'hsl(0, 100%, 50%) または 0, 100, 50'
    };
    
    inputElement.placeholder = placeholders[format] || '#FF0000';
    
    // デフォルト値も更新
    if (format === 'hex') {
        inputElement.value = '#FF0000';
    } else if (format === 'rgb') {
        inputElement.value = 'rgb(255, 0, 0)';
    } else if (format === 'hsl') {
        inputElement.value = 'hsl(0, 100%, 50%)';
    }
}

// ユーティリティ関数
function isValidHexColor(hex) {
    return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(hex);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('クリップボードにコピーしました: ' + text);
    }).catch(function(err) {
        console.error('コピーに失敗しました:', err);
        showToast('コピーに失敗しました', 'error');
    });
}

function showAlert(containerId, message, type) {
    const container = document.getElementById(containerId);
    const alertClass = type === 'error' ? 'alert-error' : 'alert-success';
    
    container.innerHTML = `
        <div class="alert alert-custom ${alertClass}" role="alert">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
            ${message}
        </div>
    `;
}

function showToast(message, type = 'success') {
    // 簡易トースト通知
    const toast = document.createElement('div');
    toast.className = `position-fixed top-0 end-0 m-3 alert alert-custom ${type === 'error' ? 'alert-error' : 'alert-success'}`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
        ${message}
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function getPaletteTypeName(type) {
    const names = {
        'complementary': '補色',
        'triadic': 'トライアド',
        'analogous': '類似色',
        'monochromatic': 'モノクロマティック',
        'tetradic': '4色相補'
    };
    return names[type] || type;
}

function getSimulationTypeName(type) {
    const names = {
        'protanopia': '赤色盲',
        'deuteranopia': '緑色盲',
        'tritanopia': '青色盲'
    };
    return names[type] || type;
}

function getSimulationDescription(type) {
    const descriptions = {
        'protanopia': '赤い光に感じにくい色覚特性をシミュレーションしています',
        'deuteranopia': '緑の光に感じにくい色覚特性をシミュレーションしています',
        'tritanopia': '青い光に感じにくい色覚特性をシミュレーションしています'
    };
    return descriptions[type] || '';
}

// OpenCV機能用の新しい表示関数
function displayExtractedColors(colors, imagePreview) {
    const resultDiv = document.getElementById('extractResult');
    
    let html = `
        <div class="extracted-colors-result">
            <div class="mb-3">
                <h6 class="text-primary">元画像</h6>
                <img src="${imagePreview}" class="img-fluid rounded" style="max-height: 200px;">
            </div>
            <div class="mb-3">
                <h6 class="text-primary">抽出された色（${colors.length}色）</h6>
            </div>
            <div class="extracted-colors-grid">
    `;
    
    colors.forEach(color => {
        html += `
            <div class="extracted-color-item" onclick="copyToClipboard('${color.hex}')">
                <div class="extracted-color-swatch" style="background-color: ${color.hex};"></div>
                <div class="extracted-color-info">
                    <div class="extracted-color-hex">${color.hex}</div>
                    <div class="extracted-color-percentage">${color.percentage}%</div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
            <div class="mt-3">
                <small class="text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    色をクリックするとHEXコードがクリップボードにコピーされます
                </small>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

function displayHistogramAnalysis(histogramPlot, statistics) {
    const resultDiv = document.getElementById('histogramResult');
    
    const html = `
        <div class="histogram-analysis-result">
            <div class="mb-3">
                <h6 class="text-primary">色ヒストグラム</h6>
                <img src="${histogramPlot}" class="img-fluid rounded" alt="Color Histogram">
            </div>
            
            <div class="statistics-grid">
                <div class="stat-card">
                    <h6 class="stat-title">Red Channel</h6>
                    <div class="stat-values">
                        <div>平均: ${statistics.red.mean.toFixed(1)}</div>
                        <div>中央値: ${statistics.red.median.toFixed(1)}</div>
                        <div>標準偏差: ${statistics.red.std.toFixed(1)}</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h6 class="stat-title">Green Channel</h6>
                    <div class="stat-values">
                        <div>平均: ${statistics.green.mean.toFixed(1)}</div>
                        <div>中央値: ${statistics.green.median.toFixed(1)}</div>
                        <div>標準偏差: ${statistics.green.std.toFixed(1)}</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h6 class="stat-title">Blue Channel</h6>
                    <div class="stat-values">
                        <div>平均: ${statistics.blue.mean.toFixed(1)}</div>
                        <div>中央値: ${statistics.blue.median.toFixed(1)}</div>
                        <div>標準偏差: ${statistics.blue.std.toFixed(1)}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

function displayColorspaceResult(conversions, targetSpace) {
    const resultDiv = document.getElementById('colorspaceResult');
    
    let html = `
        <div class="colorspace-conversion-result">
            <div class="mb-3">
                <h6 class="text-primary">元の色</h6>
                <div class="conversion-item">
                    <div class="conversion-color-preview" style="background-color: ${conversions.original.hex};"></div>
                    <div class="conversion-details">
                        <div class="conversion-label">HEX</div>
                        <div class="conversion-value">${conversions.original.hex}</div>
                    </div>
                </div>
            </div>
            
            <div class="mb-3">
                <h6 class="text-primary">${getTargetSpaceName(targetSpace)}変換結果</h6>
    `;
    
    // 変換結果を表示
    Object.keys(conversions).forEach(key => {
        if (key !== 'original') {
            const conv = conversions[key];
            html += `
                <div class="conversion-item">
                    <div class="conversion-color-preview" style="background-color: ${conversions.original.hex};"></div>
                    <div class="conversion-details">
                        <div class="conversion-label">${key.toUpperCase()}</div>
                        <div class="conversion-value">${conv.formatted}</div>
                    </div>
                    <button class="copy-btn" onclick="copyToClipboard('${conv.formatted}')" title="コピー">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            `;
        }
    });
    
    html += `
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

function getTargetSpaceName(space) {
    const names = {
        'hsv': 'HSV（色相・彩度・明度）',
        'lab': 'LAB（知覚的均等色空間）',
        'yuv': 'YUV（輝度・色差）',
        'hls': 'HLS（色相・明度・彩度）'
    };
    return names[space] || space.toUpperCase();
}

// 新機能用のハンドラー関数
function handleColorExtraction(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<span class="loading"></span> 抽出中...';
    submitBtn.disabled = true;
    
    fetch('/color-tools/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayExtractedColors(data.colors, data.image_preview);
        } else {
            showAlert('extractResult', data.error, 'error');
        }
    })
    .catch(error => {
        showAlert('extractResult', 'ネットワークエラーが発生しました', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function handleHistogramAnalysis(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<span class="loading"></span> 解析中...';
    submitBtn.disabled = true;
    
    fetch('/color-tools/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayHistogramAnalysis(data.histogram_plot, data.statistics);
        } else {
            showAlert('histogramResult', data.error, 'error');
        }
    })
    .catch(error => {
        showAlert('histogramResult', 'ネットワークエラーが発生しました', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function handleColorspaceConversion(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<span class="loading"></span> 変換中...';
    submitBtn.disabled = true;
    
    fetch('/color-tools/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayColorspaceResult(data.conversions, data.target_space);
        } else {
            showAlert('colorspaceResult', data.error, 'error');
        }
    })
    .catch(error => {
        showAlert('colorspaceResult', 'ネットワークエラーが発生しました', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

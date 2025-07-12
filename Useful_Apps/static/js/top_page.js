// トップページ専用JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 機能カードのホバーアニメーション
    const featureCards = document.querySelectorAll('.feature-card');
    const featureCardLinks = document.querySelectorAll('.feature-card-link');
    
    // Coming Soon機能のクリックイベント
    const comingSoonTriggers = document.querySelectorAll('.coming-soon-trigger');
    
    comingSoonTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const featureName = this.dataset.feature;
            showComingSoonModal(featureName);
        });
    });

    // 機能カードのクリック効果
    featureCardLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // 利用可能な機能の場合、通常のリンク動作
            if (!this.classList.contains('coming-soon-trigger')) {
                // クリック効果のアニメーション
                const card = this.querySelector('.feature-card');
                card.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    card.style.transform = '';
                }, 150);
            }
        });
    });

    // キーボードアクセシビリティ
    featureCardLinks.forEach(link => {
        link.setAttribute('tabindex', '0');
        link.setAttribute('role', 'button');
        
        link.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

    comingSoonTriggers.forEach(trigger => {
        trigger.setAttribute('tabindex', '0');
        trigger.setAttribute('role', 'button');
        trigger.setAttribute('aria-label', '開発中機能');
        
        trigger.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

    // スムーススクロール
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ページロード時のアニメーション
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    // 機能カードを監視
    featureCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // ナビゲーションバーのアクティブ状態管理
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Coming Soon モーダル表示
    function showComingSoonModal(featureName) {
        const featureNames = {
            'dictionary': '辞書検索機能',
            'text-tools': 'テキスト変換ツール',
            'data-analysis': 'データ分析ツール'
        };
        
        const displayName = featureNames[featureName] || '新機能';
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            // モーダルのタイトルを動的に更新
            const modal = document.getElementById('comingSoonModal');
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body h6');
            
            modalTitle.innerHTML = `<i class="fas fa-rocket me-2"></i>${displayName} - Coming Soon!`;
            modalBody.textContent = `${displayName}開発中`;
            
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        } else {
            // シンプルなアラート
            alert(`${displayName}は現在開発中です。近日公開予定です！`);
        }
    }

    // パフォーマンス最適化：画像の遅延読み込み
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // タイピングアニメーション効果（ヒーローセクション用）
    function typeWriter(element, text, speed = 50) {
        let i = 0;
        element.innerHTML = '';
        
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }

    // ヒーローセクションのタイトルにタイピング効果を適用（オプション）
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle && heroTitle.dataset.typing === 'true') {
        const originalText = heroTitle.textContent;
        typeWriter(heroTitle, originalText, 100);
    }

    // 統計情報のカウントアップアニメーション（将来の拡張用）
    function countUp(element, target, duration = 2000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            element.textContent = Math.floor(current);
            
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            }
        }, 16);
    }

    // エラーハンドリング
    window.addEventListener('error', function(e) {
        console.error('JavaScript Error:', e.error);
    });

    // デバッグ用（開発環境でのみ有効）
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('UsefulApp Top Page Loaded Successfully');
    }
});

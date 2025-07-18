"""
base_views.py - 基本的なビュー（トップページなど）
"""

from django.shortcuts import render


def top_page(request):
    """トップページのビュー"""
    return render(request, 'top_page.html')

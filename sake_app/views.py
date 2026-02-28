import json

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Case, When, Value, BooleanField, Subquery, OuterRef, IntegerField
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Prefecture, Brewery, Sake, SakeLog
from .forms import SakeLogForm


def _build_map_data(prefectures, drunk_counts=None):
    """都道府県データを地図用JSONに変換するヘルパー"""
    data = {}
    for p in prefectures:
        sake_count = getattr(p, "sake_count", 0) or 0
        drunk_count = 0
        if drunk_counts:
            drunk_count = drunk_counts.get(p.id, 0)
        ratio = drunk_count / sake_count if sake_count > 0 else 0
        data[str(p.id)] = {
            "name": p.name,
            "sake_count": sake_count,
            "drunk_count": drunk_count,
            "ratio": round(ratio, 3),
        }
    return json.dumps(data, ensure_ascii=False)


# ──────────────────────────────────
#  Prefecture (都道府県)
# ──────────────────────────────────

def prefecture_list(request):
    """都道府県地図"""
    prefectures = Prefecture.objects.annotate(
        sake_count=Count("breweries__sakes"),
    ).order_by("id")

    # ログイン済みなら飲んだ数を取得
    drunk_counts = {}
    if request.user.is_authenticated:
        logs = (
            SakeLog.objects.filter(user=request.user, is_drunk=True)
            .values("sake__brewery__prefecture")
            .annotate(cnt=Count("id"))
        )
        drunk_counts = {row["sake__brewery__prefecture"]: row["cnt"] for row in logs}

    map_data = _build_map_data(prefectures, drunk_counts)

    return render(request, "sake_app/prefecture_list.html", {
        "prefectures": prefectures,
        "map_data": map_data,
    })


def prefecture_detail(request, pk):
    """都道府県の詳細 ─ その県の日本酒一覧"""
    prefecture = get_object_or_404(Prefecture, pk=pk)
    sakes = Sake.objects.filter(
        brewery__prefecture=prefecture,
    ).select_related("brewery")
    return render(request, "sake_app/prefecture_detail.html", {
        "prefecture": prefecture,
        "sakes": sakes,
    })


# ──────────────────────────────────
#  Sake (日本酒)
# ──────────────────────────────────

def sake_list(request):
    """日本酒一覧 + 検索"""
    q = request.GET.get("q", "").strip()
    sakes = Sake.objects.select_related("brewery", "brewery__prefecture")
    if q:
        sakes = sakes.filter(
            Q(name__icontains=q) | Q(brewery__name__icontains=q)
        )
    return render(request, "sake_app/sake_list.html", {
        "sakes": sakes,
        "q": q,
    })


def sake_detail(request, pk):
    """日本酒の詳細 + SakeLog 登録・更新"""
    sake = get_object_or_404(
        Sake.objects.select_related("brewery", "brewery__prefecture"),
        pk=pk,
    )
    sake.f1_percent = sake.f1_hanayaka * 100 if sake.f1_hanayaka is not None else None
    sake.f2_percent = sake.f2_houjun * 100 if sake.f2_houjun is not None else None
    sake.f3_percent = sake.f3_juukou * 100 if sake.f3_juukou is not None else None
    sake.f4_percent = sake.f4_odayaka * 100 if sake.f4_odayaka is not None else None
    sake.f5_percent = sake.f5_dry * 100 if sake.f5_dry is not None else None
    sake.f6_percent = sake.f6_keikai * 100 if sake.f6_keikai is not None else None

    # ログインユーザーの既存ログを取得（あれば編集、なければ新規）
    log = None
    form = None
    if request.user.is_authenticated:
        log = SakeLog.objects.filter(user=request.user, sake=sake).first()

        if request.method == "POST":
            form = SakeLogForm(request.POST, instance=log)
            if form.is_valid():
                sakelog = form.save(commit=False)
                sakelog.user = request.user
                sakelog.sake = sake
                sakelog.save()
                messages.success(request, "ログを保存しました。")
                return redirect("sake_app:sake_detail", pk=sake.pk)
        else:
            form = SakeLogForm(instance=log)

    return render(request, "sake_app/sake_detail.html", {
        "sake": sake,
        "form": form,
        "log": log,
    })


# ──────────────────────────────────
#  SakeLog (日本酒ログ)
# ──────────────────────────────────

@login_required
def sakelog_list(request):
    """ログインユーザーの日本酒ログ一覧（is_drunk=True） + 地図"""
    logs = SakeLog.objects.filter(
        user=request.user,
        is_drunk=True,
    ).select_related("sake", "sake__brewery", "sake__brewery__prefecture")

    # 地図用データ
    prefectures = Prefecture.objects.annotate(
        sake_count=Count("breweries__sakes"),
    ).order_by("id")
    drunk_logs = (
        SakeLog.objects.filter(user=request.user, is_drunk=True)
        .values("sake__brewery__prefecture")
        .annotate(cnt=Count("id"))
    )
    drunk_counts = {row["sake__brewery__prefecture"]: row["cnt"] for row in drunk_logs}
    map_data = _build_map_data(prefectures, drunk_counts)

    return render(request, "sake_app/sakelog_list.html", {
        "logs": logs,
        "map_data": map_data,
    })


@login_required
def sakelog_detail(request, pk):
    """自分の日本酒ログ詳細 + 編集フォーム"""
    log = get_object_or_404(SakeLog, pk=pk, user=request.user)

    if request.method == "POST":
        form = SakeLogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, "ログを更新しました。")
            return redirect("sake_app:sakelog_detail", pk=log.pk)
    else:
        form = SakeLogForm(instance=log)

    return render(request, "sake_app/sakelog_detail.html", {
        "log": log,
        "form": form,
    })


@login_required
def favorite_list(request):
    """お気に入り一覧（is_liked=True のログ）"""
    logs = SakeLog.objects.filter(
        user=request.user,
        is_liked=True,
    ).select_related("sake", "sake__brewery", "sake__brewery__prefecture")
    return render(request, "sake_app/favorite_list.html", {
        "logs": logs,
    })

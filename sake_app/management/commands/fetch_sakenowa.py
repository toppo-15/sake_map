"""
さけのわAPIからデータを取得してDBに保存する管理コマンド

使い方:
    python manage.py fetch_sakenowa

全エンドポイントからデータを取得し、以下の順序でDBに保存する:
    1. areas       → Prefecture
    2. breweries   → Brewery
    3. brands      → Sake
    4. flavor-charts  → Sake 
"""

import requests
from django.core.management.base import BaseCommand
from sake_app.models import Prefecture, Brewery, Sake

BASE_URL = "https://muro.sakenowa.com/sakenowa-data/api"


class Command(BaseCommand):
    def _fetch(self, endpoint):
        """APIからデータを取得する共通メソッド"""
        url = f"{BASE_URL}/{endpoint}"
        self.stdout.write(f"  取得中: {url}")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("さけのわAPIデータ取得開始"))

        # ── 1. 都道府県 (areas) ──
        self.stdout.write(self.style.HTTP_INFO("\n[1/4] 都道府県を取得中..."))
        data = self._fetch("areas")
        areas = data.get("areas", [])
        for area in areas:
            Prefecture.objects.update_or_create(
                id=area["id"],
                defaults={"name": area["name"]},
            )
        self.stdout.write(self.style.SUCCESS(f"  → {len(areas)} 件の都道府県を保存"))

        # ── 2. 蔵元 (breweries) ──
        self.stdout.write(self.style.HTTP_INFO("\n[2/4] 蔵元を取得中..."))
        data = self._fetch("breweries")
        breweries = data.get("breweries", [])
        for b in breweries:
            pref = Prefecture.objects.get(id=b["areaId"])
            Brewery.objects.update_or_create(
                id=b["id"],
                defaults={"name": b["name"], "Prefecture": pref},
            )
        self.stdout.write(self.style.SUCCESS(f"  → {len(breweries)} 件の蔵元を保存"))

        # ── 3. 銘柄 (brands → Sake) ──
        self.stdout.write(self.style.HTTP_INFO("\n[3/4] 銘柄を取得中..."))
        data = self._fetch("brands")
        brands = data.get("brands", [])
        for brand in brands:
            brewery = None
            brewery_id = brand.get("breweryId")
            if brewery_id:
                brewery = Brewery.objects.get(id=brewery_id)
            Sake.objects.update_or_create(
                id=brand["id"],
                defaults={"name": brand["name"], "brewery": brewery},
            )
        self.stdout.write(self.style.SUCCESS(f"  → {len(brands)} 件の銘柄を保存"))

        # ── 4. フレーバーチャート (flavor-charts → Sake に統合) ──
        self.stdout.write(self.style.HTTP_INFO("\n[4/4] フレーバーチャートを取得中..."))
        data = self._fetch("flavor-charts")
        charts = data.get("flavorCharts", [])
        for chart in charts:
            brand_id = chart.get("brandId")
            
            sake = Sake.objects.get(id=brand_id)
            sake.f1_hanayaka = chart.get("f1")
            sake.f2_houjun = chart.get("f2")
            sake.f3_juukou = chart.get("f3")
            sake.f4_odayaka = chart.get("f4")
            sake.f5_dry = chart.get("f5")
            sake.f6_keikai = chart.get("f6")
            sake.save(update_fields=[
                "f1_hanayaka", "f2_houjun", "f3_juukou",
                "f4_odayaka", "f5_dry", "f6_keikai",
            ])
        self.stdout.write(self.style.SUCCESS(f"  → {len(charts)} 件のフレーバーチャートを更新"))

        self.stdout.write(self.style.MIGRATE_HEADING("\nデータ取得完了！"))

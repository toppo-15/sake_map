from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Prefecture(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField("都道府県名", max_length=200, unique=True)
    
    class Meta: 
        ordering = ["id"] 
        verbose_name = "都道府県" 
        verbose_name_plural = "都道府県"

    def __str__(self):
        return self.name
    
class Brewery(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField("蔵元名", max_length=200)
    prefecture = models.ForeignKey(
        Prefecture,
        on_delete=models.CASCADE,
        verbose_name="都道府県",
        related_name="breweries"
    )
    
    class Meta:
        ordering = ["id"]
        verbose_name = "蔵元"
        verbose_name_plural = "蔵元"

    def __str__(self):
        return self.name  

class Sake(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField("銘柄名", max_length=200)
    brewery = models.ForeignKey(
        Brewery,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sakes",
        verbose_name="蔵元",
    )
    
    # --- フレーバーチャート (0.0〜1.0) ---
    f1_hanayaka = models.FloatField("華やか", null=True, blank=True)
    f2_houjun = models.FloatField("芳醇", null=True, blank=True)
    f3_juukou = models.FloatField("重厚", null=True, blank=True)
    f4_odayaka = models.FloatField("穏やか", null=True, blank=True)
    f5_dry = models.FloatField("ドライ", null=True, blank=True)
    f6_keikai = models.FloatField("軽快", null=True, blank=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "日本酒"
        verbose_name_plural = "日本酒"

    def __str__(self):
        return self.name

    @property
    def prefecture(self):
        """蔵元経由で都道府県を取得"""
        if self.brewery:
            return self.brewery.prefecture
        return None
    
class SakeLog(models.Model): 
    class Rating(models.IntegerChoices): 
        ONE = 1, "★" 
        TWO = 2, "★★" 
        THREE = 3, "★★★" 
        FOUR = 4, "★★★★" 
        FIVE = 5, "★★★★★" 
        
    user = models.ForeignKey( 
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="sake_logs", 
        verbose_name="ユーザー", 
    )
     
    sake = models.ForeignKey(
        Sake, 
        on_delete=models.CASCADE, 
        related_name="logs", 
        verbose_name="日本酒", 
    ) 
    
    is_liked = models.BooleanField("いいね", default=False) 
    is_drunk = models.BooleanField("飲んだ", default=False) 
    rating = models.IntegerField( 
        "評価", 
        choices=Rating.choices, 
        null=True, 
        blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
    ) 
    
    memo = models.TextField("メモ", blank=True, default="") 
    drunk_at = models.DateField("飲んだ日", null=True, blank=True) 
    created_at = models.DateTimeField("作成日時", auto_now_add=True) 
    updated_at = models.DateTimeField("更新日時", auto_now=True) 
    
    class Meta: 
        ordering = ["-updated_at"] 
        verbose_name = "日本酒ログ" 
        verbose_name_plural = "日本酒ログ" 
        constraints = [
            models.UniqueConstraint( 
                fields=["user", "sake"],
                name="unique_user_sake_log",
            )
        ] 
   
    def __str__(self): 
        return f"{self.user} - {self.sake}"
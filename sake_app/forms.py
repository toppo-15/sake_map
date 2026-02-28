from django import forms
from .models import SakeLog


class SakeLogForm(forms.ModelForm):
    class Meta:
        model = SakeLog
        fields = ["is_drunk", "is_liked", "rating", "drunk_at", "memo"]
        widgets = {
            "is_drunk": forms.CheckboxInput(attrs={"class": "form-check"}),
            "is_liked": forms.CheckboxInput(attrs={"class": "form-check"}),
            "rating": forms.Select(
                choices=[("", "---")] + list(SakeLog.Rating.choices),
                attrs={"class": "form-select"},
            ),
            "drunk_at": forms.DateInput(
                attrs={"type": "date", "class": "form-input"},
            ),
            "memo": forms.Textarea(
                attrs={"rows": 3, "class": "form-textarea", "placeholder": "感想やメモを入力..."},
            ),
        }

from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    full_name = forms.CharField(label="姓名", max_length=100)
    phone_number = forms.CharField(label="電話號碼", max_length=15)
    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username",)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("兩次輸入的密碼不一致")

        return cleaned_data
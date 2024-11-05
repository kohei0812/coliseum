from django import forms

class DateInput(forms.DateInput):
    input_type = 'date'

class MyForm(forms.Form):
    date = forms.DateField(
        widget=DateInput(attrs={
            'class': 'form-control',  # 必要に応じてCSSクラスを追加
            'placeholder': 'Select a date'
        }),
        label='日付'
    )

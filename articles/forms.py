from django import forms

from articles.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["author_name", "text"]
        labels = {
            "author_name": "Имя автора",
            "text": "Комментарий",
        }
        widgets = {
            "author_name": forms.TextInput(attrs={"placeholder": "Введите ваше имя"}),
            "text": forms.Textarea(attrs={"rows": 4, "placeholder": "Напишите комментарий..."}),
        }

from django import forms

from articles.models import Comment

BANNED_WORDS = ["спам", "реклама", "дурак"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {
            "text": "Комментарий",
        }
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "placeholder": "Напишите комментарий..."}),
        }

    def clean_text(self) -> str:
        text = self.cleaned_data.get("text", "")
        if len(text.strip()) < 5:
            raise forms.ValidationError("Комментарий должен содержать не менее 5 символов.")
        text_lower = text.lower()
        for word in BANNED_WORDS:
            if word in text_lower:
                raise forms.ValidationError(f"Комментарий содержит запрещённое слово: {word}.")
        return text


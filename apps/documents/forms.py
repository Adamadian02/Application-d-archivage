# pyrefly: ignore [missing-import]
from django import forms
from .models import Document, Tag

class DocumentForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tag1, tag2, tag3'}),
        label='Tags (séparés par des virgules)'
    )

    class Meta:
        model = Document
        fields = ['titre', 'description', 'fichier', 'categorie', 'confidentialite']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du document'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fichier': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.ppt,.pptx'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'confidentialite': forms.Select(attrs={'class': 'form-select'}),
        }

    def save(self, commit=True):
        doc = super().save(commit=False)
        if commit:
            doc.save()
            tags_str = self.cleaned_data.get('tags_input', '')
            if tags_str:
                doc.tags.clear()
                for tag_nom in tags_str.split(','):
                    tag_nom = tag_nom.strip()
                    if tag_nom:
                        tag, _ = Tag.objects.get_or_create(nom=tag_nom)
                        doc.tags.add(tag)
        return doc

class LegacyDocumentForm(DocumentForm):
    class Meta(DocumentForm.Meta):
        fields = ['titre', 'description', 'fichier', 'categorie', 'confidentialite', 'created_at']
        widgets = DocumentForm.Meta.widgets.copy()
        widgets['created_at'] = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Surcharge du label pour être plus explicite sur cette interface
        self.fields['created_at'].label = "Date d'origine de l'archive (JJ/MM/AAAA)"

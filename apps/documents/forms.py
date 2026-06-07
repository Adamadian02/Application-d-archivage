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
    # Champ séparé : created_at est auto_now_add donc non-éditable via ModelForm
    date_origine = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date d'origine de l'archive"
    )

    class Meta(DocumentForm.Meta):
        # Pas de created_at ici — il sera appliqué manuellement dans la vue
        fields = ['titre', 'description', 'fichier', 'categorie', 'confidentialite']

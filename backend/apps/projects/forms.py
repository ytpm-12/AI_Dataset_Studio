from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')
        labels = {
            'name': 'Nom du projet',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ex: Analyse des ventes'}),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Objectif et contexte du projet',
                    'rows': 5,
                }
            ),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()

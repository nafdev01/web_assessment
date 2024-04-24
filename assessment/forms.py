from django import forms


class AssessmentForm(forms.Form):
    """This is a form for a url during an assessment."""

    url_here = forms.URLField(max_length=255)

    # TODO: Define form fields here

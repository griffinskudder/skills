from contextlib import contextmanager

from django import forms
from django.db import connection
from django.http import HttpResponse


def render(rows, cache_choices):
    def choices():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        count = 100 if cache_choices else 2
        return [(i, f"Product {i}") for i in range(count)]

    shared = choices() if cache_choices else None

    class Line(forms.Form):
        product = forms.ChoiceField()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["product"].choices = shared or choices()

    formset = forms.formset_factory(Line, extra=rows)()
    return HttpResponse(str(formset))


@contextmanager
def repeated():
    yield lambda: render(2, False), lambda: render(20, False)


@contextmanager
def bulky():
    yield lambda: render(2, True), lambda: render(20, True)

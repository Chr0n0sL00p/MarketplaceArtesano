from django import template

register = template.Library()

@register.filter
def eq(value, arg):
    """
    Compara dos valores convirtiéndolos a string para evitar problemas de tipos.
    Uso: {{ value|eq:arg }}
    Devuelve True si son iguales, False si no.
    """
    try:
        return str(value) == str(arg)
    except:
        return value == arg

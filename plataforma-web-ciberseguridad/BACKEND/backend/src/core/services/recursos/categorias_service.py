from ...models.categoria_recurso import CategoriaRecurso
from ...models import CategoriaRecurso, RecursoEducativo

def all_categorias_recursos():
    
    result = CategoriaRecurso.objects.all()
    return result

def crear_nuevo_recurso(titulo, descripcion, url_recurso, tipo_recurso, es_publico, categoria_id=None):
    categoria = None
    if categoria_id:
        # Si la categoría no existe, dejamos que levante el error para que el controlador lo maneje
        categoria = CategoriaRecurso.objects.get(categoria_id=categoria_id)

    recurso = RecursoEducativo.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        url_recurso=url_recurso,
        tipo_recurso=tipo_recurso,
        es_publico=es_publico,
        categoria=categoria
    )
    return recurso
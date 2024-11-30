from django.http.response import HttpResponse
from django.http import StreamingHttpResponse as DjangoStreamingHttpResponse
from django.template.loader import render_to_string
import json
from datastar_py import ServerSentEventGenerator, SSE_HEADERS
from datastar_py.consts import FragmentMergeMode as MERGE
from .models import Todo

class DatastarDjangoResponse(DjangoStreamingHttpResponse):
    def __init__(self, generator, *args, **kwargs):
        sse = ServerSentEventGenerator()
        kwargs["headers"] = SSE_HEADERS
        super().__init__(generator(sse), *args, **kwargs)

async def homepage(request):
    todos = [todo async for todo in Todo.objects.all().order_by('-id')]
    store_dict = {f'todo_check_{i.pk}':i.item_done for i in todos}
    store_dict.update({'todoInput':'', 'show':True})
    store = json.dumps(store_dict)
    # render full page
    return HttpResponse(
        render_to_string('datastar/todo_home.html', {'store': store, 'todos': todos})
    )

async def add_todos(request):
    store_in = json.loads(request.GET.get('datastar'))
    if store_in['todoInput']:  # if user entered text, create new to do entry
        new_todo = await Todo.objects.acreate(item=store_in['todoInput'])
    async def update_frag(sse):
        target = '#todo-list'
        # render the html fragment to str before sending via sse
        page = render_to_string('datastar/list_segment.html', {'item': new_todo})
        yield sse.merge_fragments(fragments=[page], merge_mode=MERGE.FragmentMergeModePrepend, selector=target)
        yield sse.merge_signals({'todoInput':''})  # clear the input
    return DatastarDjangoResponse(update_frag)

async def check_off_todo(request, pk):
    todo = await Todo.objects.aget(pk=pk)
    todo.item_done = not todo.item_done  # toggle done state
    await todo.asave()
    async def update_frag(sse):  # update the store value which will update the client side html
        yield sse.merge_signals({f'todo_check_{pk}':todo.item_done})
    return DatastarDjangoResponse(update_frag)

async def clear_todos(request):
    # create a queryset of items to delete and iterate over them
    async def remove_frag(sse):
        async for item in Todo.objects.filter(item_done=True):
            yield sse.remove_fragments('#todo_'+str(item.pk))
            await item.adelete()
    return DatastarDjangoResponse(remove_frag)

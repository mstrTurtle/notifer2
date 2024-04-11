from django.shortcuts import render

# Create your views here.

from .models import Message, Event
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)

def messages_list(request):
    messages = Message.objects.all()
    return render(request, 'notification_app/messages_list.html', {'messages': messages})


def events_list(request):
    events = Event.objects.all()
    return render(request, 'notification_app/events_list.html', {'events': events})

def cancel_message(request):
    pk = request.GET.get('pk')
    Message.objects.filter(pk=pk).update(status='canceled')

    return redirect('message_list')

from django.core.paginator import Paginator
from django.shortcuts import render
from .forms import MessageForm
from .models import Message
from .startup import addOneMessage,submitMessageAsync

def message_list(request):
    # 获取所有的Message记录
    messages = Message.objects.all().order_by('-send_time')

    # 分页处理
    paginator = Paginator(messages, 10)  # 每页显示10条记录
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 处理表单提交
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            m = form.save()
            # 重定向到当前页面，以显示新提交的记录
            submitMessageAsync(m)
            return redirect(request.path_info)
    else:
        from django.utils import timezone
        form = MessageForm(initial={'send_time': timezone.now()})

    context = {
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'notification_app/message_list.html', context)


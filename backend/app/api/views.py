import json
import random
import string

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, SuspiciousFileOperation, FieldError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Task
from .models import Image

def test_view(request):
    return make_resp(200, {'msg': 'It works !!'})

@csrf_exempt
def task_upload_view(request):

    # parse POST data
    task_name = request.POST.get('task_name')
    vertical_division = request.POST.get('vertical_division')
    images = request.FILES

    # 400 Bad Request
    if task_name == None or vertical_division == None or len(images) == 0:
        return make_resp(400, {'msg': 'POST data not parsed'})

    try:
        # new task
        new_task = Task(
            code = generate_taskcode(code_len=10), 
            name = task_name
        )
        new_task.save()
    except:
        return make_resp(400, {})

    try:
        # save images
        fs = FileSystemStorage()

        for image_label in images:
            # save image file to file storage
            filename = fs.save(image_label, images[image_label])
            uploaded_image_url = fs.url(filename)

            new_image = Image(
                task_id = new_task.id,
                src = uploaded_image_url,
                label = image_label,
                vertical_division = vertical_division,
                rects_list = '[]'
            )
            new_image.save()
    except SuspiciousFileOperation:
        return make_resp(400, {'msg': 'SuspiciousFileOperation'})
    except:
        return make_resp(400, {})

    data = {
        'task_name': new_task.name,
        'task_code': new_task.code
    }
    return make_resp(200, data)

@csrf_exempt
def image_update_view(request):

    rects_list = request.POST.get('rects_list')
    image_id = request.POST.get('image_id')

    # print(rects_list)
    # print(image_id)
    if image_id == None or rects_list == None:
        return make_resp(400, {'msg': 'POST data not parsed'})

    try:
        image = Image.objects.get(id=image_id)
    except ObjectDoesNotExist:
        return make_resp(404, {'message': 'image object not found'})
    
    try:
        image.rects_list = rects_list
        image.save()
    except FieldError:
        return make_resp(400, {'msg': 'FieldError'})
    except:
        return make_resp(400, {})

    return make_resp(200, {})

def task_get_view(request):
    task_code = request.GET.get('task_code')
    if task_code == None:
        return make_resp(400, {'msg': 'task_code not parsed'})

    try:
        task = Task.objects.get(code=task_code)
    except ObjectDoesNotExist:
        return make_resp(404, {'message': 'task not found with code: ' + task_code})

    images = Image.objects.filter(task_id=task.id)

    data = {
        'task': task.name,
        'images': []
    }
    if len(images) > 0:
        data['divide'] = images[0].vertical_division

        for image in images:
            data['images'].append({
                'id': image.id,
                'src': image.src,
                'rects_list': image.rects_list,
                'vertical_division': image.vertical_division,
                'label': image.label
            })

    return make_resp(200, data)

def task_download_view(request):
    task_code = request.GET.get('task_code')
    if task_code == None:
        return make_resp(400, {'msg': 'task_code not parsed'})

    try:
        task = Task.objects.get(code=task_code)
    except ObjectDoesNotExist:
        return make_resp(404, {'message': 'task not found with code: ' + task_code})

    images = Image.objects.filter(task_id=task.id)

    data = {
        'task': task.name,
        'divide': 0,
        'images': []
    }
    if len(images) > 0:
        data['divide'] = images[0].vertical_division

        for image in images:
            data['images'].append({
                'label': image.label,
                'pathname': image.src,
                'regions': json.loads(image.rects_list),
                'vertical_division': image.vertical_division,
            })

    return make_resp(200, data)

def generate_taskcode(code_len=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(code_len))

def make_resp(status, data):
    return JsonResponse(data, status=status)


test = test_view

task_upload = task_upload_view
image_update = image_update_view
task_get = task_get_view
task_download = task_download_view
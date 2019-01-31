from django.shortcuts import render
from django.http import StreamingHttpResponse
import subprocess


def users(request):
    def file_iterator(file_name, chunk_size=512):
        with subprocess.Popen(['python', 'manage.py', 'dumpdata', 'login'], stdout=subprocess.PIPE) as f:
            while True:
                c = f.stdout.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    the_file_name = "login.json"
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response


def inventory(request):
    def file_iterator(file_name, chunk_size=512):
        with subprocess.Popen(['python', 'manage.py', 'dumpdata', 'inventory'], stdout=subprocess.PIPE) as f:
            while True:
                c = f.stdout.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    the_file_name = "inventory.json"
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response


def trace(request):
    def file_iterator(file_name, chunk_size=512):
        with subprocess.Popen(['python', 'manage.py', 'dumpdata', 'trace_item'], stdout=subprocess.PIPE) as f:
            while True:
                c = f.stdout.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    the_file_name = "trace_item.json"
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response

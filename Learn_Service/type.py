# from typing import Dict


# type JSONDict = Dict[str, int | str | None | bool ]

# print(type("string"))

# dic: JSONDict = {"data": "Me"}

# print(type(JSONDict))

# data = [] or 90

# def empty_generator():
#     yield 0

# mygen = empty_generator()

# print(mygen)


# number = 45
# print(hex(number)[2
#                   :])  # Output: 45

# from pathlib import Path
# import os

# name = __file__

# print(Path(name).suffix.lower())

# name.seek(0, os.SEEK_END)
# size = name.tell()
# name.seek(0)  # Reset pointer
# print(size)  # Output: 0
        
# import subprocess

# # Example: Get metadata from a video
# result = subprocess.run(
#     ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", "./video.mp4"],
#     stdout=subprocess.PIPE,
#     stderr=subprocess.STDOUT
# )

# # Output JSON data
# import json
# info = json.loads(result.stdout)
# print(info['format']['duration'])  # Example: print video duration
# forms.py
from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']


# views.py
from django.shortcuts import render, redirect
from .models import Document

import uuid

def upload_file_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        
        instance = Document(title=request.POST.get('title', 'Untitled'))
        instance.file.save(unique_filename, uploaded_file)  # This handles chunking!
        instance.save()

        return render(request, 'upload_success.html', {'file_url': instance.file.url})
    
    return render(request, 'upload_form.html')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedFile

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        description = request.POST.get('description', '') #get the description from the post data.

        try:
            instance = UploadedFile(file=uploaded_file, description=description)
            instance.save() #save the model instance.
            file_url = instance.file.url
            return JsonResponse({'message': 'File uploaded successfully', 'url': file_url, 'id': instance.id}) #return the id.
        except Exception as e:
            return JsonResponse({'error': f'Error uploading file: {e}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request or no file provided'}, status=400)
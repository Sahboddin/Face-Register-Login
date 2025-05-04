import face_recognition
import face_recognition_models

import base64
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import UserImage,User
import os
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def register_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        face_image_data = request.POST['face_image']

        # Convert base64 image data to a file
        face_image_data = face_image_data.split(",")[1]  # Remove the "data:image/jpeg;base64," part
        face_image = ContentFile(base64.b64decode(face_image_data), name=f'{username}_face.jpg')

        # Save the user and face image in the database
        user = User(username=username)
        user.save()
        user_image = UserImage.objects.create(user = user, face_image = face_image)

        return JsonResponse({'status': 'success', 'message': 'User registered successfully!'})

    

    return render(request, 'register.html')


# @csrf_exempt
# def login_user(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         face_image_data = request.POST['face_image']

#         # Get the user by username
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'User not found.'})

#         # Convert base64 image data to a file
#         face_image_data = face_image_data.split(",")[1]
#         uploaded_image = ContentFile(base64.b64decode(face_image_data), name=f'{username}_face.jpg')

#         # Compare the uploaded face image with the stored face image
#         uploaded_face_image = face_recognition.load_image_file(uploaded_image)
#         uploaded_face_encoding = face_recognition.face_encodings(uploaded_face_image)

#         if uploaded_face_encoding:
#             uploaded_face_encoding = uploaded_face_encoding[0]
#             user_image = UserImage.objects.filter(user = user).first()
#             stored_face_image = face_recognition.load_image_file(user_image.face_image.path)
#             stored_face_encoding = face_recognition.face_encodings(stored_face_image)[0]

#             print(stored_face_image,stored_face_encoding)
#             # Compare the faces
#             match = face_recognition.compare_faces([stored_face_encoding], uploaded_face_encoding)
#             if match[0]:
#                 return JsonResponse({'status': 'success', 'message': 'Login successful!'})
#             else:
#                 return JsonResponse({'status': 'error', 'message': 'Face recognition failed.'})

#         return JsonResponse({'status': 'error', 'message': 'No face detected in the image.'})
   
#     return render(request, 'login.html')




import base64
from io import BytesIO
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import face_recognition
import face_recognition_models  # ensure installed via GitHub URL
from .models import UserImage, User

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username        = request.POST['username']
        face_image_data = request.POST['face_image']

        # 1) Lookup user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status':'error','message':'User not found.'})

        # 2) Decode Base64 to raw bytes
        image_data = face_image_data.split(',', 1)[1]
        img_bytes  = base64.b64decode(image_data)

        # 3) === FIX: load via BytesIO so load_image_file decodes into uint8 RGB ===
        img_stream = BytesIO(img_bytes)
        np_img     = face_recognition.load_image_file(img_stream)
        # load_image_file only accepts 8-bit gray or RGB images and returns a uint8 NumPy array :contentReference[oaicite:1]{index=1}
        # ------------------------------------------------------------------------

        # 4) Get face encodings
        encodings = face_recognition.face_encodings(np_img)
        if not encodings:
            return JsonResponse({'status':'error','message':'No face detected.'})
        uploaded_encoding = encodings[0]

        # 5) Load stored image from disk the same way
        user_image    = UserImage.objects.filter(user=user).first()
        stored_np_img = face_recognition.load_image_file(user_image.face_image.path)
        stored_encs   = face_recognition.face_encodings(stored_np_img)
        if not stored_encs:
            return JsonResponse({'status':'error','message':'No face in stored image.'})
        stored_encoding = stored_encs[0]

        # 6) Compare
        match = face_recognition.compare_faces([stored_encoding], uploaded_encoding)
        if match[0]:
            return JsonResponse({'status':'success','message':'Login successful!'})
        else:
            return JsonResponse({'status':'error','message':'Face recognition failed.'})

    return render(request, 'login.html')

from django.shortcuts import render,redirect,HttpResponse
from app.EmailBackEnd import EmailBackEnd
from django.contrib.auth import authenticate,logout,login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import CustomUser
from app.models import Teacher,Add_Notice
from django.http import JsonResponse
import face_recognition as fr
import base64
import numpy as np
import io



def HOME(request):
    return render(request,'home.html')

def CONTRACT(request):
    return render(request,'contract.html')


def ABOUT(request):
    teacher= Teacher.objects.all()

    context={
        'teacher':teacher,
    }
    return render(request,'about.html',context)



def clear_notifications(request):
   
    notifications = Add_Notice.objects.all()
    notifications.delete()  
    
    return redirect('login')


def BASE(request):
    return render(request,'base.html')

def LOGIN(request):
    return render(request,'login.html')

def JOIN_NOW(request):
    return render(request,'join_now.html')

def dologin(request):
    user_type = None
    if request.method == "POST":
        user  = EmailBackEnd().authenticate(request,
                                          username=request.POST.get('username'),
                                          password=request.POST.get('password'))
        if user != None:
            login(request,user)
            user_type= user.user_type
        if user_type == 1:
           return redirect('admin_home')
            
        elif user_type == 2:
            return redirect('teacher-home')
        elif user_type == 3:
            return redirect('student-home')
            
        else:
            messages.error(request,'Username and Password Are Invalid')
            return redirect('login')
    else:
        messages.error(request,'Username and Password Are Invalid')
        return redirect('login')




def  FACE_ID_LOGIN(request):
    return render(request,"face_id_login.html")



def dologout(request):
    logout(request)
    return redirect('login')



@login_required(login_url='login')
def PROFILE(request):
    user= CustomUser.objects.get(id=request.user.id)
    context ={
        'user':user,
    }
    return render(request,'profile.html',context)

@login_required(login_url='login')
def PROFILE_UPDATE(request):
    if request.method == 'POST':
        first_name =request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        username =request.POST.get('username')
        password =request.POST.get('password')
        
        
      
        profile_pic = request.FILES.get('profile_pic')
        print(profile_pic)
        
        #upolad this data django database
        try:
            customuser = CustomUser.objects.get(id= request.user.id)
            
            if first_name != None and first_name != "":
                customuser.first_name=first_name
            
            if last_name != None and last_name != "":
                customuser.last_name=last_name

            

            
            if profile_pic != None and profile_pic != "":
                customuser.profile_pic=profile_pic

            #customuser.username= username
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request,'Your Profile Updated Successfully')
            return redirect('profile')
            
      
        except:
            messages.error(request,'Failed To Update Your Profile')

    return render(request,'profile.html')



def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces():
    users = CustomUser.objects.all()

    encoded = {}

    for user in users:
        if user.profile_pic:
            face = fr.load_image_file(user.profile_pic.path)
            face_encodings = fr.face_encodings(face)

            if len(face_encodings) > 0:
                encoding = face_encodings[0]
                encoded[user.username] = encoding
            else:
                print(f"No face found in the profile picture of user: {user.username}")
        else:
            print(f"No profile picture found for user: {user.username}")

    return encoded



def classify_face(img):
    """
    This function takes an image as input and returns the name of the face it contains
    """
    # Load all the known faces and their encodings
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    # Load the input image
    img = fr.load_image_file(img)
 
    try:
        # Find the locations of all faces in the input image
        face_locations = fr.face_locations(img)

        # Encode the faces in the input image
        unknown_face_encodings = fr.face_encodings(img, face_locations)

        # Identify the faces in the input image
        face_names = []
        for face_encoding in unknown_face_encodings:
            # Compare the encoding of the current face to the encodings of all known faces
            matches = fr.compare_faces(faces_encoded, face_encoding)

            # Find the known face with the closest encoding to the current face
            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)

            # If the closest known face is a match for the current face, label the face with the known name
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            else:
                name = "Unknown"

            face_names.append(name)

        # Return the name of the first face in the input image
        return face_names[0]
    except:
        # If no faces are found in the input image or an error occurs, return False
        return False


def FACE_ID_DOLOGIN(request):
    if is_ajax(request):
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')
        decoded_file = base64.b64decode(str_img)

        # Convert the decoded image data to a file-like object
        img_file = io.BytesIO(decoded_file)

        # Pass the file-like object to the classify_face function
        res = classify_face(img_file)
        
        if res:  # Check if face classification was successful
            user_exists = CustomUser.objects.filter(username=res).exists()
            if user_exists:
                user = CustomUser.objects.get(username=res)
                login(request, user)
                user_type= user.user_type

                if user_type == 1:
                    redirect_url = 'admin-home'
                elif user_type == 2:
                    redirect_url = 'teacher-home'
                elif user_type == 3:
                    redirect_url = 'student-home'
                else:
                    redirect_url = None

                if redirect_url:
                    return JsonResponse({'redirect_url': redirect_url})
                
    error_msg = "Face Not Found. Please Take The Photo Again."
    return JsonResponse({'error': error_msg}, status=400)
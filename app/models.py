from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER = (
        (1, 'ADMIN'),
        (2, 'TEACHER'),
        (3, 'STUDENT'),
    )

    username = models.CharField(max_length=50, unique=True)
    user_type = models.IntegerField(choices=USER, default=1)
    profile_pic = models.ImageField(upload_to='media/profile_pic', null=True, blank=True)
    first_name = models.CharField(max_length=30, )  # Add first name field
    last_name = models.CharField(max_length=30,)   # Add last name field
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class Class(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Course(models.Model):
    class1= models.ForeignKey(Class, on_delete=models.CASCADE,default=1)
    name = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Session_Year(models.Model):
    

    session_start= models.CharField(max_length=100)
    session_end= models.CharField(max_length=100)

    def __str__(self):
        return self.session_start + ' To ' + self.session_end
    


class Student(models.Model):
    admin= models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=100, blank=True, null=True)
    mothers_name = models.CharField(max_length=100, blank=True, null=True)
    
    roll_number = models.CharField(max_length=10, blank=True, null=True)
    class_id= models.ForeignKey(Class, on_delete=models.DO_NOTHING,default=1)
    
    session_year_id = models.ForeignKey(Session_Year, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return self.admin.first_name + ' ' + self.admin.last_name
    


class Teacher(models.Model):
      admin= models.OneToOneField(CustomUser, on_delete=models.CASCADE)
      phone_number = models.CharField(max_length=15)
      address = models.TextField()
      gender = models.CharField(max_length=100)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at= models.DateTimeField(auto_now=True)
      def __str__(self):
        return self.admin.username




class Subject(models.Model):
    name = models.CharField(max_length=100)
    class1 = models.ForeignKey(Class,on_delete=models.CASCADE,default=1)
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    

class Practice_Exam(models.Model):
    exam_name = models.CharField(max_length=50)
    total_questions = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    class_id= models.ForeignKey(Class, on_delete=models.CASCADE,default=0)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    duration = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.exam_name


class PracticeExamTimer(models.Model):
    exam = models.ForeignKey(Practice_Exam,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    def __str__(self):
        return self.exam.exam_name


class PracticeExamQuestion(models.Model):
    exam =models.ForeignKey(Practice_Exam,on_delete=models.CASCADE,default=0)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200,choices=cat)

    def __str__(self):
        return self.exam.exam_name



class Practice_Exam_Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Practice_Exam,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)



class Star_student(models.Model):
   student_name = models.CharField(max_length=50)
   user_class = models.CharField(max_length=10, blank=True, null=True)
   roll = models.PositiveIntegerField()
   mark = models.PositiveIntegerField()
   persentage = models.CharField(max_length=10, blank=True, null=True)
   year = models.PositiveIntegerField()

   def __str__(self):
        return self.student_name

class Student_activity(models.Model):
    date = models.DateTimeField(auto_now_add=True,null=True)
    description = models.TextField()
    



class Teacher_Notification(models.Model):
    teacher_id= models.ForeignKey(Teacher,on_delete=models.CASCADE)
    message= models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)
    status = models.IntegerField(null=True,default=0)

    def __str__(self):
        return self.teacher_id.admin.first_name
    

class Teacher_Feedback(models.Model):
    teacher_id= models.ForeignKey(Teacher,on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.teacher_id.admin.first_name + " " + self.teacher_id.admin.last_name
    

class Student_Notification(models.Model):
    student_id= models.ForeignKey(Student,on_delete=models.CASCADE)
    message= models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)
    status = models.IntegerField(null=True,default=0)

    def __str__(self):
        return self.student_id.admin.first_name



class Student_Feedback(models.Model):
    student_id= models.ForeignKey(Student,on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_id.admin.first_name + " " + self.student_id.admin.last_name
    


class Attendance(models.Model):
    class_id = models.ForeignKey(Class,on_delete=models.DO_NOTHING,default=1)
    attendance_date = models.DateField()
    session_year_id = models.ForeignKey(Session_Year,on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.class_id.name


class Attendance_Report(models.Model):
    student_id = models.ForeignKey(Student,on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_id.admin.first_name + " " + self.student_id.admin.last_name



class StudentResult(models.Model):
    student_id = models.ForeignKey(Student,on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject,on_delete=models.CASCADE)
    assignment_mark = models.IntegerField()
    exam_mark = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_id.admin.first_name + " " + self.student_id.admin.last_name




class Add_Notice(models.Model):
      
      notice = models.TextField()
      
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at= models.DateTimeField(auto_now=True)
      def __str__(self):
        return self.notice



class OnlineLiveClass(models.Model):
    topic = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    duration = models.IntegerField()
    zoom_meeting_id = models.CharField(max_length=255, unique=True)  # Unique ID from Zoom
    start_url = models.URLField()
    join_url = models.URLField()
    password = models.CharField(max_length=255)
    agenda = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.topic
    

class Live_Exam(models.Model):
    exam_name = models.CharField(max_length=50)
    total_questions = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    class_id= models.ForeignKey(Class, on_delete=models.CASCADE,default=0)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.DurationField(default=0)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.exam_name


class Live_Exam_Report(models.Model):
    exam = models.ForeignKey(Live_Exam,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='taken_exams', blank=True, null=True)
    is_taken = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.exam.exam_name


class LiveExamTimer(models.Model):
    exam = models.ForeignKey(Live_Exam,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    def __str__(self):
        return self.exam.exam_name


class LiveExamQuestion(models.Model):
    exam =models.ForeignKey(Live_Exam,on_delete=models.CASCADE,default=0)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200,choices=cat)

    def __str__(self):
        return self.exam.exam_name


class Live_Exam_Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Live_Exam,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)

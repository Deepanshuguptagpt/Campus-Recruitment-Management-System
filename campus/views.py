from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.core.mail import EmailMessage

from .forms import (
    Student_SignUpForm, UsdForm, dispstuForm,
    company_SignUpForm, ccdForm, jobposForm
)

from campus.models import (
    stu_details, comp_details, job_pos, applied_jobs
)


# ------------------ Student Login ------------------
def student_login(request):
    if request.user.is_authenticated and request.user.groups.filter(name='student').exists():
        return render(request, 'campus/stulog.html')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if request.user.groups.filter(name='student').exists():
                return render(request, 'campus/stulog.html')
            else:
                logout(request)
        return render(request, 'campus/student_login.html', {'form': form})

    return render(request, 'campus/student_login.html', {'form': AuthenticationForm()})


# ------------------ Home ------------------
def home(request):
    return render(request, 'campus/home.html')


# ------------------ Logout ------------------
def pagelogout(request):
    logout(request)
    return redirect('/')


# ------------------ Student Registration ------------------
def student_register(request):
    if request.method == 'POST':
        form = Student_SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='student')
            user.groups.add(group)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/student/student_login/')

        return render(request, 'campus/register.html', {'form': form})

    return render(request, 'campus/register.html', {'form': Student_SignUpForm()})


# ------------------ Student Update Details ------------------
def usd(request):
    stu = request.user.username
    
    # If record exists → load it
    if stu_details.objects.filter(username=stu).exists():
        post = stu_details.objects.get(username=stu)
    else:
        post = None
    
    if request.method == "POST":
        form = UsdForm(request.POST, instance=post)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.username = stu
            obj.save()
            return redirect('/student/student_login/')
    else:
        form = UsdForm(instance=post)

    return render(request, 'campus/usd.html', {'form': form})



# ------------------ Student Display ------------------
def dispstu(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='student').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    stu = request.user.username
    post = stu_details.objects.filter(username=stu)
    return render(request, 'campus/dispstu.html', {'form': dispstuForm(), 'post': post})


# ------------------ Company Registration ------------------
def company_register(request):
    if request.method == 'POST':
        form = company_SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='company')
            user.groups.add(group)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            c = comp_details()
            c.username = username
            c.company_name = request.POST.get('company_name')
            c.email = request.POST.get('email')
            c.est_year = request.POST.get('est_year')
            c.type = request.POST.get('type')
            c.about = request.POST.get('about')
            c.hr_name = request.POST.get('hr_name')
            c.hr_phn = request.POST.get('hr_phn')
            c.headquaters = request.POST.get('headquaters')
            c.save()

            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')

        return render(request, 'campus/register1.html', {'form': form})

    return render(request, 'campus/register1.html', {'form': company_SignUpForm()})


# ------------------ Company Login ------------------
def company_login(request):
    if request.user.is_authenticated and request.user.groups.filter(name='company').exists():
        return render(request, 'campus/comlog.html')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if request.user.groups.filter(name='company').exists():
                return render(request, 'campus/comlog.html')

            logout(request)
        return render(request, 'campus/company_login.html', {'form': form})

    return render(request, 'campus/company_login.html', {'form': AuthenticationForm()})


# ------------------ Company Update Details ------------------
def ccd(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='company').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    comp = request.user.username
    post = comp_details.objects.filter(username=comp).first()

    if request.method == "POST":
        form = ccdForm(request.POST)
        if form.is_valid():
            post.hr_name = request.POST.get('hr_name')
            post.hr_phn = request.POST.get('hr_phn')
            post.about = request.POST.get('about')
            post.save()
            return render(request, 'campus/comlog.html')

    form = ccdForm()
    return render(request, 'campus/ccd.html', {"form": form, "x": post.hr_name, "y": post.hr_phn, "z": post.about})


# ------------------ Add Job Position ------------------
def jobpos(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='company').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    if request.method == "POST":
        form = jobposForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'campus/comlog.html')
        return render(request, 'campus/jobpos.html', {'form': form})

    form = jobposForm()
    comp = request.user.username
    company = comp_details.objects.filter(username=comp).first()
    cname = company.company_name.replace(" ", "_")
    return render(request, 'campus/jobpos.html', {'form': form, 'x': comp, 'y': cname})


# ------------------ Edit Job Details ------------------
def jd(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='company').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    if request.method == "POST":
        job = job_pos.objects.filter(job_id=request.POST.get("job_id")).first()

        if not job:
            return render(request, 'campus/jd.html', {'s': "Wrong job ID"})

        job.designation = request.POST.get("designation")
        job.salary = request.POST.get("salary")
        job.bond_years = request.POST.get("bond_years")
        job.information_technology = request.POST.get("information_technology")
        job.mech = request.POST.get("mech")
        job.civil = request.POST.get("civil")
        job.ece = request.POST.get("ece")
        job.eee = request.POST.get("eee")
        job.chemical = request.POST.get("chemical")
        job.cse = request.POST.get("cse")
        job.save()
        return render(request, 'campus/comlog.html', {'s': ""})

    comp = request.user.username
    company = comp_details.objects.filter(username=comp).first()
    cname = company.company_name.replace(" ", "_")
    return render(request, 'campus/jd.html', {'x': comp, 'y': cname})


# ------------------ Delete Vacancy ------------------
def deletevacan(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='company').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    if request.method == "POST":
        job = job_pos.objects.filter(job_id=request.POST.get("jobid")).first()

        if not job:
            return render(request, 'campus/jobdelete.html', {'s': "Wrong job ID"})

        applied_jobs.objects.filter(job_id=job.job_id).delete()
        job.delete()
        return render(request, 'campus/comlog.html', {'s': "Deleted successfully"})

    return render(request, 'campus/jobdelete.html')


# ------------------ View Posted Jobs ------------------
def viewpos(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='company').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    comp = request.user.username
    jobs = job_pos.objects.filter(username=comp)

    msg = ""
    if len(jobs) == 0:
        msg = "No vacancies posted"

    return render(request, 'campus/viewpos.html', {'y': jobs, 's': msg})


# ------------------ Apply Job ------------------
def applyjob(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='student').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    result = []
    msg = ""

    if request.method == "POST":
        salary = request.POST.get("salary")
        years = request.POST.get("years")
        stu = request.user.username
        branch = stu_details.objects.filter(username=stu).first().branch

        branch_map = {
            "it": "information_technology",
            "cse": "cse",
            "me": "mech",
            "ce": "civil",
            "eee": "eee",
            "ece": "ece",
            "ch": "chemical"
        }

        if branch in branch_map:
            filter_field = {branch_map[branch]: "yes"}
            result = job_pos.objects.filter(
                salary__gte=salary,
                bond_years__lte=years,
                **filter_field
            ).order_by('salary')

        if len(result) == 0:
            msg = "No vacancies for this preference"

        return render(request, 'campus/applyjob.html', {'y': result, 's': msg})

    return render(request, 'campus/applyjob.html', {'y': [], 's': ""})


# ------------------ Apply Job (Step 2) ------------------
def apply(request, opt):
    if not request.user.is_authenticated or not request.user.groups.filter(name='student').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    if request.method == "POST":
        stu = request.user.username
        comp = job_pos.objects.filter(job_id=opt).first().username

        entry = applied_jobs(student_id=stu, company_id=comp, job_id=opt)
        entry.save()

        return HttpResponse("<h1>You applied successfully!</h1>")

    comp = job_pos.objects.filter(job_id=opt).first().username
    company = comp_details.objects.filter(username=comp).first()
    return render(request, 'campus/compdisp.html', {'post': company})


# ------------------ Select Students ------------------
def selectstu(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='company').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    results = []
    msg = ""

    if request.method == "POST":
        jobid = request.POST.get("jobid")
        comp = request.user.username

        if not job_pos.objects.filter(job_id=jobid, username=comp).exists():
            return render(request, 'campus/sstu.html', {'y': [], 's': "Enter correct Job ID"})

        applicants = applied_jobs.objects.filter(job_id=jobid, company_id=comp).values('student_id')

        if not applicants:
            return render(request, 'campus/sstu.html', {'y': [], 's': "No applicants yet"})

        tenth = request.POST.get("tenth")
        twelfth = request.POST.get("twth")
        btech = request.POST.get("btech")

        for stu in applicants:
            filtered = stu_details.objects.filter(
                username=stu['student_id'],
                class_10_cgpa__gte=tenth,
                class_12_percentage__gte=twelfth,
                cgpa_Btech__gte=btech
            )
            if filtered.exists():
                results.append(filtered)

        if not results:
            msg = "Requirements not satisfied"

        return render(request, 'campus/sstu.html', {'y': results, 's': msg})

    return render(request, 'campus/sstu.html', {'y': [], 's': ""})


# ------------------ Send Mail to Selected Student ------------------
def stumail(request, opt):
    if not request.user.is_authenticated or not request.user.groups.filter(name='company').exists():
        return HttpResponse("<h1>You are not logged in</h1>")

    if request.method == "POST":
        student = stu_details.objects.filter(username=opt).first()
        company = comp_details.objects.filter(username=request.user.username).first()

        subject = f"Call letter from {company.company_name}"
        body = f"Congratulations {student.name}! You are selected for the interview."

        email = EmailMessage(subject, body, to=[student.email])
        email.send()

        return HttpResponse("<h1>Mail sent</h1>")

    student = stu_details.objects.filter(username=opt).first()
    return render(request, 'campus/showstudent.html', {'post': student})

from flask.helpers import flash
import psycopg2
from datetime import timedelta
from flask import Flask, redirect, render_template, request, url_for
from flask import session
from datetime import date
import time

conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
conn.autocommit=True
conn.set_isolation_level(0)
cur=conn.cursor()
printdbcr='''
dropdb database if not exists jobportal;
create database jobportal;
'''
createfile = open('./createtables.sql','r')
insertfile=open('./insertrecs.sql','r')

cur.execute("select * from Login")
login_data = cur.fetchall()

if login_data == []:
    cur.execute(createfile.read())
    cur.execute(insertfile.read())
    
cur.close()

conn.commit()
conn.close()


app=Flask(__name__,template_folder='templates')
app.secret_key = "DBMS"
#session.pop("user", None)

role_link='H'
logged_user=''
@app.route('/', endpoint = 'loginpage', methods = ['GET', 'POST'])
def loginpage():
    #signup login for candidate and recruiter
    find = 0
    global role_link
    global logged_user
    if request.method == 'POST':
        # retrieving the entries made in the login form
        loginDetails = request.form
        username = loginDetails['username']
        password = loginDetails['password']
        role = loginDetails['role']
        role_link=role
        logged_user=username
        #print(username, password, role)
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        find = cur.execute('Select * from Login where (login_username, user_password, login_user_type) = (%s, %s,%s) ', (username, password,role))
        # selecting email and password attributes from jobseeker entity to check if the email and its password exists in the entity
        details = cur.fetchall()
        cur.close()
    # login to home page if we find such an entry in the table or redirect to the same page
    if find != 0:
        user = details[0][0]
        session["user"] = user
        #print(user)
        return redirect('/home')
    else: 
        if "user" in session:
            #print('here')
            return redirect('/logout')
        return render_template('login.html', find = find)

@app.route('/signup_cand', endpoint='singup_cand', methods = ['GET', 'POST'])
def signup_cand():
    if request.method == 'POST':
        # retrieving the entries made in the signup form
        userDetails = request.form
        name = userDetails['name']
        username = userDetails['username']
        role = userDetails['role']
        email = userDetails['email']
        address = userDetails['address']
        phone_num = userDetails['phone_num']
        gender = userDetails['gender']
        DOB = userDetails['DOB']
        password = userDetails['password']
        cpassword = userDetails['cpassword']
        # checking if the password entered in both the fields are same
        if password == cpassword and role == 'C':
            conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
            cur=conn.cursor()
            # creating a record by inserting the jobseeker details in jobseeker entity
            cur.execute("INSERT INTO Login(login_username, user_password, login_user_type) VALUES (%s, %s, %s)",(username, password, role))
            cur.execute("select nextval('Candidate_seq')")
            Cand_id = cur.fetchone()
            cur.execute("INSERT INTO Candidate(cand_id, Cand_name, Cand_email,Cand_address, Cand_phone , Cand_DOB, Cand_gender, cand_login_username) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)",(Cand_id, name, email, address,phone_num, DOB,gender,username))
            conn.commit()
            cur.close()
            #print('here')
            # go to login page on submit
            return redirect('/')
        else:
            return redirect('signup_cand')
    return render_template('signup_cand.html')

@app.route('/signup_rec', endpoint='singup_rec', methods = ['GET', 'POST'])
def signup_rec():
    if request.method == 'POST':
        # retrieving the entries made in the signup form
        userDetails = request.form
        name = userDetails['name']
        username = userDetails['username']
        role = userDetails['role']
        email = userDetails['email']
        HQ = userDetails['HQ']
        phone_num = userDetails['phone_num']
        password = userDetails['password']
        cpassword = userDetails['cpassword']
        # checking if the password entered in both the fields are same
        if password == cpassword and role == 'R':
            conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
            cur=conn.cursor()
            # creating a record by inserting the jobseeker details in jobseeker entity
            cur.execute("INSERT INTO Login(login_username, user_password, login_user_type) VALUES (%s, %s, %s)",(username, password, role))
            cur.execute("select nextval('Candidate_seq')")
            emp_id = cur.fetchone()
            cur.execute("INSERT INTO Recruiter(emp_id,emp_name, emp_HQ, emp_phone,emp_email,login_username) VALUES (%s, %s, %s, %s, %s,%s)",(emp_id, name, HQ, phone_num,email, username))
            conn.commit()
            cur.close()
            print('here')
            # go to login page on submit
            return redirect('/')
        else:
            return redirect('signup_rec')
    return render_template('signup_rec.html')

@app.route('/home', endpoint='homepage')
def homepage():
    print(role_link)
    if(role_link=='C'):
        return redirect('/home_cand')
    elif(role_link=='R'):
        return redirect('/home_rec')
    else:
        return "at home page"

@app.route('/jia_cand', endpoint='candidate_jia', methods=['POST','GET'])
def candidate_jia():

    conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
    cur=conn.cursor()
    cur.execute('select job_name, job_type, job_description, emp_name, job_qualifications, job_experience, job_primary_skill, job_id from Job_Profile as j, Recruiter as r where j.recruiter_id=r.emp_id;')
    recarr = cur.fetchall()

    if "user" in session:
        user = session["user"]
        int_sch='''select emp_name, job_name, int_date, int_type, int_result, int_remarks
        from interview as i, job_profile as j, recruiter as r, candidate as c, login as l
        where i.int_job=j.job_id and i.candidateid=c.cand_id and j.recruiter_id=r.emp_id and c.cand_login_username=l.login_username and i.int_result!='PENDING' and l.login_username='{}';'''
        cur.execute(int_sch.format(user))
        interviewarr=cur.fetchall()

        int_pending='''select emp_name, job_name, application_date 
        from applications as a, recruiter as r, job_profile as j, login as l, candidate as c
        where a.application_job_id=j.job_id and j.recruiter_id=r.emp_id and a.application_cand_id=c.cand_id and c.cand_login_username=l.login_username and l.login_username='{}';'''
        cur.execute(int_pending.format(user))
        pendingarr=cur.fetchall()
        conn.commit()
        cur.close()
        return render_template('candidate_page.html', recarr=recarr, intv = interviewarr, pending=pendingarr)

@app.route('/jobsearch', endpoint = 'jobsearch',  methods = ['GET', 'POST'])
def jobsearch():
    if "user" in session:
        if request.method == 'POST':
            searchjob = request.form
            keyword = searchjob['keyword']
            location = searchjob['location']
            conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
            cur=conn.cursor()
            # if only keyword is entered in the job search, then select those jobs where the keyword matches the job details
            # by using LIKE clause and inner join on jobs and corresponding companies 
            if keyword and (not location):
                count_search = cur.execute("select job_name, job_type, emp_name,job_location, job_qualifications, job_experience, job_primary_skill, job_description,  job_vacancy from Job_Profile as j, Job_Profile_job_location as l, Recruiter as r where r.emp_id = j.recruiter_ID and j.job_id=l.job_id and (j.job_name LIKE '%{}%') OR (j.job_type LIKE '%{}%') OR (j.job_description LIKE '%{}%');".format(keyword,keyword,keyword))
            
            # if only location is entered in the job search, then select those jobs where the keyword matches the company location
            # by using LIKE clause and inner join on jobs and corresponding companies
            elif location and (not keyword):
                count_search = cur.execute("select job_name, job_type, emp_name,job_location, job_qualifications, job_experience, job_primary_skill, job_description,  job_vacancy from Job_Profile as j, Job_Profile_job_location as l, Recruiter as r where r.emp_id = j.recruiter_ID and j.job_id=l.job_id and (l.job_location LIKE '%{}%');".format(location))
            
            # if keyword and location are entered in the job search, then select those jobs where the keyword matches the job details
            # and company location by using LIKE clause and inner join on jobs and corresponding companies
            elif location and keyword:
                count_search = cur.execute("select job_name, job_type, emp_name,job_location, job_qualifications, job_experience, job_primary_skill, job_description,  job_vacancy from Job_Profile as j, Job_Profile_job_location as l, Recruiter as r where r.emp_id = j.recruiter_ID and j.job_id=l.job_id and ((j.job_name LIKE '%{}%') OR (j.job_type LIKE '%{}%') OR (j.job_description LIKE '%{}%')) and (l.job_location LIKE '%{}%');".format(keyword,keyword,keyword,location))
            else:
                count_search = 0

            jobsearch = cur.fetchall()
            return render_template('display_search.html', jobsearch = jobsearch)
        '''
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        # display all jobs and their details by selecting all jobs of companies using inner join on job and company
        count_jobs = cur.execute("SELECT job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id")
        
        if count_jobs > 0:
            alljobs = cur.fetchall()'''
        return render_template('search_jobs.html')
    else:
        return redirect(url_for('login'))

@app.route('/home_cand', endpoint='cand_home', methods=['POST','GET'])
def cand_home():
    if "user" in session:
        user = session["user"]
        #print(user)
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        # selecting jobseeker details to display the name of the jobseeker on the home page who is currently logged in
        cur.execute("SELECT * FROM Candidate WHERE cand_login_username = '{}'".format(user))
        userdet = cur.fetchall()
        name = userdet[0][1]
        return render_template('candidate_home.html', name = name)
    else:
        return redirect(url_for('login'))

@app.route('/home_rec', endpoint='rec_home', methods=['POST','GET'])
def rec_home():
    if "user" in session:
        user = session["user"]
        #print(user)
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        # selecting jobseeker details to display the name of the jobseeker on the home page who is currently logged in
        cur.execute("SELECT * FROM Recruiter WHERE login_username = '{}'".format(user))
        userdet = cur.fetchall()
        name = userdet[0][1]
        return render_template('recruiter_home.html', name = name)
    else:
        return redirect(url_for('login'))
    
job_id = 0    
@app.route('/rec_view_jobs', endpoint='recruiter_jobs', methods=['POST','GET'])
def recruiter_jobs():
    global job_id
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        cur.execute("SELECT * FROM Recruiter WHERE login_username = '{}'".format(user))
        userdet = cur.fetchall()
        name = userdet[0][1]
        cur.execute("select j.job_id, job_name, job_type, job_description, job_qualifications, job_experience, job_primary_skill, job_location, job_vacancy from Job_Profile as j, Job_Profile_job_location as l, Recruiter as r where r.login_username = '{}' and r.emp_id = j.recruiter_ID and j.job_id=l.job_id;".format(user))
        jobs = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        
        if request.method == 'POST':
            job_id = request.form.get('j_id')
            return redirect(url_for('update_job', job_id = job_id))  
        
        return render_template('recruiter_jobs.html', jobs = jobs,name = name)
    else:
        return redirect(url_for('login'))
    
@app.route('/update_job', endpoint='update_job', methods=['POST','GET'])
def update_job():
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        cur.execute("SELECT * FROM Recruiter WHERE login_username = '{}'".format(user))
        userdet = cur.fetchall()
        name = userdet[0][1]
         
        cur.execute("select j.job_id, job_name, job_type, job_description, job_qualifications, job_experience, job_primary_skill, job_location, job_vacancy from Job_Profile as j, Job_Profile_job_location as l, Recruiter as r where r.login_username = '{}' and r.emp_id = j.recruiter_ID and j.job_id=l.job_id and j.job_id = '{}';".format(user,job_id))
        old_details = cur.fetchall()
        loc = old_details[0][7]
        
        if request.method == 'POST':
            profile=request.form
            print(profile)
            type = profile["type"]
            description=profile["description"]
            qualification =profile["qualification"]
            experience =profile["experience"]
            skill =profile["skill"]
            location =profile["location"]
            vacancy =profile["vacancy"]
            cur.execute("update Job_Profile set job_type=%s, job_description=%s, job_qualifications=%s, job_experience=%s, job_primary_skill = %s where job_id = '{}';".format(job_id),(type,description,qualification,experience,skill))
            cur.execute("update Job_Profile_job_location set job_location=%s, job_vacancy=%s where job_id = '{}'  and job_location = '{}';".format(job_id,loc),(location,vacancy))
            conn.commit()
            cur.close()
            return redirect("/home_rec")
        return render_template('update_jobs.html', details = old_details[0])
    else:
        return redirect(url_for('login'))
    
    return render_template('update_jobs.html')    

    
@app.route('/rec_view_app', endpoint='recruiter_app', methods=['POST','GET'])
def recruiter_app():
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        cur.execute("SELECT * FROM Recruiter WHERE login_username = '{}'".format(user))
        userdet = cur.fetchall()
        name = userdet[0][1]
        cur.execute("select j.job_id, job_name, application_date, Cand_name from Candidate as c, Applications as a, Recruiter as r, Job_Profile as j where r.login_username = '{}' and r.emp_id = j.recruiter_ID and j.job_id=a.application_job_id and a.application_cand_id = c.Cand_id;".format(user))
        apps = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return render_template('recruiter_app.html', apps = apps,name = name)
    else:
        return redirect(url_for('login'))
    
@app.route('/rec_view_cand', endpoint='recruiter_cand', methods=['POST','GET'])
def recruiter_cand():
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        cur.execute("SELECT * FROM Recruiter WHERE login_username = '{}'".format(user))
        userdet = cur.fetchall()
        name = request.form['candname']
        print(name)
        cur.execute("select Cand_name, Cand_email,Cand_address, Cand_phone , Cand_DOB, Cand_gender, resume_qualification, resume_experience,resume_id from Resume as r, Candidate as c where r.Candidate_id = c.cand_id and c.Cand_name = '{}';".format(name))
        candidate = cur.fetchone()
        print(candidate)
        rid = candidate[8]
        print(rid)
        cur.execute("select resume_skills from Resume_resume_skills as r where r.resume_id = '{}';".format(rid))
        skills = cur.fetchall()
        
        conn.commit()
        cur.close()
        conn.close()
        return render_template('Recruiter_candidate.html', candidate=candidate, skills = skills)
    else:
        return redirect(url_for('login'))

@app.route('/postjob', endpoint = 'postjob', methods = ['GET', 'POST'])
def postjob():
    if "user" in session:
        if request.method == 'POST':
            user = session["user"]
            conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
            cur=conn.cursor()
            
            userDetails = request.form
            name = userDetails['name']
            type = userDetails['type']
            qualification = userDetails['qualification']
            experience = userDetails['experience']
            primaryskill = userDetails['primaryskill']
            location = userDetails['location']
            vacancy = userDetails['vacancy']
            description = userDetails['description']
            # checking if the password entered in both the fields are same
            conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
            cur=conn.cursor()
            # creating a record by inserting the jobseeker details in jobseeker entity
            cur.execute("select nextval('job_seq')")
            job_id = cur.fetchone()
            cur.execute("select emp_id from Recruiter where login_username = '{}'".format(user))
            recruiter_ID = cur.fetchone()
            
            cur.execute("INSERT INTO Job_Profile_job_location(job_id, job_location, job_vacancy) VALUES (%s, %s, %s)",(job_id, location, vacancy))
            cur.execute("INSERT INTO Job_Profile(job_id,job_name, job_type, job_description,recruiter_ID, job_qualifications, job_experience, job_primary_skills) VALUES (%s, %s, %s, %s, %s,%s,%s,%s)",(job_id, name, type, description, recruiter_ID, qualification, experience, primaryskill))
            conn.commit()
            cur.close()
            return redirect('postjob.html')
        else:
            return render_template('postjob.html')
    else:
        return render_template('login.html')

@app.route('/postinterview', endpoint = 'postinterview', methods = ['GET', 'POST'])
def postinterview():
    if "user" in session:
        if request.method == 'POST':
            user = session["user"]
            conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
            cur=conn.cursor()
            
            userDetails = request.form
            jobid = userDetails['jobid']
            type = userDetails['type']
            date = userDetails['date']
            results = "pending"
            remarks = "pending"
            candid = userDetails['candid']
            # checking if the password entered in both the fields are same
            conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
            cur=conn.cursor()
            # creating a record by inserting the jobseeker details in jobseeker entity
            cur.execute("select nextval('interview_seq')")
            int_id = cur.fetchone()
            
            cur.execute("INSERT INTO Interview(int_id,int_job,int_date, int_result, int_remarks, int_type, candidate_ID) VALUES (%s, %s, %s, %s, %s,%s,%s)",(int_id, jobid,date, results, remarks, type, candid))
            conn.commit()
            cur.close()
            return redirect('postinterview.html')
        else:
            return render_template('postinterview.html')
    else:
        return render_template('login.html')

@app.route('/apply',endpoint='applyjob', methods=['GET','POST'])
def applyjob():
    if "user" in session:
        print('here10')
        user = session["user"]
        if request.method=='POST':
            applied=request.form
            apjob=applied['jobid']
            apjob=int(apjob)
            conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
            cur=conn.cursor()
            cur.execute('select application_id from applications;')
            ids=cur.fetchall()
            new_id=int(ids[-1][0])+1
            exist_appl='''select application_job_id 
            from applications as a, candidate as c, login as l 
            where a.application_cand_id=c.cand_id and c.cand_login_username=l.login_username and l.login_username='{}';'''
            cur.execute(exist_appl.format(user))
            existing=cur.fetchall()
            l=list()
            for i in existing:
                for j in i:
                    l.append(j)
            if apjob in l:
                flash('Looks like you have already applied!')
            else:
                cur.execute("select cand_id from candidate as c, login as l where c.cand_login_username=l.login_username and l.login_username='{}';".format(user))
                candid=cur.fetchone()
                insertappl='''insert into applications(application_id, application_job_id,application_date, application_cand_id) values (%s,%s,%s,%s);'''
                cur.execute(insertappl,(new_id, apjob, date.today(), candid))
                conn.commit()
                cur.close()
                conn.close()
    return redirect('/jia_cand')

@app.route('/resume_edit', endpoint='edit_resume', methods=["GET","POST"])
def edit_resume():
    id=0
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        edit_res='''select resume_name, resume_qualification, resume_experience, r.resume_id
        from resume as r, candidate as c, login as l
        where r.candidate_id=c.cand_id and c.cand_login_username=l.login_username and l.login_username='{}';'''
        cur.execute(edit_res.format(user))
        old_det=cur.fetchone()
        id=old_det[3]
        cur.execute("select resume_skills from Resume_resume_skills as s, resume as r where s.resume_id=r.resume_id and r.resume_id=%s;",(id,))
        skill_old=cur.fetchall()
        l=list()
        stringsk=''
        for i in skill_old:
            for j in i:
                l.append(j)
                stringsk=stringsk+j+','

    if request.method=="POST":
        resume=request.form
        name=resume["name"]
        qualf = resume["qualf"]
        expr = resume["expr"]
        skills = resume["skills"]
        skills=skills.split(',')
        print('skills',skills)
        
        for i in skills:
            if i not in l:
                print('skill: ', i)
                cur.execute("insert into resume_resume_skills(resume_id, resume_skills) values (%s,%s);",(id, i))

        old_sk=set(l)
        new_sk=set(skills)
        removedsk=old_sk-new_sk
        for i in removedsk:
            cur.execute("delete from resume_resume_skills where resume_skills=%s and resume_id=%s;",(i,id))

        cur.execute("update resume set resume_name=%s, resume_qualification=%s, resume_experience=%s where resume_id=%s;",(name, qualf, expr, id))
        conn.commit()
        cur.close()
        return redirect('/home_cand')

    return render_template('resume_edit.html', resume=old_det, oldsk=stringsk)

@app.route('/profile_cand', endpoint='profile_cand', methods=["GET","POST"])
def profile_cand():
    id=0
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        cur.execute("select cand_name, cand_email, cand_address, cand_phone, cand_id from Candidate as c, Login as l where c.cand_login_username=l.login_username and l.login_username='{}';".format(user))
        old_details=cur.fetchone()
        print(old_details)
        id=old_details[4]

    if request.method == 'POST':
        profile=request.form
        name=profile["name"]
        email=profile["email"]
        address=profile["address"]
        phoneno=profile["phoneno"]
        
        cur.execute("update Candidate set cand_email=%s, cand_name=%s, cand_address=%s, cand_phone=%s where cand_id=%s;",(email, name, address,phoneno,id))
        conn.commit()
        cur.close()
        return redirect('/home_cand')
    return render_template('profile_edit_cand.html', profile=old_details)
#commented to add endpoint to all functions


@app.route('/profile_rec',endpoint='profile_rec', methods=["GET","POST"])
def profile_rec():
    id=0
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        cur.execute("select emp_id, emp_name, emp_HQ, emp_phone, emp_email from Recruiter as r, Login as l where r.login_username=l.login_username and l.login_username='{}';".format(user))
        old_details=cur.fetchone()
        id=old_details[0]

    if request.method == 'POST':
        profile=request.form
        name=profile["name"]
        email=profile["email"]
        address=profile["address"]
        phoneno=profile["phoneno"]
        
        cur.execute("update Recruiter set emp_email=%s, emp_name=%s, emp_HQ=%s, emp_phone=%s where emp_id=%s;",(email, name, address,phoneno,id))
        conn.commit()
        cur.close()
        return redirect('/home_rec')
    return render_template('profile_edit_rec.html', profile_data=old_details)

int_id = 0

@app.route('/view_int', endpoint='view_int', methods=['POST','GET'])
def view_int():
    global int_id
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        cur.execute("SELECT * FROM Recruiter WHERE login_username = '{}'".format(user))
        userdet = cur.fetchall()
        name = userdet[0][1]
        cur.execute("select int_id,int_job,j.job_name,i.CandidateID, c.Cand_name, int_type ,int_date, int_result, int_remarks from Interview as i, Job_Profile as j, Candidate as c, Recruiter as r where  r.login_username = '{}' and c.cand_id = i.CandidateID and r.emp_id = j.recruiter_ID and j.job_id=i.int_job;".format(user))
        old_details = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        if request.method == 'POST':
            int_id = request.form.get('j_id')
            return redirect(url_for('update_int', int_id = int_id))  
        
        return render_template('viewinterviews.html', interviews= old_details,name = name)
          
    else:
        return redirect(url_for('login'))
    
    
@app.route('/update_int', endpoint='update_int', methods=['POST','GET'])
def update_int():
    if "user" in session:
        user = session["user"]
        conn=psycopg2.connect(database='jobportal', user='postgres', password='P@rimala9', port=5432, host='127.0.0.1')
        cur=conn.cursor()
        cur.execute("SELECT * FROM Recruiter WHERE login_username = '{}'".format(user))
        userdet = cur.fetchall()
        name = userdet[0][1]
        cur.execute("select int_id,int_job,j.job_name,i.CandidateID, c.Cand_name, int_type ,int_date, int_result, int_remarks from Interview as i, Job_Profile as j, Candidate as c, Recruiter as r where  r.login_username = '{}' and c.cand_id = i.CandidateID and r.emp_id = j.recruiter_ID and j.job_id=i.int_job and i.int_id = '{}';".format(user,int_id))
        old_details = cur.fetchall()
        print(old_details)
        
        if request.method == 'POST':
            profile=request.form
            print(profile)
            date = profile["date"]
            type = profile["type"]
            remarks=profile["remarks"]
            result=profile["results"]
            cur.execute("update Interview set int_date=%s, int_type=%s, int_remarks=%s, int_result=%s where int_id=%s;",(date,type,remarks,result,int_id))
            conn.commit()
            cur.close()
            return redirect("/home_rec")
        return render_template('update_results.html', details = old_details[0])
    else:
        return redirect(url_for('login'))
    
    return render_template('update_results.html')
    
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)

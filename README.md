# CareerForge

CareerForge is a Flask prototype for student career preparation and recruiter-assisted screening. Students can save a profile, compare skills against job postings, download tailored resumes, apply for roles, and practice interviews. Recruiters can publish jobs, review applicants, and decide whom to shortlist.

## Run locally on Windows

Install Git and Python 3.11. In the VS Code PowerShell terminal, clone the demo branch if you are setting up the project for the first time.

```powershell
git clone --branch codex/career-platform-foundation https://github.com/ayaan-23/CareerForge.git
cd CareerForge
```

If you already have this branch checked out, open the existing `CareerForge` folder and run `git pull --ff-only`.

Run these commands in the project folder. Let the package installation finish before starting the app.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:SECRET_KEY = [guid]::NewGuid().ToString()
.\.venv\Scripts\python.exe app.py
```

If you already created the virtual environment and installed the dependencies, run only the last two commands. First startup can take longer while the resume analyzer downloads its model. Once the server is running, open [CareerForge](http://127.0.0.1:5000) and choose **Student and recruiter workspace**.

## Demo walkthrough

Use two browser sessions with different email addresses so you can switch between the student and recruiter without signing out. Open the second session in an incognito window.

| Step | Role | Expected result |
| --- | --- | --- |
| Publish a sample job | Recruiter | A **Junior Software Engineer** posting requiring `Python, SQL` appears on the recruiter dashboard. |
| Save a profile with Python as the only skill | Student | The job shows **50% skill match**, with Python matched and SQL missing. |
| Download the tailored resume | Student | The Word file shows the target role, lists Python under **Relevant skills**, and includes the saved education. |
| Apply | Student | The job shows **Submitted**. |
| Open **Review applicants** and shortlist the applicant | Recruiter | The applicant shows **Shortlisted**. Refreshing the student dashboard shows the same status. |
| Start and submit a practice interview | Student | The score and feedback appear in **Interview history**. |

The skill score is the percentage of explicitly listed required skills that match the student’s profile. Review education and other qualifications separately. Interview feedback comes from the built-in scoring rules.

The **Interview Ready** badge is awarded after answering every question and averaging at least 75/100. A student who earns it for a job they applied to can optionally share it with that job’s recruiter. Practice answers and feedback stay private.

## Local data

The app stores accounts, profiles, jobs, applications, and practice history in `instance/career.sqlite3`. Restarting the server preserves this data. Use sample profiles and job postings for the demo.

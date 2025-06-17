from flask import Flask, render_template, request
from utils import (
    parse_resume,
    match_resume_with_jd,
    predict_salary,
    analyze_linkedin_profile,
    generate_dashboard,
    generate_badge,
    generate_ai_recommendations
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['POST'])
def dashboard():
    resume = request.files['resume']
    jd_text = request.form.get('job_description')
    linkedin_url = request.form.get('linkedin')

    parsed = parse_resume(resume)
    match = match_resume_with_jd(parsed, jd_text)
    salary = predict_salary(parsed)
    linkedin = analyze_linkedin_profile(linkedin_url)
    dashboard_data = generate_dashboard(parsed, jd_text)

    # 🏅 Badge logic based on match percentage
    badge = generate_badge(match['match_percent'])

    # 🔥 AI Recommendations based on missing skills
    recommendations = generate_ai_recommendations(dashboard_data['skills_missing'])

    return render_template(
        'dashboard.html',
        parsed=parsed,
        match=match,
        salary=salary,
        linkedin=linkedin,
        dashboard=dashboard_data,
        badge=badge,
        recommendations=recommendations
    )


# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))

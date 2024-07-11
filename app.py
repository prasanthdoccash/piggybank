from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure the PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://prasanth6:Qoz7mjjkVsiGWZ8qviximXME3aBVRGBf@dpg-cq7l85jv2p9s73c675n0-a/piggy_breu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the TaskPoints model
class TaskPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    wake_up_early = db.Column(db.Float, nullable=False, default=0)
    breakfast = db.Column(db.Float, nullable=False, default=0)
    afternoon_sleeping = db.Column(db.Float, nullable=False, default=0)
    study_everyday = db.Column(db.Float, nullable=False, default=0)
    proper_dinner = db.Column(db.Float, nullable=False, default=0)
    sleeping_on_time = db.Column(db.Float, nullable=False, default=0)
    screen_time = db.Column(db.Float, nullable=False, default=0)
    healthy_food = db.Column(db.Float, nullable=False, default=0)
    unhealthy_food = db.Column(db.Float, nullable=False, default=0)
    redeemed = db.Column(db.Float, nullable=False, default=0)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    children = ['Nainika', 'Dyansh']
    return render_template('index.html', children=children)

@app.route('/task_input/<child>', methods=['GET', 'POST'])
def task_input(child):
    if request.method == 'POST':
        date = datetime.utcnow().date()
        wake_up_early = float(request.form['wake_up_early'])
        breakfast = float(request.form['breakfast'])
        afternoon_sleeping = float(request.form['afternoon_sleeping'])
        study_everyday = float(request.form['study_everyday'])
        proper_dinner = float(request.form['proper_dinner'])
        sleeping_on_time = float(request.form['sleeping_on_time'])
        screen_time = float(request.form['screen_time'])
        healthy_food = float(request.form['healthy_food'])
        unhealthy_food = float(request.form['unhealthy_food'])

        task_points = TaskPoints(
            date=date,
            wake_up_early=wake_up_early,
            breakfast=breakfast,
            afternoon_sleeping=afternoon_sleeping,
            study_everyday=study_everyday,
            proper_dinner=proper_dinner,
            sleeping_on_time=sleeping_on_time,
            screen_time=screen_time,
            healthy_food=healthy_food,
            unhealthy_food=unhealthy_food,
            redeemed=0
        )
        db.session.add(task_points)
        db.session.commit()
        return redirect(url_for('points_display', child=child))

    return render_template('task_input.html', child=child)

@app.route('/points_display/<child>', methods=['GET', 'POST'])
def points_display(child):
    total_earned = db.session.query(
        db.func.sum(TaskPoints.wake_up_early) +
        db.func.sum(TaskPoints.breakfast) +
        db.func.sum(TaskPoints.afternoon_sleeping) +
        db.func.sum(TaskPoints.study_everyday) +
        db.func.sum(TaskPoints.proper_dinner) +
        db.func.sum(TaskPoints.sleeping_on_time) +
        db.func.sum(TaskPoints.screen_time) +
        db.func.sum(TaskPoints.healthy_food) +
        db.func.sum(TaskPoints.unhealthy_food) -
        db.func.sum(TaskPoints.redeemed)
    ).scalar() or 0

    if request.method == 'POST':
        redeem_points = float(request.form['redeem_points'])
        if redeem_points <= total_earned:
            latest_entry = TaskPoints.query.order_by(TaskPoints.date.desc()).first()
            if latest_entry:
                latest_entry.redeemed += redeem_points
                db.session.commit()
                total_earned -= redeem_points
        return redirect(url_for('points_display', child=child))

    points_summary = TaskPoints.query.all()
    return render_template('points_display.html', points_summary=points_summary, child=child, total_earned=total_earned)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

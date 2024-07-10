import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)

# Ensure tasks.csv exists
tasks_file = 'tasks.csv'
if not os.path.exists(tasks_file):
    tasks_df = pd.DataFrame(columns=['task'])
    tasks_df.to_csv(tasks_file, index=False)
else:
    tasks_df = pd.read_csv(tasks_file)

# Initialize children's points files if they don't exist
children = ['Nainika', 'Dyansh']
for child in children:
    points_file = f'{child}_points.csv'
    if not os.path.exists(points_file):
        pd.DataFrame(columns=['Date'] + list(tasks_df['task']) + ['Redeemed']).to_csv(points_file, index=False)

@app.route('/')
def index():
    return render_template('index.html', children=children)

@app.route('/task_input/<child>', methods=['GET', 'POST'])
def task_input(child):
    points_file = f'{child}_points.csv'
    
    # Check if the points file exists
    if not os.path.exists(points_file):
        return render_template('error.html', error_message=f'{child} points data is missing.')

    if request.method == 'POST':
        date = datetime.now().strftime('%d/%m/%Y')
        points = request.form.getlist('points')
        new_data = {task: float(point) if point else 0 for task, point in zip(tasks_df['task'], points)}
        new_data['Date'] = date
        new_data['Redeemed'] = 0
        new_data_df = pd.DataFrame(new_data, index=[0])
        
        try:
            # Read the entire CSV file including headers
            points_df = pd.read_csv(points_file)
        except pd.errors.EmptyDataError:
            points_df = pd.DataFrame(columns=['Date'] + list(tasks_df['task']) + ['Redeemed'])
        
        points_df = pd.concat([points_df, new_data_df], ignore_index=True)
        points_df.to_csv(points_file, index=False)
        return redirect(url_for('points_display', child=child))
    
    return render_template('task_input.html', tasks=tasks_df['task'], child=child)

@app.route('/points_display/<child>', methods=['GET', 'POST'])
def points_display(child):
    points_file = f'{child}_points.csv'

    # Check if the points file exists
    if not os.path.exists(points_file):
        return render_template('error.html', error_message=f'{child} points data is missing.')

    try:
        # Read the entire CSV file including headers
        points_df = pd.read_csv(points_file)
        
        # Convert columns to numeric types
        numeric_cols = ['wake up early (5)','Breakfast (5)','Afternoon sleeping (2)','Study everyday (3)','Proper dinner (2)',
'Sleeping on time (3)',
'screen time (10)',
'Healthy food (x)',
'Unhealthy food (x)', 'Redeemed']
        for col in numeric_cols:
            points_df[col] = pd.to_numeric(points_df[col], errors='coerce').fillna(0)

        if request.method == 'POST':
            redeem_points = float(request.form['redeem_points'])
            
            # Recalculate total earned before redemption
            total_earned_before = points_df.drop(columns=['Date', 'Redeemed']).sum().sum()
            print(total_earned_before)
            if redeem_points <= total_earned_before:
                # Update the last row with redeemed points
                points_df.loc[points_df.index[-1], 'Redeemed'] += redeem_points
                points_df.to_csv(points_file, index=False)
                
                # Recalculate total earned after redemption
                total_earned_after = total_earned_before - redeem_points
                print(total_earned_after)
                # Assign the updated total earned
                total_earned = total_earned_after
            else:
                redeem_points = total_earned_before
                points_df.loc[points_df.index[-1], 'Redeemed'] += redeem_points
                points_df.to_csv(points_file, index=False)
                total_earned = 0  # Set total earned to zero after full redemption

        else:
            # Initial calculation of total earned when no redemption occurs
            total_earned = points_df.drop(columns=['Date', 'Redeemed']).sum().sum()

        points_summary = points_df.groupby('Date').sum().reset_index()

        # Convert to list for Jinja2 template rendering
        points_summary_list = points_summary.values.tolist()

        return render_template('points_display.html', points_summary=points_summary_list, child=child, total_earned=total_earned)

    except pd.errors.EmptyDataError:
        return render_template('error.html', error_message=f'{child} points data is empty or cannot be parsed.')

if __name__ == '__main__':
    app.run(debug=True)

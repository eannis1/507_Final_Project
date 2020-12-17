from flask import Flask, render_template, request
import sqlite3
import plotly.graph_objects as go

app = Flask(__name__)

def get_results_pt(sort_by):
    conn = sqlite3.connect('gillray_prints.sqlite')
    cur = conn.cursor()

    if sort_by == 'Techniques':
        column = 'Technique'
        table = 'Techniques'
    elif sort_by == 'Printsellers':
        column = 'Name'
        table = 'Printsellers'

    query = f'''
        SELECT {column}, Website
        FROM {table}
    '''
    results = cur.execute(query).fetchall()
    conn.close()
    return results

def get_results_print(sort_by):
    conn = sqlite3.connect('gillray_prints.sqlite')
    cur = conn.cursor()

    query = f'''
        SELECT pt.Title, pt.Date, t.Technique Technique, p.Name Printseller, pt.Description, pt.Website
        FROM Prints pt
        JOIN Techniques t
        ON t.Id = pt.TechniqueId
        JOIN Printsellers p
        ON p.Id = pt.PrintsellerId
    '''
    results = cur.execute(query).fetchall()
    conn.close()
    return results

def get_plot_techniques(sort_by):
    conn = sqlite3.connect('gillray_prints.sqlite')
    cur = conn.cursor()

    query = f'''
        SELECT Technique
        FROM Techniques
            JOIN Prints
                on Techniques.Id=TechniqueId
    '''
    results = cur.execute(query).fetchall()
    unique_results = []
    for item in results:
        if item not in unique_results:
            unique_results.append(item)
    item_counts = []
    for item in unique_results:
        item_count = results.count(item)
        item_counts.append(item_count)
    conn.close()
    return unique_results, item_counts

def get_plot_printsellers(sort_by):
    conn = sqlite3.connect('gillray_prints.sqlite')
    cur = conn.cursor()

    query = f'''
        SELECT Name
        FROM Printsellers
            JOIN Prints
                on Printsellers.Id=PrintsellerId
    '''
    results = cur.execute(query).fetchall()
    unique_results = []
    for item in results:
        if item not in unique_results:
            unique_results.append(item)
    item_counts = []
    for item in unique_results:
        item_count = results.count(item)
        item_counts.append(item_count)
    conn.close()
    return unique_results, item_counts

def get_plot_dates(sort_by):
    conn = sqlite3.connect('gillray_prints.sqlite')
    cur = conn.cursor()

    query = f'''
        SELECT Date
        FROM Prints
    '''
    results = cur.execute(query).fetchall()
    unique_results = []
    for item in results:
        if item not in unique_results:
            unique_results.append(item)
    item_counts = []
    for item in unique_results:
        item_count = results.count(item)
        item_counts.append(item_count)
    conn.close()
    return unique_results, item_counts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about') #see flaskapp2.py
def about():
    course = 'SI 507'
    semester = 'Fall 2020'
    f_name = 'Erin'
    l_name = 'Annis'
    return render_template('about.html',
        first_name=f_name,
        last_name=l_name,
        course=course,
        semester=semester)

@app.route('/views')
def views():
    return render_template('views.html')

@app.route('/results', methods=['POST'])
def results():
    sort_by = request.form['sort'] # From views.html
    if sort_by == "Techniques":
        results = get_results_pt(sort_by)
        return render_template('results.html', sort=sort_by, results=results)
    elif sort_by == "Printsellers":
        results = get_results_pt(sort_by)
        return render_template('results.html', sort=sort_by, results=results)
    else:
        results = get_results_print(sort_by)
        return render_template('results_print.html', sort=sort_by, results=results)

@app.route('/plot')
def plot():
    return render_template('plot.html')

@app.route('/plot_results', methods=['POST'])
def plot_results():
    sort_by = request.form['plot_sort'] # from plot.html
    if sort_by == "Prints per Technique":
        x_vals, y_vals = get_plot_techniques(sort_by)
        bars_data = go.Bar(
            x=x_vals,
            y=y_vals
        )
        fig = go.Figure(data=bars_data)
        div = fig.to_html(full_html=False)
    elif sort_by == "Prints per Printseller":
        x_vals, y_vals = get_plot_printsellers(sort_by)
        bars_data = go.Bar(
            x=x_vals,
            y=y_vals
        )
        fig = go.Figure(data=bars_data)
        div = fig.to_html(full_html=False)
    elif sort_by == "Prints per Date":
        #markers={'symbol':'circle', 'size':20, 'color': 'black'},
        x_vals, y_vals = get_plot_dates(sort_by)
        scatter_data = go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='markers+text'
        )
        fig = go.Figure(data=scatter_data)
        div = fig.to_html(full_html=False)
    
    return render_template("plot_results.html", plot_div=div)

if __name__ == '__main__':
    app.run(debug=True)
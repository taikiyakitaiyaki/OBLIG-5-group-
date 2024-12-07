from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import altair as alt
from data import barnehager_info
from models import db, Application
from forms import ApplicationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applications.db'
app.secret_key = 'supersecretkey'  # Nødvendig for CSRF-beskyttelse
db.init_app(app)

def reset_kindergarten_lists():
    # Tilbakestill barnehagelistene til deres opprinnelige antall ledige plasser
    for barnehage in barnehager_info:
        barnehage['ledige_plasser'] = barnehage['opprinnelige_ledige_plasser']

@app.route('/init_db')
def init_db():
    db.create_all()
    return "Database initialized!"

@app.route('/', methods=['GET', 'POST'])
def new_home():
    return render_template('new_home.html')

@app.route('/old_home', methods=['GET', 'POST'])
def index():
    form = ApplicationForm()
    if form.validate_on_submit():
        print("Skjemaet er validert")
        
        # Hent data fra skjemaet
        email = form.email.data
        parent1_name = form.parent1_name.data
        parent2_name = form.parent2_name.data
        parent1_address = form.parent1_address.data
        parent2_address = form.parent2_address.data
        parent1_phone = form.parent1_phone.data
        parent2_phone = form.parent2_phone.data
        parent1_id = form.parent1_id.data
        parent2_id = form.parent2_id.data
        child1_id = form.child1_id.data
        child1_age = form.child1_age.data
        child2_id = form.child2_id.data
        child2_age = form.child2_age.data
        priority = form.priority.data
        kindergarten_list = form.kindergarten_list.data
        start_date = form.start_date.data
        siblings = 'Ja' if form.siblings.data else 'Nei'
        income = form.income.data
        
        # Ny kode inn
        kindergarten_choice_1 = form.kindergarten_choice_1.data
        kindergarten_choice_2 = form.kindergarten_choice_2.data
        kindergarten_choice_3 = form.kindergarten_choice_3.data
        
        # Sjekk om noen av valgene er None og erstatt med tom streng hvis nødvendig
        kindergarten_choices = [kindergarten_choice_1, kindergarten_choice_2, kindergarten_choice_3]
        kindergarten_choices = [choice if choice is not None else '' for choice in kindergarten_choices]
        
        # Sjekk om barnet er for gammelt
        if child1_age is not None and child1_age > 6 or (child2_age is not None and child2_age > 6):
            response_message = 'AVSLAG: Beklager, barnet er for gammelt for barnehageplass.'
            status = 'AVSLAG'
        else:
            # Sjekk ledige plasser i valgt barnehage med prioritet
            valgt_barnehage = None
            if priority:
                for choice in kindergarten_choices:
                    if choice:
                        barnehage = next((b for b in barnehager_info if b['navn'] == choice and b.get('ledige_plasser', 0) > 0), None)
                        if barnehage:
                            valgt_barnehage = barnehage
                            break
            
            # Hvis ingen barnehage ble funnet med prioritet, sjekk uten prioritet
            if not valgt_barnehage:
                for choice in kindergarten_choices:
                    if choice:
                        barnehage = next((b for b in barnehager_info if b['navn'] == choice and b.get('ledige_plasser', 0) > 0), None)
                        if barnehage:
                            valgt_barnehage = barnehage
                            break
            
            if valgt_barnehage:
                response_message = f'TILBUD: Takk for din søknad! Vi har funnet en ledig plass i {valgt_barnehage["navn"]}. Vi vil kontakte deg på {email} med et tilbud om barnehageplass.'
                status = 'TILBUD'
                valgt_barnehage['ledige_plasser'] -= 1
            else:
                response_message = 'AVSLAG: Beklager, det er ingen ledige plasser i de valgte barnehagene.'
                status = 'AVSLAG'
        
        # Lagre søknaden i databasen
        new_application = Application(
            email=email,
            parent1_name=parent1_name,
            parent2_name=parent2_name,
            parent1_address=parent1_address,
            parent2_address=parent2_address,
            parent1_phone=parent1_phone,
            parent2_phone=parent2_phone,
            parent1_id=parent1_id,
            parent2_id=parent2_id,
            child1_id=child1_id,
            child1_age=child1_age,
            child2_id=child2_id,
            child2_age=child2_age,
            priority=priority,
            kindergarten_list=', '.join(kindergarten_choices),
            start_date=start_date,
            siblings=siblings,
            income=income,
            status=status
        )
        db.session.add(new_application)
        db.session.commit()
        
        # Lagre dataen i en Excel-fil
        excel_path = r"C:\Users\mytri\Desktop\DELT OPP\applications.xlsx"
        try:
            df = pd.read_excel(excel_path)
        except FileNotFoundError:
            df = pd.DataFrame(columns=[
                'email', 'parent1_name', 'parent2_name', 'parent1_address', 'parent2_address',
                'parent1_phone', 'parent2_phone', 'parent1_id', 'parent2_id', 'child1_id',
                'child1_age', 'child2_id', 'child2_age', 'priority', 'kindergarten_list',
                'start_date', 'siblings', 'income', 'status'
            ])
        new_row = pd.DataFrame([{
            'email': email,
            'parent1_name': parent1_name,
            'parent2_name': parent2_name,
            'parent1_address': parent1_address,
            'parent2_address': parent2_address,
            'parent1_phone': parent1_phone,
            'parent2_phone': parent2_phone,
            'parent1_id': parent1_id,
            'parent2_id': parent2_id,
            'child1_id': child1_id,
            'child1_age': child1_age,
            'child2_id': child2_id,
            'child2_age': child2_age,
            'priority': priority,
            'kindergarten_list': ', '.join(kindergarten_choices),
            'start_date': start_date,
            'siblings': siblings,
            'income': income,
            'status': status
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(excel_path, index=False)
        
        print(f"Response message: {response_message}")
        return redirect(url_for('response', message=response_message))
    else:
        print("Skjemaet ble ikke validert")
        print(form.errors)
    
    return render_template('index.html', form=form)

@app.route('/response')
def response():
    message = request.args.get('message', '')
    print(f"Response message in route: {message}")
    return render_template('response.html', message=message)

@app.route('/barnehager')
def barnehager():
    print(barnehager_info)  # Skriv ut listen til konsollen
    return render_template('barnehager.html', barnehager=barnehager_info)

@app.route('/applications')
def applications():
    applications = Application.query.all()
    message = request.args.get('message', '')
    return render_template('applications.html', applications=applications, message=message)

import re

@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    # Sti til Excel-filen
    excel_path = r"C:\Users\mytri\Desktop\DELT OPP\ssb-barnehager-2015-2023-alder-1-2-aar.xlsm"
    
    # Les data fra Excel-filen
    df = pd.read_excel(excel_path,
                       sheet_name="KOSandel120000",
                       header=3,
                       names=['kommune', 'y15', 'y16', 'y17', 'y18', 'y19', 'y20', 'y21', 'y22', 'y23'],
                       na_values=['.'])  # Behandle punktum som NaN
    
    # Debugging: Sjekk de første radene i 'kommune' kolonnen
    print("Original kommune data:")
    print(df['kommune'].head(10))  # Skriv ut de første 10 radene for å inspisere
    
    # Filtrer ut rader hvor kommunenummeret er ugyldig
    # Anta at en kommune skal ha et 4-sifret tall etterfulgt av kommune-navn
    def is_valid_kommune(value):
        # Sjekk om verdien starter med 4 sifre (kommunenummer) etterfulgt av et mellomrom og et navn
        return bool(re.match(r'^\d{4} .+', str(value)))

    # Filtrer ut rader som ikke er gyldige kommuner (f.eks. adresse, telefonnummer)
    df = df[df['kommune'].apply(is_valid_kommune)]
    
    # Debugging: Sjekk de første radene etter at filtreringen er gjort
    print("Kommune data etter filtering:")
    print(df['kommune'].head(10))  # Skriv ut de første 10 radene etter filtreringen

    # Konverter kolonnene for å være numeriske, og håndter eventuelle feil
    for column in ['y15', 'y16', 'y17', 'y18', 'y19', 'y20', 'y21', 'y22', 'y23']:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    
    # Long format for data
    df_long = df.melt(id_vars=['kommune'],
                      value_vars=['y15', 'y16', 'y17', 'y18', 'y19', 'y20', 'y21', 'y22', 'y23'],
                      var_name='år',
                      value_name='prosentandel')
    
    # Legg til data for Kristiansand kommune fra 2015-2019
    additional_data = pd.DataFrame({
        'kommune': ['4204 Kristiansand'] * 5,
        'år': ['y15', 'y16', 'y17', 'y18', 'y19'],
        'prosentandel': [78.0, 79.5, 79.1, 80.1, 81.6]
    })
    
    # Kombiner de to datasettene
    data = pd.concat([df_long, additional_data], ignore_index=True)
    
    # Hent alle kommuner (unike verdier fra data)
    kommuner = data['kommune'].unique().tolist()
    
    # Velg kommune fra URL (standardverdi er Kristiansand)
    valgt_kommune = request.args.get('kommune', '4204 Kristiansand')
    kommune_data = data[data['kommune'] == valgt_kommune]
    
    # Fyll inn manglende år med NaN
    all_years = ['y15', 'y16', 'y17', 'y18', 'y19', 'y20', 'y21', 'y22', 'y23']
    existing_years = kommune_data['år'].unique()
    missing_years = set(all_years) - set(existing_years)
    
    # Create a DataFrame for missing years
    missing_data = pd.DataFrame({'kommune': valgt_kommune, 
                                 'år': list(missing_years), 
                                 'prosentandel': [None] * len(missing_years)})
    
    # Append missing data to kommune_data
    kommune_data = pd.concat([kommune_data, missing_data], ignore_index=True)
    
    kommune_data['år'] = pd.Categorical(kommune_data['år'], categories=all_years, ordered=True)
    kommune_data = kommune_data.sort_values('år')
    
    # Sjekk om det finnes gyldige data
    if kommune_data['prosentandel'].notna().sum() == 0:
        chart_html = "Ingen gyldige data for valgt kommune."
    else:
        # Lag diagrammet
        chart = alt.Chart(kommune_data).mark_bar().encode(
            x=alt.X('år:N', title='År'),
            y=alt.Y('prosentandel:Q').scale(domain=[0, 100]),  # Sett y-aksen til [0, 100]
            tooltip=['kommune:N', 'år:N', 'prosentandel:Q']
        ).properties(
            title='Prosentandel av valgt kommune fra 2015-2023',
            width=800,
            height=400
        )
        
        chart_html = chart.to_html()
    
    return render_template('statistics.html', chart_html=chart_html, valgt_kommune=valgt_kommune, kommuner=kommuner)

@app.route('/commit')
def commit():
    # Sti til Excel-filen
    excel_path = r"C:\Users\mytri\Desktop\DELT OPP\applications.xlsx"
    
    # Les data fra Excel-filen
    df = pd.read_excel(excel_path)
    
    # Konverter dataene til en liste av ordbøker
    data = df.to_dict(orient='records')
    
    if not data:
        return "Ingen data funnet i Excel-filen."
    
    return render_template('commit.html', data=data)

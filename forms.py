from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Email, NumberRange, Optional
from data import barnehager_info

class ApplicationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    parent1_name = StringField('Forelder 1 Navn', validators=[DataRequired()])
    parent2_name = StringField('Forelder 2 Navn', validators=[Optional()])
    parent1_address = StringField('Forelder 1 Adresse', validators=[DataRequired()])
    parent2_address = StringField('Forelder 2 Adresse', validators=[Optional()])
    parent1_phone = StringField('Forelder 1 Telefon', validators=[DataRequired()])
    parent2_phone = StringField('Forelder 2 Telefon', validators=[Optional()])
    parent1_id = StringField('Forelder 1 ID', validators=[DataRequired()])
    parent2_id = StringField('Forelder 2 ID', validators=[Optional()])
    child1_id = StringField('Barn 1 ID', validators=[DataRequired()])
    child1_age = IntegerField('Barn 1 Alder', validators=[DataRequired()])  # Fjernet NumberRange
    child2_id = StringField('Barn 2 ID', validators=[Optional()])
    child2_age = IntegerField('Barn 2 Alder', validators=[Optional(), NumberRange(min=1, max=6)])
    priority = BooleanField('Fortrinnsrett')
    kindergarten_choice_1 = SelectField('1. Prioritert Barnehage', choices=[('', 'Velg barnehage')] + [(b['navn'], b['navn']) for b in barnehager_info])
    kindergarten_choice_2 = SelectField('2. Prioritert Barnehage', choices=[('', 'Velg barnehage')] + [(b['navn'], b['navn']) for b in barnehager_info])
    kindergarten_choice_3 = SelectField('3. Prioritert Barnehage', choices=[('', 'Velg barnehage')] + [(b['navn'], b['navn']) for b in barnehager_info])
    kindergarten_list = SelectMultipleField('Barnehager', choices=[(b['navn'], b['navn']) for b in barnehager_info], validators=[Optional()])
    start_date = DateField('Startdato', validators=[DataRequired()])
    siblings = BooleanField('Søsken')
    income = IntegerField('Inntekt', validators=[DataRequired()])

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.parent2_name.data or self.parent2_address.data or self.parent2_phone.data or self.parent2_id.data:
            if not self.parent2_name.data:
                self.parent2_name.errors.append('Navn på foresatt 2 må fylles ut hvis noen av de andre feltene for foresatt 2 er fylt ut.')
                return False
            if not self.parent2_address.data:
                self.parent2_address.errors.append('Adresse for foresatt 2 må fylles ut hvis noen av de andre feltene for foresatt 2 er fylt ut.')
                return False
            if not self.parent2_phone.data:
                self.parent2_phone.errors.append('Telefonnummer for foresatt 2 må fylles ut hvis noen av de andre feltene for foresatt 2 er fylt ut.')
                return False
            if not self.parent2_id.data:
                self.parent2_id.errors.append('ID for foresatt 2 må fylles ut hvis noen av de andre feltene for foresatt 2 er fylt ut.')
                return False
        return True

    def validate_on_submit(self):
        return self.is_submitted() and self.validate()
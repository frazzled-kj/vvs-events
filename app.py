from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, logout_user
import random

app = Flask(__name__)  
app.config['SECRET_KEY'] = '5791_vvs_events'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vvs_events.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Admins(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return Admins.query.get(int(user_id))

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    is_ongoing = db.Column(db.Boolean, default=True)
    adj_form_created = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=False)
    rules = db.Column(db.Text, nullable=False)
    adj_form_fields = db.Column(db.Text, nullable=True)


    def __str__(self):
        return self.name

class EventView(ModelView):
    form_columns = ['name', 'is_umbrella_event', 'description', 'rules']


class Adjudicators(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    event = db.relationship('Events', backref=db.backref('adjudicators', lazy=True))

class AdjudicatorView(ModelView):
    form_columns = ['event', 'name', 'email']


class Participants(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    institute = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    team = db.Column(db.String(100), nullable=True)
    event = db.relationship('Events', backref=db.backref('participants', lazy=True))

    def __str__(self):
        return self.name
class ParticipantView(ModelView):
    form_columns = ['name', 'event', 'institute']


class Venues(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    event = db.relationship('Events', backref=db.backref('venues', lazy=True))

class VenueView(ModelView):
    form_columns = ['event', 'name']


class Rounds(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    event = db.relationship('Events', backref=db.backref('rounds', lazy=True))
    is_released = db.Column(db.Boolean, default=False)
    adj_form_released = db.Column(db.Boolean, default=False)

    def __str__(self):
        return (self.name)
    
class RoundView(ModelView):
    form_columns = ['event', 'name']


class AdjForm(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    event = db.relationship('Events', backref=db.backref('adjform', lazy=True))
    round = db.relationship('Rounds', backref=db.backref('adjform', lazy=True))
    is_created = db.Column(db.Boolean, default=False)


class Draws(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    team1 = db.Column(db.String(100), nullable=False)
    role1 = db.Column(db.String(100), nullable=False)
    team2 = db.Column(db.String(100), nullable=True)
    role2 = db.Column(db.String(100), nullable=True)
    venue = db.Column(db.String(100), nullable=False)
    adjudicators = db.Column(db.String(300), nullable=False)
    motion_s = db.Column(db.String(100), nullable=True)
    event = db.relationship('Events', backref=db.backref('draws', lazy=True))
    round = db.relationship('Rounds', backref=db.backref('draws', lazy=True))
    is_released = db.Column(db.Boolean, default=False)

class DrawView(ModelView):
    form_columns = ['event', 'round', 'team1', 'role1', 'team2', 'role2', 'motion_s', 'venue', 'adjudicators']


class Motions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    motion = db.Column(db.Text, nullable=False)
    motion_s = db.Column(db.String(100), nullable=True)
    info_slide = db.Column(db.Text, nullable=True)
    event = db.relationship('Events', backref=db.backref('motions', lazy=True))
    round = db.relationship('Rounds', backref=db.backref('motions', lazy=True))
    is_released = db.Column(db.Boolean, default=False)

class MotionView(ModelView):
    form_columns = ['event', 'round', 'motion', 'motion_s', 'info_slide']


class TeamScores(db.Model):
    adj_form_id = db.Column(db.String(20), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    is_winning_team = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, nullable=False)
    event = db.relationship('Events', backref=db.backref('team_scores', lazy=True))
    round = db.relationship('Rounds', backref=db.backref('team_scores', lazy=True))
    result_released = db.Column(db.Boolean, default=False)
    leaderboard_released = db.Column(db.Boolean, default=False)


class TeamScoreView(ModelView):
    form_columns = ['event', 'round', 'team', 'is_winning_team', 'score']


class IndividualScores(db.Model):
    adj_form_id = db.Column(db.String(20), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    institute = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    score = db.Column(db.Integer, nullable=False)
    event = db.relationship('Events', backref=db.backref('individual_scores', lazy=True))
    round = db.relationship('Rounds', backref=db.backref('individual_scores', lazy=True))
    result_released = db.Column(db.Boolean, default=False)
    leaderboard_released = db.Column(db.Boolean, default=False)

class IndividualScoreView(ModelView):
    form_columns = ['event', 'round', 'name', 'institute', 'role', 'score']

class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        events = Events.query.all()
        rounds = Rounds.query.all()
        adj_forms = AdjForm.query.all()
        return self.render('admin/index.html', events=events, rounds=rounds, adj_forms = adj_forms)
    
    
with app.app_context():
    admin = Admin(app, name = 'VVS Events', template_mode='bootstrap4', index_view=IndexView(endpoint='/admin'))

admin.add_view(EventView(Events, db.session))
admin.add_view(AdjudicatorView(Adjudicators, db.session))
admin.add_view(ParticipantView(Participants, db.session))
admin.add_view(VenueView(Venues, db.session))
admin.add_view(RoundView(Rounds, db.session))
admin.add_view(MotionView(Motions, db.session))
admin.add_view(DrawView(Draws, db.session))
admin.add_view(TeamScoreView(TeamScores, db.session))
admin.add_view(IndividualScoreView(IndividualScores, db.session))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def home():
    events = Events.query.all()
    return render_template('index.html', events=events)

@app.route('/admin/create_adj_form', methods=['POST'])
def create_adj_form():
    event_name = request.form['event_name']
    event = Events.query.filter_by(name=event_name).first()
    if event.adj_form_created != True:
            return render_template('create_adj_form.html')
    else:
            return render_template('created_adj_form.html')
    print(fields)
    db.session.commit()

@app.route('/admin/create_teams', methods=['POST'])
def create_teams():
    event_name = request.form['event_name']
    num_teams = request.form['num_teams']
    participants = Participants.query.filter(Participants.event.has(name=event_name)).all()
    
    if num_teams=='':
        for participant in participants:
            participant.team = participant.institute
    else:
        team_numbers = list(range(1, int(num_teams)+1))
        team_num_list = team_numbers
        while len(team_numbers) < len(participants):
            team_num_list += team_numbers
        random.shuffle(team_num_list)
        
        for i, participant in enumerate(participants):
            participant.team = f'Team {team_numbers[i]}'
    
    db.session.commit()
    return redirect('/admin/')


@app.route('/admin/create_draws', methods=['GET', 'POST'])
def create_draws():
    event_name = request.form['event_name']
    round_list = request.form['round_name'].split('-')
    round_name = round_list[0]
    event = Events.query.filter_by(name=event_name).first()
    event_id = int(event.id) if event else None
    round = Rounds.query.filter_by(event_id=event_id, name=round_name).first()
    round_id = int(round.id) if round else None
    num_adj = request.form['num_adj']
    role1 = request.form['role1']
    role2 = request.form['role2']
    power_matching = request.form.get('power_matching', False)     
    breaks = request.form['breaks']

    if power_matching == 'True':
        if breaks == '':
            breaks = len(teams)
        else:
            breaks = int(breaks)
        teams = db.session.query(distinct(TeamScores.team)).filter_by(event_id=event_id).all()
        teams = sorted(teams, key=lambda t: t.score, reverse=True)
        advancing_teams = teams[:breaks]
        draws = []
        for i in range(0, len(advancing_teams), 2):
            team1 = advancing_teams[i][0]
            team2 = advancing_teams[i+1][0]
            if role1 != '' and role2 != '':
                team1_count = (
                    Draws.query
                    .filter(Draws.event.has(name=event_name))
                    .filter(
                        ((Draws.team1 ==team1)  & (Draws.role1 == role1)) |
                        ((Draws.team2 == team1) & (Draws.role2 == role1))
                    )
                    .count()
                )                
                team2_count = (
                    Draws.query
                    .filter(Draws.event.has(name=event_name))
                    .filter(
                        ((Draws.team1==team2) & (Draws.role1 == role1)) |
                        ((Draws.team2==team2) & (Draws.role2 == role1))
                    )
                    .count()
                )                
                if team1_count <= team2_count:
                    team1_role = role1
                    team2_role = role2
                else:
                    team1_role = role2
                    team2_role = role1
            else:
                team1_role = None
                team2_role = None
            
            draw = Draws(event_id = event_id, round_id = round_id, event = event, round=round, team1=team1, team2=team2, role1=team1_role, team2_role=team2_role)
            draws.append(draw)
    else:
        teams = db.session.query(distinct(Participants.team)).filter_by(event_id=event_id).all()
        print(teams)
        random.shuffle(teams)
        print(teams)
        draws = []
        for i in range(0, len(teams), 2):
            team_1 = teams[i][0]
            print(team_1)
            team_2 = teams[i+1][0]
            if role1 != '' and role2 != '':
                team1_count = (
                    Draws.query
                    .filter(Draws.event.has(name=event_name))
                    .filter(
                        ((Draws.team1 ==team_1)  & (Draws.role1 == role1)) |
                        ((Draws.team2 == team_1) & (Draws.role2 == role1))
                    )
                    .count()
                )                
                team2_count = (
                    Draws.query
                    .filter(Draws.event.has(name=event_name))
                    .filter(
                        ((Draws.team1==team_2) & (Draws.role1 == role1)) |
                        ((Draws.team2==team_2) & (Draws.role2 == role1))
                    )
                    .count()
                )               
                if team1_count <= team2_count:
                    team1_role = role1
                    team2_role = role2
                else:
                    team1_role = role2
                    team2_role = role1
            else:
                team1_role = None
                team2_role = None
            
            draw = Draws(event_id = event_id, round_id = round_id, event = event, round=round, team1=team_1, team2=team_2, role1=team1_role, role2=team2_role)
            print(draw)
            draws.append(draw)

    venues = list(db.session.query(distinct(Venues.name)).filter_by(event_id=event_id).all())
    adjudicators = list(db.session.query(distinct(Adjudicators.name)).filter_by(event_id=event_id).all())
    for draw in draws:
        venue_choice = random.choice(venues)
        draw.venue = venue_choice[0]
        venues.remove(venue_choice)
        adj_list = ''
        for i in range (int(num_adj)):
            adj_choice = random.choice(adjudicators)
            adj_list += adj_choice[0] + ', '
            adjudicators.remove(adj_choice)
        draw.adjudicators = adj_list
        db.session.add(draw)
    
    db.session.commit()
    
    return redirect('/admin/')

@app.route('/admin/release_draws', methods=['POST'])
def release_draws():
    event_name = request.form['event_name']
    round_list = request.form['round_name'].split('-')
    round_name = round_list[0]
    event = Events.query.filter_by(name=event_name).first()
    event_id = int(event.id) if event else None
    round = Rounds.query.filter_by(event_id=event_id, name=round_name).first()
    round_id = int(round.id) if round else None
    draws = Draws.query.filter_by(event_id=event_id, round_id=round_id).all()
    for draw in draws:
        draw.is_released = True
    round.is_released = True
    db.session.commit()

    return redirect('/admin/')


@app.route('/admin/release_motions', methods=['POST'])
def release_motions():
    event_name = request.form['event_name']
    round_list = request.form['round_name'].split('-')
    round_name = round_list[0]
    event = Events.query.filter_by(name=event_name).first()
    event_id = int(event.id) if event else None
    round = Rounds.query.filter_by(event_id=event_id, name=round_name).first()
    round_id = int(round.id) if round else None
    motions = Motions.query.filter_by(event_id=event_id, round_id=round_id).all()
    for motion in motions:
        motion.is_released = True
    db.session.commit()
    return redirect('/admin/')

@app.route('/admin/release_adjudicator_forms', methods=['POST'])
def release_adjudicator_forms():
    event_name = request.form['event_name']
    round_list = request.form['round_name'].split('-')
    round_name = round_list[0]
    event = Events.query.filter_by(name=event_name).first()
    event_id = int(event.id) if event else None
    round = Rounds.query.filter_by(event_id=event_id, name=round_name).first()
    round.adj_form_released = True
    db.session.commit()
    return redirect('/admin/')

@app.route('/admin/release_results', methods=['POST'])
def release_results():
    event_name = request.form['event_name']
    round_list = request.form['round_name'].split('-')
    round_name = round_list[0]
    event = Events.query.filter_by(name=event_name).first()
    event_id = int(event.id) if event else None
    round = Rounds.query.filter_by(event_id=event_id, name=round_name).first()
    round_id = int(round.id) if round else None
    individual_results = IndividualScores.query.filter_by(event_id=event_id, round_id=round_id).all()
    for individual_result in individual_results:
        individual_result.result_released = True
    team_results = TeamScores.query.filter_by(event_id=event_id, round_id=round_id).all()
    for team_result in team_results:
        team_result.result_released = True
    db.session.commit()
    return redirect('/admin/')

@app.route('/admin/release_individual_leaderboard', methods=['POST'])
def release_individual_leaderboard():
    event_name = request.form['event_name']
    event = Events.query.filter_by(name=event_name).first()
    event_id = int(event.id) if event else None
    individual_results = IndividualScores.query.filter_by(event_id=event_id).all()
    for individual_result in individual_results:
        individual_result.leaderboard_released = True
    db.session.commit()
    return redirect('/admin/')

@app.route('/admin/release_institutional_leaderboard', methods=['POST'])
def release_institutional_leaderboard():
    event_name = request.form['event_name']
    event = Events.query.filter_by(name=event_name).first()
    event_id = int(event.id) if event else None
    team_results = TeamScores.query.filter_by(event_id=event_id).all()
    for team_result in team_results:
        team_result.leaderboard_released = True
    db.session.commit()
    return redirect('/admin/')


@app.route('/admin/end_event', methods=['POST'])
def end_event():
    event_name = request.form['event_name']
    event = Events.query.filter_by(name=event_name).first()
    event_id = int(event.id) if event else None
    event.is_ongoing = False
    db.session.commit()
    return redirect('/admin/')


@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')


@app.route('/event/<int:event_id>')
def event_details(event_id):
    event = Events.query.get(event_id)
    adjudicators = Adjudicators.query.filter_by(event_id=event_id).all()
    participants = Participants.query.filter_by(event_id=event_id).all()
    rounds = Rounds.query.filter_by(event_id=event_id).all()
    individual_leaderboard = IndividualScores.query.filter_by(event_id=event_id).all()
    institutional_leaderboard = TeamScores.query.filter_by(event_id=event_id).all()
    return render_template('event_details.html', event=event, adjudicators=adjudicators, participants=participants, rounds=rounds, individual_leaderboard=individual_leaderboard, institutional_leaderboard=institutional_leaderboard)


@app.route('/participants/<int:event_id>')
def participants(event_id):
    event = Events.query.get(event_id)
    adjudicators = Adjudicators.query.filter_by(event_id=event_id).all()
    participants = Participants.query.filter_by(event_id=event_id).all()
    rounds = Rounds.query.filter_by(event_id=event_id).all()
    individual_leaderboard = IndividualScores.query.filter_by(event_id=event_id).all()
    institutional_leaderboard = TeamScores.query.filter_by(event_id=event_id).all()
    return render_template('participants.html', event=event, adjudicators=adjudicators, participants=participants, rounds=rounds, individual_leaderboard=individual_leaderboard, institutional_leaderboard=institutional_leaderboard)

@app.route('/adjudicators/<int:event_id>')
def adjudicators(event_id):
    event = Events.query.get(event_id)
    adjudicators = Adjudicators.query.filter_by(event_id=event_id).all()
    participants = Participants.query.filter_by(event_id=event_id).all()
    rounds = Rounds.query.filter_by(event_id=event_id).all()
    individual_leaderboard = IndividualScores.query.filter_by(event_id=event_id).all()
    institutional_leaderboard = TeamScores.query.filter_by(event_id=event_id).all()
    return render_template('adjudicators.html', event=event, adjudicators=adjudicators, participants=participants, rounds=rounds, individual_leaderboard=individual_leaderboard, institutional_leaderboard=institutional_leaderboard)

@app.route('/round_details/<int:event_id>/<int:round_id>')
def round_details(event_id, round_id):
    event = Events.query.get(event_id)
    round = Rounds.query.get(round_id)
    return render_template('index.html')

@app.route('/individual_leaderboard/<int:event_id>')
def individual_leaderboard(event_id):
    event = Events.query.get(event_id)
    return render_template('index.html')

@app.route('/institutional_leaderboard/<int:event_id>')
def institutional_leaderboard(event_id):
    event = Events.query.get(event_id)
    return render_template('index.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
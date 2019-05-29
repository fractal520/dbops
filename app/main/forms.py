from flask_wtf import Form
from wtforms import StringField, IntegerField, TextAreaField, BooleanField, SelectField, SubmitField, RadioField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User, Dbinfo, Dbtype, Db_arch, Dbinst_role, Instance


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class EditDbinfoForm(Form):
    dbname = StringField('database name', validators=[Required(), Length(0, 64)])
    db_type = SelectField('dbtype', coerce=int)
    db_arch = SelectField('dbarch', coerce=int)
    add_inst = BooleanField('add instance', default=True)
    submit = SubmitField('Submit')

    def __init__(self, dbinfo, *args, **kwargs):
        super(EditDbinfoForm, self).__init__(*args, **kwargs)
        self.db_type.choices = [
            (dbtype.db_type_id, dbtype.db_type_name)
            for dbtype in Dbtype.query.order_by(Dbtype.db_type_name).all()]

        self.db_arch.choices = [
            (dbarch.db_arch_id, dbarch.db_arch_name)
            for dbarch in Db_arch.query.order_by(Db_arch.db_arch_name).all()]

        self.dbinfo = dbinfo


class EditInstForm(Form):
    instance_name = StringField('instance name', validators=[Length(0, 64)])
    dbinst_role = SelectField('instance role', coerce=int)
    host_name = StringField('host name', validators=[Length(0, 64)])
    host_ip = StringField('host ip', validators=[Length(0, 64)])
    specify_inst_ip = BooleanField('instance ip use host\'s default',
                                   default=True)
    inst_ip = StringField('inst ip', validators=[Length(0, 64)])
    access_port = IntegerField('port number')
    #schema_name = StringField('schema name', validators=[Length(0, 64)])
    cont_add = BooleanField('continue add instance')
    submit = SubmitField('Submit')

    def __init__(self, inst, *args, **kwargs):
        super(EditInstForm, self).__init__(*args, **kwargs)
        self.dbinst_role.choices = [
            (role.dbinst_role_id, role.dbinst_role_name) for role in
            Dbinst_role.query.order_by(Dbinst_role.dbinst_role_name).all()]

        self.inst = inst


class EditSchemaForm(Form):
    schema_name = StringField('schema name',
                            validators=[Required(), Length(0, 64)])
    submit = SubmitField('Submit')


class EditHostForm(Form):
    host_name = StringField('host name',
                            validators=[Required(), Length(0, 64)])
    host_ip = StringField('host ip', validators=[Length(0, 64)])
    submit = SubmitField('Submit')


class PostForm(Form):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')

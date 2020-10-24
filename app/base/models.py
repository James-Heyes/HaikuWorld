# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import base64
import os
import sys
from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String, DateTime, Boolean
from flask import current_app, url_for

from app import db, login_manager
from app.base.util import hash_pass
import datetime
from datetime import datetime, timedelta


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class JobSchedule(db.Model, PaginatedAPIMixin, UserMixin):
    
    __tablename__ = 'JobSchedule'

    id = Column(Integer, primary_key=True)
    scheduledTime = Column(DateTime)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
                
            setattr(self, property, value)


    def from_dict(self, data):
        for field in ['scheduledTime']:
            if field in data:
                setattr(self, field, data[field])
    

    def to_dict(self):
        data = {
            'id': self.id,
            'scheduledTime': self.scheduledTime.isoformat(),
        }
        return data

    def __repr__(self):
        return str(self.scheduledTime)


class User(db.Model, PaginatedAPIMixin, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)
    token = Column(db.String(32), index=True, unique=True)
    token_expiration = Column(db.DateTime)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)


    def __repr__(self):
        return str(self.username)
    

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token


    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)


    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
    

    def reset_password(self, data):
        if 'password' in data:
            print("test", flush=True)
            password = hash_pass(data['password']) # we need bytes here (not plain str)
            setattr(self, 'password', password)
        else:
            print("fuck", flush=True)
        return None


    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
    

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
        }
        if include_email:
            data['email'] = self.email
        return data


class Poem(db.Model, PaginatedAPIMixin):

    __tablename__ = 'Poem'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String, unique=False)
    postDate = Column(DateTime)
    rejected = Column(Integer)
    approved = Column(Integer)
    used = Column(Integer)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)


    def __repr__(self):
        return str(self.body)

    def stamp_used(self, used=1):
        setattr(self, 'used', used)

    def from_dict(self, data, new_poem=False):
        for field in ['body', 'title']:
            if field in data:
                setattr(self, field, data[field])
        setattr(self, 'postDate', datetime.datetime.today())
        setattr(self, 'approved', 0)
        setattr(self, 'rejected', 0)
        setattr(self, 'used', 0)
        #if new_poem and 'password' in data:
        #    self.set_password(data['password'])

    def to_dict(self):
        data = {
            'id': self.id,
            'body': self.body,
            'postDate' : self.postDate
        }
        return data
    
    def updateStatus(self, reject=0, accept=0, undo=0):
        if reject:
            setattr(self, 'rejected', 1)
        if accept:
            setattr(self, 'approved', 1)
        if undo:
            setattr(self, 'approved', 0)
            setattr(self, 'rejected', 0)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None

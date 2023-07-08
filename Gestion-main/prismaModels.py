# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Account(models.Model):
    id = models.TextField(primary_key=True)
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userId')  # Field name made lowercase.
    type = models.TextField()
    provider = models.TextField()
    provideraccountid = models.TextField(db_column='providerAccountId')  # Field name made lowercase.
    refresh_token = models.TextField(blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    expires_at = models.IntegerField(blank=True, null=True)
    token_type = models.TextField(blank=True, null=True)
    scope = models.TextField(blank=True, null=True)
    id_token = models.TextField(blank=True, null=True)
    session_state = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Account'
        unique_together = (('provider', 'provideraccountid'),)


class Example(models.Model):
    id = models.TextField(primary_key=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Example'


class Session(models.Model):
    id = models.TextField(primary_key=True)
    sessiontoken = models.TextField(db_column='sessionToken', unique=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userId')  # Field name made lowercase.
    expires = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Session'


class Testtest(models.Model):
    id = models.TextField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'TestTest'


class User(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    surname = models.TextField()
    email = models.TextField(unique=True)
    username = models.TextField(unique=True)
    password = models.TextField()
    isadmin = models.BooleanField(db_column='isAdmin')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User'


class Userinformation(models.Model):
    id = models.TextField(primary_key=True)
    cin = models.TextField()
    naissance = models.DateTimeField()
    address = models.TextField()
    tel = models.TextField(unique=True)
    userid = models.OneToOneField(User, models.DO_NOTHING, db_column='userId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'UserInformation'


class Verificationtoken(models.Model):
    identifier = models.TextField()
    token = models.TextField(unique=True)
    expires = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'VerificationToken'
        unique_together = (('identifier', 'token'),)


class PrismaMigrations(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    checksum = models.CharField(max_length=64)
    finished_at = models.DateTimeField(blank=True, null=True)
    migration_name = models.CharField(max_length=255)
    logs = models.TextField(blank=True, null=True)
    rolled_back_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField()
    applied_steps_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = '_prisma_migrations'

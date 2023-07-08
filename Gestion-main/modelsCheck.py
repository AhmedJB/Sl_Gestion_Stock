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


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class ControllerClient(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    credit = models.FloatField()
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'controller_client'


class ControllerCustomuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    email = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controller_customuser'


class ControllerCustomuserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(ControllerCustomuser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controller_customuser_groups'
        unique_together = (('customuser', 'group'),)


class ControllerCustomuserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(ControllerCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controller_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class ControllerEcheance(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.IntegerField()
    total = models.FloatField()
    paid = models.FloatField()
    reste = models.FloatField()
    dateecheance = models.DateTimeField(db_column='dateEcheance')  # Field name made lowercase.
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'controller_echeance'


class ControllerInvoices(models.Model):
    id = models.BigAutoField(primary_key=True)
    f_id = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'controller_invoices'


class ControllerMvtstock(models.Model):
    id = models.BigAutoField(primary_key=True)
    mvt_type = models.CharField(max_length=255)
    qt_sortie = models.IntegerField()
    qt_entree = models.IntegerField()
    old_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    date = models.DateTimeField()
    product = models.ForeignKey('ControllerProduct', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controller_mvtstock'


class ControllerOptioncategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'controller_optioncategories'


class ControllerOptions(models.Model):
    id = models.BigAutoField(primary_key=True)
    metal = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    product = models.ForeignKey('ControllerProduct', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controller_options'


class ControllerOrder(models.Model):
    id = models.BigAutoField(primary_key=True)
    total = models.FloatField()
    date = models.DateTimeField()
    client = models.ForeignKey(ControllerClient, models.DO_NOTHING)
    o_id = models.CharField(max_length=255)
    paid = models.FloatField()
    mode = models.IntegerField()
    transport = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'controller_order'


class ControllerOrderdetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    prix = models.FloatField()
    order = models.ForeignKey(ControllerOrder, models.DO_NOTHING)
    prix_achat = models.FloatField()
    product_id = models.IntegerField()
    provider_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'controller_orderdetails'


class ControllerProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    ptype = models.CharField(max_length=255)
    price_vente = models.FloatField()
    price_achat = models.FloatField()
    quantity = models.IntegerField()
    provider = models.ForeignKey('ControllerProvider', models.DO_NOTHING)
    p_id = models.CharField(max_length=255)
    paid = models.FloatField()
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'controller_product'


class ControllerProvider(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    date = models.DateTimeField()
    address = models.CharField(max_length=255)
    credit = models.FloatField()

    class Meta:
        managed = False
        db_table = 'controller_provider'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(ControllerCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

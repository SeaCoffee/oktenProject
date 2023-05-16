from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
import profanity_check

class CarBrand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.brand.name} {self.name}'


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, is_premium=False):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            is_premium=is_premium,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_premium=True,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Role(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    account_type = models.CharField(max_length=255, choices=(('basic', 'Basic'), ('premium', 'Premium')),
                                    default='basic')
    roles = models.ManyToManyField(Role)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin


class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        text = f'{self.title} {self.description}'
        if profanity_check.predict([text])[0]:
            self.is_active = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Conversation(models.Model):
    buyer = models.ForeignKey(User, related_name='buyer_conversations', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='seller_conversations', on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Conversation #{self.id}'

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def __str__(self):
        return str(self.user)

class CarMake(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class MissingCarMakeRequest(models.Model):
    car_make = models.CharField(max_length=255)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Missing Car Make Request for {self.car_make}"

class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name

class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency} - {self.rate}"

class AdPrice(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='prices')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ad} - {self.currency} - {self.price}"






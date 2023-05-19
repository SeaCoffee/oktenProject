import django
django.setup()
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CarBrand(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Car Brand'
        verbose_name_plural = 'Car Brands'

    def __str__(self):
        return self.name


class CarModels(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Car Model'
        verbose_name_plural = 'Car Models'

    def __str__(self):
        return f'{self.brand.name} {self.name}'


class MyUserManager(BaseUserManager):
    class Meta:
        verbose_name = 'My User Manager'
        verbose_name_plural = 'My User Managers'

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

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    account_type = models.CharField(max_length=255, choices=(('basic', 'Basic'), ('premium', 'Premium')),
                                    default='basic')
    roles = models.ManyToManyField(Role, related_name='users')

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    car_model = models.ForeignKey(CarModels, on_delete=models.CASCADE)
    seller = models.ForeignKey('main.CustomUser', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ad'
        verbose_name_plural = 'Ad'

    def save(self, *args, **kwargs):
        self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Conversation(models.Model):
    buyer = models.ForeignKey(CustomUser, related_name='buyer_conversations', on_delete=models.CASCADE)
    seller = models.ForeignKey(CustomUser, related_name='seller_conversations', on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f'Conversation #{self.id}'


class Manager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Manager'
        verbose_name_plural = 'Managers'

    def __str__(self):
        return str(self.user)


class CarMake(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Car Make'
        verbose_name_plural = 'Car Make'

    def __str__(self):
        return self.name


class MissingCarMakeRequest(models.Model):
    car_make = models.CharField(max_length=255)
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Missing Car Make Request'
        verbose_name_plural = 'Missing Car Make Requests'

    def __str__(self):
        return f"Missing Car Make Request for {self.car_make}"

class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return self.name

class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Exchange Rate'
        verbose_name_plural = 'Exchange Rates'

    def __str__(self):
        return f"{self.currency} - {self.rate}"

class AdPrice(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='prices')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Ad Price'
        verbose_name_plural = 'Ad Prices'

    def __str__(self):
        return f"{self.ad} - {self.currency} - {self.price}"




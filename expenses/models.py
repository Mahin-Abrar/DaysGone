from django.conf import settings
from django.db import models


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="categories", null=True, blank=True,
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#6366f1")
    icon = models.CharField(max_length=10, default="💰")
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_CHOICES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("mobile", "Mobile Banking"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="expenses")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=300, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="cash")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.amount} - {self.category.name}"

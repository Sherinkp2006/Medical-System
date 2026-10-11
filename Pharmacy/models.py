from django.db import models


class Pharmacy(models.Model):
    """
    Model to store pharmacy/medicine inventory information.

    This model tracks all medicines in stock including their details,
    pricing, and availability.
    """

    medicine_name = models.CharField(
        max_length=100,
        help_text="Name of the medicine"
    )

    manufacturer = models.CharField(
        max_length=100,
        help_text="Name of the medicine manufacturer/company"
    )

    manufacture_date = models.DateField(
        help_text="Date when the medicine was manufactured"
    )

    expiry_date = models.DateField(
        help_text="Date when the medicine expires"
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price of one unit of medicine"
    )

    stock_available = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantity of medicine available in stock"
    )

    # Auto-tracking fields (good practice)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Pharmacy"
        ordering = ['-created_at']

    def __str__(self):
        """Display medicine name when object is printed"""
        return f"{self.medicine_name} - {self.manufacturer}"

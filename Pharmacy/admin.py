from django.contrib import admin
from .models import Pharmacy


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Pharmacy model.
    Customizes how medicines are displayed and managed in Django admin.
    """

    # Fields to display in the list view (table columns)
    list_display = (
        'id',
        'medicine_name',
        'manufacturer',
        'manufacture_date',
        'expiry_date',
        'unit_price',
        'stock_available',
    )

    # Enable search functionality on these fields
    search_fields = (
        'medicine_name',      # Search by medicine name
        'manufacturer',       # Search by manufacturer name
    )

    # Add filters on the right sidebar in list view
    list_filter = (
        'manufacture_date',   # Filter by manufacture date
        'expiry_date',        # Filter by expiry date
    )

    # Fields to be read-only in the admin form
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
    )

    # Organize fields in the edit form
    fieldsets = (
        ('Medicine Information', {
            'fields': ('medicine_name', 'manufacturer')
        }),
        ('Dates', {
            'fields': ('manufacture_date', 'expiry_date')
        }),
        ('Pricing & Stock', {
            'fields': ('unit_price', 'stock_available')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsed by default
        }),
    )


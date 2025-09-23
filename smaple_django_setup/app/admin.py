from django.contrib import admin
from app.models import *
from datetime import datetime
from .models import UserRole 

# Register your models here.

models = [
    UserRole,
    Profile,
    OtpHistory,
    EmailTemplate,
    Tag,
    Category,
    Country,
    State,
    City,
    zip,
    Address,
    OrderHistory,
    TransactionHistory,
    Leads,
    ProductAddon,
    Review,
    QuotationOrder,
    TransactionHistory,
]


class ProfileAdmin(admin.ModelAdmin):
    # form = CountryMasterForm
    exclude = ["updated_at", "created_at"]

    list_filter = ["is_active", "created_at", "updated_at"]

    search_fields = [
        "email",
    ]

    list_display = [
        "first_name",
        "last_name",
        "email",
        "is_active",
        "created_at",
        "updated_at",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Profile, ProfileAdmin)


class OtpHistoryAdmin(admin.ModelAdmin):
    # form = CountryMasterForm
    # exclude = ["expiration_time", "created_at"]

    list_filter = ["created_at", "expiration_time", "is_used", "otp_type"]

    # search_fields = []

    list_display = [
        "profile",
        "otp",
        "is_used",
        "otp_type",
        "created_at",
        "expiration_time",
    ]

    readonly_fields = list_display + ["otp"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(OtpHistory, OtpHistoryAdmin)


class UserRoleAdmin(admin.ModelAdmin):
    # form = CountryMasterForm
    exclude = ["updated_at", "created_at"]

    list_filter = ["created_at", "updated_at", "is_active"]

    # search_fields = []

    list_display = ["name", "is_active", "created_at", "updated_at"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(UserRole, UserRoleAdmin)


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["email_event_type", "subject", "body"]
    search_fields = ["email_event_type", "subject"]
    list_filter = ["email_event_type"]
    ordering = ["email_event_type"]
    readonly_fields = []
    exclude = [
        "is_active",
        "updated_at",
        "created_at",
        "reason_to_deactivate",
        "last_deactivated_at",
    ]


admin.site.register(EmailTemplate, EmailTemplateAdmin)


class CategoryAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_filter = ["name", "is_active", "is_popular"]

    search_fields = [
        "name",
    ]

    list_display = [
        "name",
        "cover_pic_s3_key",
        "description",
        "is_active",
        "is_popular",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Category, CategoryAdmin)


class TagAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_filter = ["name", "is_active"]

    search_fields = [
        "name",
    ]

    list_display = ["name", "is_active"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Tag, TagAdmin)


class CountryAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_filter = ["name", "iso_code", "is_active"]

    search_fields = [
        "name",
    ]

    list_display = [
        "name",
        "iso_code",
        "is_active",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Country, CountryAdmin)


class StateAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_filter = ["name", "country", "is_active"]

    search_fields = [
        "name",
    ]

    list_display = [
        "name",
        "country",
        "is_active",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(State, StateAdmin)


class CityAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_filter = ["name", "state", "is_active"]

    search_fields = [
        "name",
    ]

    list_display = [
        "name",
        "state",
        "is_active",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(City, CityAdmin)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_filter = ["name", "city", "is_active"]

    search_fields = ["name"]

    list_display = [
        "name",
        "city",
        "is_active",
        "servicable_radius",
        "address_details",
        "additional_address_detail",
        "latitude",
        "longitude",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


class AddressAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_filter = ["is_active"]

    list_display = [
        "profile_address",
        "city",
        "is_active",
        "zip_code",
        "lat",
        "long",
        "address_details",
        "additional_address_detail",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Address, AddressAdmin)


class APILogAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = [
        "method",
        "path",
        "content_type",
        "query_params",
        "request_body",
        "response_body",
        "request_files_info",
        "status_code",
        "response_time_ms",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(APILog, APILogAdmin)


class ServiceAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = [
        "name",
        "is_active",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Service, ServiceAdmin)


class ServicePriceTypeAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = [
        "name",
        "is_active",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(ServicePriceType, ServicePriceTypeAdmin)


class ServiceFeatureAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = [
        "name",
        "is_active",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(ServiceFeature, ServiceFeatureAdmin)


class ServiceTypeAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = [
        "name",
        "is_active",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(ServiceType, ServiceTypeAdmin)


class ServiceFeatureMappingAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = [
        "service",
        "service_type",
        "get_features",
        "price_type",
        "price",
        "discounted_price",
        "price_per_square_feet",
        "description",
        "is_active",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def get_features(self, obj):
        return ", ".join([f.name for f in obj.features.all()])

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(ServiceFeatureMapping, ServiceFeatureMappingAdmin)


class ServiceAttachmentAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = ["id", "service", "service_feature_mapping"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(ServiceAttachment, ServiceAttachmentAdmin)


class OrderHistoryAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = [
        "user",
        "order_id",
        "allocated_technician",
        "order_status",
        "order_detail",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(OrderHistory, OrderHistoryAdmin)


class OrderLogAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = ["order", "previous_order_status", "current_order_status"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(OrderLog, OrderLogAdmin)


class LeadsAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = [
        "name",
        "email",
        "mobile",
        "customer_address",
        "additional_address",
        "lat",
        "long",
        "message",
        "created_at",
    ]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Leads, LeadsAdmin)


class ProductAddonAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = ["name", "category"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(ProductAddon, ProductAddonAdmin)


class ReviewAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = ["user", "service", "comment", "star"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Review, ReviewAdmin)


class QuotationOrderAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = ["order", "service_feature_mapping", "walls", "status"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(QuotationOrder, QuotationOrderAdmin)


class TransactionHistoryAdmin(admin.ModelAdmin):

    exclude = ["updated_at", "created_at"]

    list_display = ["id", "order", "razorpay_order_id", "transaction_type"]

    list_per_page = 10

    def has_add_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_at = datetime.now()
        else:
            obj.updated_at = datetime.now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(TransactionHistory, TransactionHistoryAdmin)

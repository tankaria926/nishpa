from django.contrib import admin
from .models import ProductCategory, Product, Inquiry, InquiryItem


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sku')
    list_filter = ('category',)


class InquiryItemInline(admin.TabularInline):
    model = InquiryItem
    extra = 0


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'status', 'created_at', 'item_count')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'message')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [InquiryItemInline]
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Inquiry Details', {
            'fields': ('message', 'status')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

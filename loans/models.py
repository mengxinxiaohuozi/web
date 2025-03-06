from django.db import models
from django.utils import timezone

def get_current_year():
    return timezone.now().year

# Create your models here.

class LoanRecord(models.Model):
    LOAN_TYPES = [
        ('convenience', '便民卡'),
        ('normal', '普通贷款'),
        ('rural', '惠农e贷'),
        ('mortgage', '按揭贷款')
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('completed', '已完成')
    ]
    
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES, verbose_name='贷款类型')
    loan_number = models.CharField(max_length=50, unique=True, verbose_name='贷款档案编号')
    customer_name = models.CharField(max_length=100, verbose_name='客户姓名')
    id_number = models.CharField(max_length=18, verbose_name='身份证号', default='000000000000000000')
    year = models.IntegerField(verbose_name='年份', default=get_current_year)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='贷款金额')
    loan_date = models.DateField(verbose_name='贷款日期')
    loan_term = models.IntegerField(verbose_name='贷款期限(月)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    change_history = models.TextField(blank=True, null=True, verbose_name='溯源记录')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '贷款档案'
        verbose_name_plural = '贷款档案'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.loan_number} - {self.customer_name}"

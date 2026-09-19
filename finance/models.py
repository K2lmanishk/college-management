from django.db import models
from accounts.models import Student, Program


class ProgramSemesterFee(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.CharField(max_length=50)
    fee_amount = models.FloatField()
    academic_year = models.CharField(max_length=20, default='2025-2026')

    class Meta:
        unique_together = ('program', 'semester')

    def __str__(self):
        return f"{self.program.code} - {self.semester}: ₹{self.fee_amount}"


class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    amount = models.FloatField()
    due_date = models.DateField()
    paid_amount = models.FloatField(default=0)
    status = models.CharField(max_length=20, default='Pending')
    payment_method = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)

    @property
    def due_amount(self):
        return self.amount - self.paid_amount

    def __str__(self):
        return f"{self.student} - ₹{self.amount} ({self.status})"

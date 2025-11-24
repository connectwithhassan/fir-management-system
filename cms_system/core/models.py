from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytesseract
from PIL import Image
import platform # OS check krne k liye

# --- SMART TESSERACT PATH CONFIGURATION ---
if platform.system() == 'Windows':
    # Aapke Local Computer k liye
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    # cPanel / Linux Server k liye (Standard Path)
    # Note: Server pr Tesseract install hona chahiye
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# --- 1. POLICE OFFICER ---
class PoliceOfficer(models.Model):
    RANK_CHOICES = (
        ('CONSTABLE', 'Constable'), ('ASI', 'Assistant Sub-Inspector (ASI)'),
        ('SI', 'Sub-Inspector (SI)'), ('INSPECTOR', 'Inspector'), ('SHO', 'SHO'),
    )
    name = models.CharField(max_length=100)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='SI')
    badge_number = models.CharField(max_length=20, unique=True, help_text="Belt No.")
    def __str__(self): return f"{self.rank} {self.name} ({self.badge_number})"

# --- 2. CRIMINAL ---
class Criminal(models.Model):
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100, blank=True)
    cnic = models.CharField(max_length=15, unique=True)
    age = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=1, choices=(('M','Male'),('F','Female'),('O','Other')), default='M')
    photo = models.ImageField(upload_to='criminals/', blank=True, null=True)
    address = models.TextField(default="Unknown")
    crime_history = models.TextField(blank=True)
    def __str__(self): return f"{self.name} ({self.cnic})"

# --- 3. FIR ---
class FIR(models.Model):
    STATUS_CHOICES = (('PENDING','Pending Investigation'),('SOLVED','Case Solved'),('SNOOZED','Snoozed'),('EXPIRED','Expired Case'))
    
    case_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    date_reported = models.DateField(default=timezone.now, verbose_name="FIR Date")
    is_unknown_suspect = models.BooleanField(default=False, verbose_name="Unknown Suspect")
    suspects = models.ManyToManyField(Criminal, blank=True, verbose_name="Select Criminals")
    fir_image = models.ImageField(upload_to='fir_scans/', null=True, blank=True)
    description = models.TextField(blank=True)
    officer_assigned = models.ForeignKey(PoliceOfficer, on_delete=models.SET_NULL, null=True, verbose_name="Investigating Officer")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.fir_image and not self.description:
            try:
                img = Image.open(self.fir_image)
                extracted_text = pytesseract.image_to_string(img)
                self.description = extracted_text
                if not self.title: self.title = extracted_text.split('\n')[0][:100]
            except: pass
        super().save(*args, **kwargs)
    def __str__(self): return str(self.case_id)

# --- 4. ACTION LOG ---
class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
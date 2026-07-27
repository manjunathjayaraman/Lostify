from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    logout,
    login,
    authenticate,
    get_user_model,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import activate

from .models import (
    LostItemReport,
    FoundItemReport,
    ItemMatch,
    ContactComplaint,
    UserPreference,
    Profile,
)

import json
import random
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

GOOGLE_CLIENT_ID = "744893062918-ea0q0rvoasofupumu9tdd0c19k9kjmnv.apps.googleusercontent.com"


def generate_otp():
    secure_random = random.SystemRandom()
    return str(secure_random.randint(100000, 999999))


import traceback

def send_otp_email(email, otp):
    try:
        html_message = render_to_string("otp_email.html", {"otp": otp})

        email_message = EmailMessage(
            subject="Lostify OTP Verification",
            body=html_message,
            from_email=None,      # Uses DEFAULT_FROM_EMAIL from settings.py
            to=[email],
        )

        email_message.content_subtype = "html"

        result = email_message.send(fail_silently=False)

        print("Email sent result:", result)

        return True

    except Exception:
        traceback.print_exc()
        return False

def home(request):
    return render(request, "home.html")


@login_required
def report_lost(request):
    if request.method == "POST":
        LostItemReport.objects.create(
            user=request.user,
            title=request.POST.get("title"),
            category=request.POST.get("category"),
            brand=request.POST.get("brand"),
            model=request.POST.get("model"),
            color=request.POST.get("color"),
            estimated_value=request.POST.get("estimated_value"),
            description=request.POST.get("description"),
            imei_number=request.POST.get("imei_number"),
            serial_number=request.POST.get("serial_number"),
            vehicle_number=request.POST.get("vehicle_number"),
            lost_date=request.POST.get("lost_date"),
            lost_time=request.POST.get("lost_time") or None,
            lost_place_text=request.POST.get("lost_place_text"),
            latitude=request.POST.get("latitude"),
            longitude=request.POST.get("longitude"),
            contact_name=request.POST.get("contact_name"),
            contact_phone=request.POST.get("contact_phone"),
            contact_email=request.POST.get("contact_email"),
            alternate_contact=request.POST.get("alternate_contact"),
            reward_note=request.POST.get("reward_note"),
            extra_notes=request.POST.get("extra_notes"),
            item_image=request.FILES.get("item_image"),
            ownership_bill=request.FILES.get("ownership_bill"),
        )

        messages.success(
            request,
            "Your lost item report has been submitted successfully. You can track its status anytime from the My Status section.",
        )
        return redirect("home")

    return render(request, "report_lost.html")


@login_required
def report_found(request):
    if request.method == "POST":
        FoundItemReport.objects.create(
            user=request.user,
            title=request.POST.get("title"),
            category=request.POST.get("category"),
            brand=request.POST.get("brand"),
            model=request.POST.get("model"),
            color=request.POST.get("color"),
            description=request.POST.get("description"),
            imei_number=request.POST.get("imei_number"),
            serial_number=request.POST.get("serial_number"),
            vehicle_number=request.POST.get("vehicle_number"),
            found_date=request.POST.get("found_date"),
            found_time=request.POST.get("found_time") or None,
            found_place_text=request.POST.get("found_place_text"),
            latitude=request.POST.get("latitude"),
            longitude=request.POST.get("longitude"),
            finder_name=request.POST.get("finder_name"),
            finder_phone=request.POST.get("finder_phone"),
            finder_email=request.POST.get("finder_email"),
            extra_notes=request.POST.get("extra_notes"),
            item_image=request.FILES.get("item_image"),
        )

        messages.success(
            request,
            "Your found item report has been submitted successfully. You can track its status anytime from the My Status section.",
        )
        return redirect("home")

    return render(request, "report_found.html")


def find_items(request):
    query = request.GET.get("q", "").strip()
    found_items = FoundItemReport.objects.exclude(status="returned").order_by("-created_at")

    if query:
        found_items = found_items.filter(
            Q(title__icontains=query)
            | Q(category__icontains=query)
            | Q(brand__icontains=query)
            | Q(model__icontains=query)
            | Q(color__icontains=query)
            | Q(description__icontains=query)
            | Q(found_place_text__icontains=query)
        ).distinct()

    return render(
        request,
        "find_items.html",
        {
            "found_items": found_items,
            "query": query,
        },
    )


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        try:
            user_obj = User.objects.get(email__iexact=email)
            username = user_obj.username
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "Invalid email or password"})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            saved_language = getattr(getattr(user, "preferences", None), "language", "en")
            if saved_language:
                activate(saved_language)
                request.session["django_language"] = saved_language

            return redirect("home")

        return render(request, "login.html", {"error": "Invalid email or password"})

    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname", "").strip()
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not email.endswith("@gmail.com"):
            return render(
                request,
                "register.html",
                {"error": "Please enter a valid Gmail address"},
            )

        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        if User.objects.filter(email__iexact=email).exists():
            return render(request, "register.html", {"error": "Email already exists"})

        otp = generate_otp()

        request.session["register_data"] = {
            "fullname": fullname,
            "email": email,
            "username": username,
            "password": password,
        }
        request.session["register_otp"] = otp

        print("Generated OTP:", otp)
        print("Sending OTP to:", email)
        
        email_sent = send_otp_email(email, otp)

        if not email_sent:
            return render(
                request,
                "register.html",
                {"error": "Unable to send OTP email right now. Please try again in a moment."},
            )

        return redirect("verify_otp")

    return render(request, "register.html")


def verify_otp_view(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        saved_otp = request.session.get("register_otp")
        register_data = request.session.get("register_data")

        if not saved_otp or not register_data:
            return render(
                request,
                "verify_otp.html",
                {"error": "OTP session expired. Please register again."},
            )

        if entered_otp != saved_otp:
            return render(request, "verify_otp.html", {"error": "Invalid OTP"})

        fullname = register_data.get("fullname", "")
        email = register_data.get("email", "")
        username = register_data.get("username", "")
        password = register_data.get("password", "")

        parts = fullname.split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        UserPreference.objects.get_or_create(
            user=user,
            defaults={
                "language": "en",
                "region": "India",
            },
        )

        Profile.objects.get_or_create(user=user)

        request.session.pop("register_otp", None)
        request.session.pop("register_data", None)

        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "verify_otp.html")


def resend_otp_view(request):
    register_data = request.session.get("register_data")

    if not register_data:
        return redirect("register")

    otp = generate_otp()
    request.session["register_otp"] = otp

    email_sent = send_otp_email(register_data["email"], otp)

    if not email_sent:
        return render(
            request,
            "verify_otp.html",
            {"error": "Unable to resend OTP right now. Please try again shortly."},
        )

    return render(
        request,
        "verify_otp.html",
        {"success": "A new OTP has been sent to your email."},
    )


def logout_view(request):
    logout(request)
    return redirect("home")


@csrf_exempt
@require_POST
def google_login(request):
    try:
        credential = None

        if request.content_type and "application/json" in request.content_type:
            data = json.loads(request.body)
            credential = data.get("credential")
        else:
            credential = request.POST.get("credential")

        if not credential:
            return JsonResponse({"success": False, "error": "No credential received"}, status=400)

        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )

        if idinfo.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            return JsonResponse({"success": False, "error": "Invalid issuer"}, status=400)

        email = idinfo.get("email", "").lower()
        google_name = idinfo.get("name", "")
        email_verified = idinfo.get("email_verified", False)

        if not email or not email_verified:
            return JsonResponse({"success": False, "error": "Email not verified"}, status=400)

        UserModel = get_user_model()
        user = UserModel.objects.filter(email__iexact=email).first()

        if not user:
            username_base = google_name.strip().replace(" ", "") if google_name else email.split("@")[0]
            username = username_base
            count = 1

            while UserModel.objects.filter(username=username).exists():
                username = f"{username_base}{count}"
                count += 1

            name_parts = google_name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            user = UserModel.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user.set_unusable_password()
            user.save()
        else:
            if google_name and not user.first_name:
                name_parts = google_name.split()
                user.first_name = name_parts[0] if name_parts else ""
                user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                user.save()

        UserPreference.objects.get_or_create(
            user=user,
            defaults={
                "language": "en",
                "region": "India",
            },
        )

        Profile.objects.get_or_create(user=user)

        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)

        saved_language = getattr(getattr(user, "preferences", None), "language", "en")
        if saved_language:
            activate(saved_language)
            request.session["django_language"] = saved_language

        return JsonResponse({"success": True, "username": user.username})

    except ValueError as e:
        return JsonResponse(
            {"success": False, "error": f"Invalid Google token: {str(e)}"},
            status=400,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def my_status(request):
    lost_items = LostItemReport.objects.filter(user=request.user).order_by("-created_at")
    found_items = FoundItemReport.objects.filter(user=request.user).order_by("-created_at")
    matches = ItemMatch.objects.filter(
        Q(lost_item__user=request.user) | Q(found_item__user=request.user)
    ).distinct().order_by("-matched_at")

    return render(
        request,
        "my_status.html",
        {
            "lost_items": lost_items,
            "found_items": found_items,
            "matches": matches,
        },
    )


@login_required
def mark_lost_item_found(request, lost_id, found_id):
    lost_item = get_object_or_404(LostItemReport, id=lost_id)
    found_item = get_object_or_404(FoundItemReport, id=found_id)

    lost_item.status = "found"
    found_item.status = "matched"
    lost_item.save()
    found_item.save()

    ItemMatch.objects.get_or_create(
        lost_item=lost_item,
        found_item=found_item,
        defaults={"is_confirmed": True},
    )

    return redirect("my_status")


@login_required
@require_POST
def claim_found_item(request, found_id):
    found_item = get_object_or_404(FoundItemReport, id=found_id, status="unclaimed")

    lost_item = LostItemReport.objects.filter(
        user=request.user,
        status="not_found",
    ).order_by("-created_at").first()

    if not lost_item:
        return JsonResponse(
            {
                "success": False,
                "error": "You need at least one lost item report to claim a found item.",
            }
        )

    found_item.status = "matched"
    found_item.save()

    lost_item.status = "found"
    lost_item.save()

    ItemMatch.objects.get_or_create(
        lost_item=lost_item,
        found_item=found_item,
        defaults={"is_confirmed": True},
    )

    return JsonResponse({"success": True})


def help_view(request):
    return render(request, "help.html")


def contact_us_view(request):
    if request.method == "POST":
        ContactComplaint.objects.create(
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            phone_number=request.POST.get("phone_number"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )
        messages.success(request, "Your complaint has been submitted successfully.")
        return redirect("home")

    return render(request, "contact_us.html")


def detect_region_from_request(request):
    return "India"


@login_required
def settings_view(request):
    prefs, created = UserPreference.objects.get_or_create(
        user=request.user,
        defaults={"region": "India", "language": "en"},
    )

    detected_region = detect_region_from_request(request)
    if prefs.region != detected_region:
        prefs.region = detected_region
        prefs.save(update_fields=["region"])

    if request.method == "POST":
        current_password = request.POST.get("current_password", "").strip()
        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if current_password or new_password or confirm_password:
            if not request.user.check_password(current_password):
                return render(
                    request,
                    "settings.html",
                    {
                        "prefs": prefs,
                        "error": "Current password is incorrect.",
                    },
                )

            if new_password != confirm_password:
                return render(
                    request,
                    "settings.html",
                    {
                        "prefs": prefs,
                        "error": "New passwords do not match.",
                    },
                )

            if len(new_password) < 8:
                return render(
                    request,
                    "settings.html",
                    {
                        "prefs": prefs,
                        "error": "New password must be at least 8 characters.",
                    },
                )

            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

        prefs.email_notifications = bool(request.POST.get("email_notifications"))
        prefs.match_alerts = bool(request.POST.get("match_alerts"))
        prefs.claim_updates = bool(request.POST.get("claim_updates"))

        prefs.contact_after_match = bool(request.POST.get("contact_after_match"))
        prefs.hide_sensitive_details = bool(request.POST.get("hide_sensitive_details"))
        prefs.activity_logging = bool(request.POST.get("activity_logging"))

        prefs.otp_verification = bool(request.POST.get("otp_verification"))
        prefs.google_login_access = bool(request.POST.get("google_login_access"))
        prefs.login_alerts = bool(request.POST.get("login_alerts"))

        prefs.save_search_history = bool(request.POST.get("save_search_history"))
        prefs.save_report_drafts = bool(request.POST.get("save_report_drafts"))
        prefs.personalized_suggestions = bool(request.POST.get("personalized_suggestions"))

        prefs.region = detected_region
        prefs.save()

        messages.success(request, "Settings saved successfully.")
        return redirect("home")

    return render(request, "settings.html", {"prefs": prefs})


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name = request.POST.get("last_name", "").strip()
        request.user.save()

        profile.phone_number = request.POST.get("phone_number", "").strip()
        profile.location = request.POST.get("location", "").strip()
        profile.bio = request.POST.get("bio", "").strip()

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("my_profile")

    lost_count = LostItemReport.objects.filter(user=request.user).count()
    found_count = FoundItemReport.objects.filter(user=request.user).count()
    matched_count = ItemMatch.objects.filter(
        Q(lost_item__user=request.user) | Q(found_item__user=request.user)
    ).distinct().count()
    complaint_count = ContactComplaint.objects.filter(email=request.user.email).count()

    return render(
        request,
        "my_profile.html",
        {
            "profile": profile,
            "lost_count": lost_count,
            "found_count": found_count,
            "matched_count": matched_count,
            "complaint_count": complaint_count,
        },
    )
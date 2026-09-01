from django.core.management.base import BaseCommand

from expenses.models import Category
from rewards.models import Badge

DEFAULT_CATEGORIES = [
    ("Food", "#ef4444", "🍔"),
    ("Transport", "#6366f1", "🚗"),
    ("Bills", "#f59e0b", "📄"),
    ("Shopping", "#8b5cf6", "🛍️"),
    ("Health", "#10b981", "💊"),
    ("Entertainment", "#06b6d4", "🎬"),
    ("Education", "#ec4899", "📚"),
    ("Other", "#84cc16", "💰"),
]

DEFAULT_BADGES = [
    (7, "Week Warrior", "Completed 7 days in a row!", "🔥", "#f59e0b"),
    (14, "Fortnight Fighter", "Two weeks of consistency!", "⚡", "#6366f1"),
    (30, "Monthly Master", "A full month of dedication!", "🌟", "#10b981"),
    (60, "Iron Will", "60 days — unstoppable!", "💎", "#8b5cf6"),
    (100, "Century Legend", "100-day streak achieved!", "👑", "#ef4444"),
]


class Command(BaseCommand):
    help = "Seed default categories and badges"

    def handle(self, *args, **options):
        for name, color, icon in DEFAULT_CATEGORIES:
            Category.objects.get_or_create(
                name=name, is_default=True, user=None,
                defaults={"color": color, "icon": icon},
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(DEFAULT_CATEGORIES)} categories"))

        for days, name, desc, icon, color in DEFAULT_BADGES:
            Badge.objects.get_or_create(
                milestone_days=days,
                defaults={"name": name, "description": desc, "icon": icon, "color": color},
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(DEFAULT_BADGES)} badges"))

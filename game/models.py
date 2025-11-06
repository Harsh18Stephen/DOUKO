from django.db import models
import string, random, json


# ✅ Helper to generate unique codes
def generate_unique_code():
    length = 6
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if not Room.objects.filter(code=code).exists():
            return code


# ✅ Room model
class Room(models.Model):
    code = models.CharField(max_length=10, unique=True, default=generate_unique_code)
    host = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10, default="easy")
    puzzle = models.TextField()   # JSON string of puzzle grid
    solution = models.TextField() # JSON string of solved grid
    winner = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    player_times = models.JSONField(default=list)  # store [{"name":..., "time":...}, ...]

    def __str__(self):
        return f"Room {self.code} ({self.difficulty})"

    # helper function for results
    def add_player_result(self, name, time):
        results = self.player_times or []
        results.append({"name": name, "time": time})
        self.player_times = results
        self.save()


# ✅ Player model
class Player(models.Model):
    name = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="players")

    def __str__(self):
        return f"{self.name} ({self.room.code})"

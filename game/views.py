from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Room, Player
from .sudoku import generate_sudoku
import uuid
import json


# 🏠 Home page – create or join a room
def home(request):
    if request.method == "POST":
        name = request.POST.get("player_name")
        action = request.POST.get("action")
        request.session["player_name"] = name

        # ✅ Create a new room
        if action == "create":
            puzzle, solution = generate_sudoku()
            room = Room.objects.create(
                host=name,  # 👈 use host instead of name
                code=str(uuid.uuid4())[:6].upper(),
                puzzle=json.dumps(puzzle),
                solution=json.dumps(solution),
                started=False
            )
            Player.objects.create(name=name, room=room)
            return redirect("room", code=room.code)

        # ✅ Join an existing room
        elif action == "join":
            code = request.POST.get("room_code", "").upper()
            try:
                room = Room.objects.get(code=code)
                Player.objects.create(name=name, room=room)
                return redirect("room", code=room.code)
            except Room.DoesNotExist:
                return render(request, "home.html", {"error": "Room not found!"})

    return render(request, "home.html")



# 🧩 Room view – show players, start button for host
def room(request, code):
    room = get_object_or_404(Room, code=code)
    players = room.players.all()  # ✅ thanks to related_name="players"
    host = players.first()
    
    player_name = request.session.get("player_name")
    is_host = (player_name == host.name if host else False)

    # Redirect directly to game if it’s already started
    if room.started:
        return redirect("game", code=room.code)

    return render(request, "room.html", {
        "room": room,
        "players": players,
        "is_host": is_host,
    })

from django.http import HttpResponse

# 🕹️ Game page – render Sudoku puzzle
def game(request, code):
    room = get_object_or_404(Room, code=code)
    puzzle = json.loads(room.puzzle)

    context = {
        "room": room,
        "puzzle": puzzle,
        "cells": range(81),  
    }


    return render(request, "game.html", context)



# 📊 API – check if game started
def room_status(request, code):
    try:
        room = Room.objects.get(code=code)
        return JsonResponse({"started": room.started})
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)


# 🚀 API – start the game (host only)
@csrf_exempt
def start_game(request, code):
    try:
        room = Room.objects.get(code=code)
        room.started = True
        room.save()
        return JsonResponse({"success": True})
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)


# 🧮 API – submit Sudoku solution
@csrf_exempt
def submit_solution(request, code):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    room = get_object_or_404(Room, code=code)
    data = json.loads(request.body)
    grid = data.get("grid")
    player_name = request.session.get("player_name", "Unknown Player")
    player_time = data.get("time", 0)

    solution = json.loads(room.solution)

    # Normalize both for comparison
    grid_int = [[int(c) for c in r] for r in grid]
    solution_int = [[int(c) for c in r] for r in solution]

    if room.winner:
        room.add_player_result(player_name, player_time)
        return JsonResponse({"status": "lost"})

    if grid_int == solution_int:
        room.add_player_result(player_name, player_time)

        if not room.winner:
            room.winner = player_name
            room.save()

        return JsonResponse({"status": "winner"})

    return JsonResponse({"status": "wrong"})

# 🏁 Results Page
def result_view(request, code):
    room = get_object_or_404(Room, code=code)

    # 🧩 Debug info
    print("DEBUG → room.player_times:", room.player_times)
    print("DEBUG → type:", type(room.player_times))

    # Handle both string and list cases
    if isinstance(room.player_times, str):
        try:
            results = json.loads(room.player_times)
        except json.JSONDecodeError:
            print("DEBUG → JSONDecodeError: couldn't decode string")
            results = []
    elif isinstance(room.player_times, list):
        results = room.player_times
    else:
        print("DEBUG → Unexpected type for player_times")
        results = []

    # Sort players by time
    ranked = sorted(results, key=lambda x: x["time"]) if results else []

    for i, r in enumerate(ranked):
        r["rank"] = i + 1
        minutes = int(r["time"] // 60)
        seconds = int(r["time"] % 60)
        r["display_time"] = f"{minutes}:{seconds:02d}"

    return render(request, "result.html", {"room": room, "ranked": ranked})



def add_player_result(self, player_name, time_taken):
    results = json.loads(self.player_times) if isinstance(self.player_times, str) else (self.player_times or [])
    results.append({"name": player_name, "time": time_taken})
    self.player_times = json.dumps(results)
    self.save()
    
def solved_list(request):
    """
    Show all rooms/puzzles that have been solved.
    """
    # Only get rooms with a winner (solved)
    solved_rooms = Room.objects.filter(winner__isnull=False)

    rooms_data = []
    for room in solved_rooms:
        puzzle = json.loads(room.solution)  # show solution
        rooms_data.append({
            "code": room.code,
            "winner": room.winner,
            "solution": puzzle,
        })

    return render(request, "solved_list.html", {"rooms": rooms_data})

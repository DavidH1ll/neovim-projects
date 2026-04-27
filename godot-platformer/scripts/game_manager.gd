extends Node

class_name GameManager

@onready var player: Player = $"../Player"
@onready var ui: GameUI = $"../UI"

var score: int = 0
var coins_collected: int = 0
var total_coins: int = 0
var level_completed: bool = false

func _ready() -> void:
	# Count total coins in level
	total_coins = get_tree().get_nodes_in_group("coin").size()
	ui.update_coin_count(coins_collected, total_coins)
	ui.update_score(score)
	ui.update_health(player.health)

	# Connect player signals
	player.health_changed.connect(_on_player_health_changed)
	player.died.connect(_on_player_died)

	# Connect all coins
	for coin in get_tree().get_nodes_in_group("coin"):
		if coin.has_signal("collected"):
			coin.collected.connect(_on_coin_collected)

	# Connect flag
	for flag in get_tree().get_nodes_in_group("flag"):
		if flag.has_signal("level_complete"):
			flag.level_complete.connect(_on_level_complete)

func _process(_delta: float) -> void:
	if Input.is_action_just_pressed("restart") and player.is_dead:
		restart_level()

func _on_coin_collected() -> void:
	coins_collected += 1
	score += 100
	ui.update_coin_count(coins_collected, total_coins)
	ui.update_score(score)

func _on_player_health_changed(new_health: int) -> void:
	ui.update_health(new_health)

func _on_player_died() -> void:
	ui.show_game_over(score)
	await get_tree().create_timer(2.0).timeout
	# Optional: auto-restart or wait for R key

func _on_level_complete() -> void:
	if level_completed:
		return
	level_completed = true
	score += 1000  # Completion bonus
	ui.show_level_complete(score, coins_collected, total_coins)

func restart_level() -> void:
	get_tree().reload_current_scene()

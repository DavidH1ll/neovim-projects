extends Control

class_name GameUI

@onready var score_label: Label = $MarginContainer/VBoxContainer/ScoreLabel
@onready var coin_label: Label = $MarginContainer/VBoxContainer/HBoxContainer/CoinLabel
@onready var health_bar: HBoxContainer = $MarginContainer/VBoxContainer/HBoxContainer/HealthBar
@onready var game_over_panel: PanelContainer = $GameOverPanel
@onready var game_over_label: Label = $GameOverPanel/VBoxContainer/GameOverLabel
@onready var final_score_label: Label = $GameOverPanel/VBoxContainer/FinalScoreLabel
@onready var restart_label: Label = $GameOverPanel/VBoxContainer/RestartLabel
@onready var level_complete_panel: PanelContainer = $LevelCompletePanel

var heart_texture: Texture2D

func _ready() -> void:
	game_over_panel.hide()
	level_complete_panel.hide()

func update_score(new_score: int) -> void:
	score_label.text = "Score: %d" % new_score

func update_coin_count(collected: int, total: int) -> void:
	coin_label.text = "Coins: %d / %d" % [collected, total]

func update_health(health: int) -> void:
	# Clear existing hearts
	for child in health_bar.get_children():
		child.queue_free()

	# Add heart labels
	for i in range(health):
		var heart := Label.new()
		heart.text = "♥"
		heart.add_theme_color_override("font_color", Color(1, 0.2, 0.2))
		heart.add_theme_font_size_override("font_size", 32)
		health_bar.add_child(heart)

func show_game_over(final_score: int) -> void:
	game_over_label.text = "GAME OVER"
	final_score_label.text = "Final Score: %d" % final_score
	restart_label.text = "Press R to Restart"
	game_over_panel.show()

func show_level_complete(final_score: int, coins: int, total: int) -> void:
	var label := level_complete_panel.get_node("VBoxContainer/CompleteLabel") as Label
	var score_l := level_complete_panel.get_node("VBoxContainer/ScoreLabel") as Label
	var coin_l := level_complete_panel.get_node("VBoxContainer/CoinLabel") as Label
	var restart_l := level_complete_panel.get_node("VBoxContainer/RestartLabel") as Label

	label.text = "LEVEL COMPLETE!"
	score_l.text = "Score: %d" % final_score
	coin_l.text = "Coins: %d / %d" % [coins, total]
	restart_l.text = "Press R to Restart"
	level_complete_panel.show()

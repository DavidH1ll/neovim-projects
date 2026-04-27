extends Area2D

class_name Coin

@onready var sprite: Sprite2D = $Sprite2D
@onready var collect_sound: AudioStreamPlayer2D = $CollectSound

signal collected

func _ready() -> void:
	# Bobbing animation
	var tween := create_tween().set_loops()
	tween.tween_property(sprite, "position:y", -4, 0.5).set_trans(Tween.TRANS_SINE)
	tween.tween_property(sprite, "position:y", 4, 0.5).set_trans(Tween.TRANS_SINE)

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		collected.emit()
		if collect_sound:
			collect_sound.play()
		# Collect animation
		var tween := create_tween()
		tween.tween_property(self, "scale", Vector2(1.5, 1.5), 0.1)
		tween.tween_property(self, "modulate:a", 0.0, 0.1)
		tween.tween_callback(queue_free)

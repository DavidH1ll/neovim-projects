extends Area2D

class_name Flag

@onready var sprite: Sprite2D = $Sprite2D

signal level_complete

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		set_deferred("monitoring", false)
		level_complete.emit()

extends CharacterBody2D

class_name Player

@export var speed: float = 200.0
@export var jump_velocity: float = -400.0
@export var gravity: float = 980.0
@export var max_health: int = 3

@onready var sprite: Sprite2D = $Sprite2D
@onready var jump_sound: AudioStreamPlayer2D = $JumpSound
@onready var hurt_sound: AudioStreamPlayer2D = $HurtSound

var health: int
var is_dead: bool = false
var facing_right: bool = true
var invincible: bool = false

signal health_changed(new_health: int)
signal died

func _ready() -> void:
	health = max_health

func _physics_process(delta: float) -> void:
	if is_dead:
		return

	# Apply gravity
	if not is_on_floor():
		velocity.y += gravity * delta

	# Jump
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_velocity
		if jump_sound:
			jump_sound.play()

	# Horizontal movement
	var direction := Input.get_axis("move_left", "move_right")
	if direction:
		velocity.x = direction * speed
		# Flip sprite
		if direction > 0 and not facing_right:
			facing_right = true
			sprite.flip_h = false
		elif direction < 0 and facing_right:
			facing_right = false
			sprite.flip_h = true
		# Use idle sprite when running (could add run animation)
		sprite.texture = preload("res://assets/player/player_idle.png")
	else:
		velocity.x = move_toward(velocity.x, 0, speed)
		sprite.texture = preload("res://assets/player/player_idle.png")

	# Use jump sprite when in air
	if not is_on_floor():
		sprite.texture = preload("res://assets/player/player_jump.png")

	move_and_slide()

func take_damage(amount: int = 1) -> void:
	if is_dead or invincible:
		return

	health -= amount
	health_changed.emit(health)

	if hurt_sound:
		hurt_sound.play()

	# Knockback
	velocity.y = -200
	velocity.x = -velocity.x * 0.5

	if health <= 0:
		die()
	else:
		# Brief invincibility
		invincible = true
		sprite.modulate = Color(1, 0.3, 0.3, 0.7)
		await get_tree().create_timer(1.0).timeout
		invincible = false
		sprite.modulate = Color(1, 1, 1, 1)

func die() -> void:
	is_dead = true
	died.emit()
	# Death animation: fall off screen
	velocity = Vector2(0, -300)
	var tween := create_tween()
	tween.tween_property(self, "rotation", PI, 0.5)
	tween.tween_property(self, "modulate:a", 0.0, 0.5)

func heal(amount: int = 1) -> void:
	health = mini(health + amount, max_health)
	health_changed.emit(health)

func add_score(amount: int) -> void:
	# Score is handled by GameManager via signals
	pass

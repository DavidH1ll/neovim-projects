extends Node2D

## Procedural level generator for the platformer.
## Places floor, platforms, coins, spikes, and flag based on player jump metrics.

const TILE_SIZE := 32
const GROUND_Y_TILES := 18
const LEVEL_WIDTH_TILES := 64

const TILE_SOURCE_GROUND := 0
const TILE_SOURCE_MID := 1
const TILE_SOURCE_PLATFORM := 2

@export var jump_velocity: float = -400.0
@export var gravity: float = 980.0

@onready var tilemap: TileMap = $TileMap
@onready var ground_y_px: float = GROUND_Y_TILES * TILE_SIZE

var coin_scene: PackedScene = preload("res://scenes/coin.tscn")
var spike_scene: PackedScene = preload("res://scenes/spike.tscn")
var flag_scene: PackedScene = preload("res://scenes/flag.tscn")


func _ready() -> void:
	generate_platforms()
	place_spikes()
	place_coins()
	place_flag()


func get_max_jump_height() -> float:
	"""Calculate maximum vertical reach from velocity and gravity.
	v^2 = u^2 + 2*a*s  =>  s = u^2 / (2*|a|)  at apex where v=0
	"""
	return (jump_velocity * jump_velocity) / (2.0 * gravity)


func generate_platforms() -> void:
	"""Place platforms in a reachable parabolic arc.
	Each step is 2 tiles (64 px) vertically -- well within the ~82 px jump ceiling.
	"""
	var platform_rows: Array[int] = [16, 14, 12, 10, 8, 10, 14, 16]
	var platform_x_starts: Array[int] = [8, 14, 20, 26, 32, 38, 44, 50]
	var lengths: Array[int] = [4, 3, 3, 4, 3, 3, 4, 4]

	for i in range(platform_rows.size()):
		var py: int = platform_rows[i]
		var px: int = platform_x_starts[i]
		for dx in range(lengths[i]):
			tilemap.set_cell(0, Vector2i(px + dx, py), TILE_SOURCE_PLATFORM, Vector2i(0, 0))


func place_spikes() -> void:
	"""Snap spikes to the ground surface so their sprite base aligns with y=576."""
	var spike_tile_xs := [5, 12, 19, 28, 36, 46, 55, 61]
	for tx in spike_tile_xs:
		var spike := spike_scene.instantiate() as Node2D
		# Sprite2D is 32x32 centered; bottom edge = y + 16
		spike.position = Vector2(tx * TILE_SIZE + TILE_SIZE / 2.0, ground_y_px - 16.0)
		spike.z_index = 1
		add_child(spike)


func place_coins() -> void:
	"""Place coins in a parabolic arc reachable from platforms and ground jumps."""
	var max_height := get_max_jump_height()
	var num_coins := 16
	var start_tile_x := 6
	var end_tile_x := LEVEL_WIDTH_TILES - 4

	for i in range(num_coins):
		var t := float(i) / float(num_coins - 1)
		var px := lerpf(start_tile_x * TILE_SIZE + 16.0, end_tile_x * TILE_SIZE + 16.0, t)

		# Parabolic height profile: rises to apex then falls
		var arc_ratio := sin(t * PI)
		# Coins peak at ~60 % of theoretical max so they're comfortably reachable
		var height_offset := arc_ratio * max_height * 0.60

		# Base y: start above ground, rise, then return to ground level
		var py := ground_y_px - 40.0 - height_offset

		var coin := coin_scene.instantiate() as Node2D
		coin.position = Vector2(px, py)
		coin.z_index = 1
		add_child(coin)

	# Bonus: place a coin on top of each platform
	var platform_rows_top: Array[int] = [16, 14, 12, 10, 8, 10, 14, 16]
	var platform_x_centers: Array[int] = [10, 16, 22, 28, 34, 40, 46, 52]
	for i in range(platform_rows_top.size()):
		var py: float = platform_rows_top[i] * TILE_SIZE - 18.0  # slightly above platform surface
		var px: float = platform_x_centers[i] * TILE_SIZE + TILE_SIZE / 2.0
		var coin := coin_scene.instantiate() as Node2D
		coin.position = Vector2(px, py)
		coin.z_index = 1
		add_child(coin)


func place_flag() -> void:
	"""Place finish flag at the far right, snapped to ground surface."""
	var flag := flag_scene.instantiate() as Node2D
	# Sprite is 32x32 centered; bottom edge = y + 16
	flag.position = Vector2((LEVEL_WIDTH_TILES - 3) * TILE_SIZE, ground_y_px - 16.0)
	flag.z_index = 1
	add_child(flag)

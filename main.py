import sys, pygame, math
from pygame import gfxdraw

version = "0.0.1"

pygame.init()


# Global Variables and Constants
pi = math.pi

fov = pi / 3
resolution = 8 # ray spacing (to reduce lag)
angle_float_precision = 3 # Balances out the amount of memoized ray tangents
tan_dir_array = []

for i in range(math.ceil(pi*2 * (10 ** angle_float_precision))): # Memoize all possible ray tangents
	tan_dir_array.append(round(math.tan(i * 10 ** -angle_float_precision), 3))

print(len(tan_dir_array))

map = [
	[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
	[1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
	[1, 0, 1, 0, 0, 1, 0, 0, 0, 1],
	[1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

## Block defs
passable_blocks = [0]

dimensions = (len(map[0]), len(map))

block_size = 64
#screen_dimensions = (len(map[0]) * block_size, len(map) * block_size)
screen_dimensions = (800, 600)

player = {
	"x": dimensions[0]/2, 
	"y": dimensions[1]/2,
	"direction": 0,			# Radians
	"forward_vel": 0,		# Pixels per frame
}

movement_speed = 0.002
turn_speed = 0.003

w_down = a_down = s_down = d_down = left_down = right_down = False



screen = pygame.display.set_mode(screen_dimensions, pygame.RESIZABLE)
pygame.display.set_caption("Raycaster Test v" + version)


def do_keys(key, val):
	global w_down, a_down, s_down, d_down, left_down, right_down
	match key:
		case pygame.K_w:
			w_down = val
		case pygame.K_a:
			a_down = val
		case pygame.K_s:
			s_down = val
		case pygame.K_d:
			d_down = val
		case pygame.K_LEFT:
			left_down = val
		case pygame.K_RIGHT:
			right_down = val
		case pygame.K_q:
			if val:
				print(len(tan_dir_array)) # test

def check_collision(x, y):
	return map[int(y)][int(x)] in passable_blocks

def move_player():
	[test_x, test_y] = [player["x"], player["y"]]
	if left_down:
		player["direction"] -= turn_speed
	if right_down:
		player["direction"] += turn_speed
	player["direction"] += pi * 2
	player["direction"] %= pi * 2

	if w_down:
		test_x += math.cos(player["direction"]) * movement_speed
		test_y += math.sin(player["direction"]) * movement_speed
	if a_down:
		test_x += math.cos(player["direction"] + pi/2) * -movement_speed
		test_y += math.sin(player["direction"] + pi/2) * -movement_speed
	if s_down:
		test_x += math.cos(player["direction"]) * -movement_speed
		test_y += math.sin(player["direction"]) * -movement_speed
	if d_down:
		test_x += math.cos(player["direction"] + pi/2) * movement_speed
		test_y += math.sin(player["direction"] + pi/2) * movement_speed

	if check_collision(test_x, player["y"]):
		player["x"] = test_x
	if check_collision(player["x"], test_y):
		player["y"] = test_y


def draw_map():
	for y_block in range(len(map)):
		for x_block in range(len(map[y_block])):
			if (map[y_block][x_block]) == 1:
				gfxdraw.box(screen, pygame.Rect(x_block*block_size, y_block*block_size, block_size, block_size), (100, 0, 0))

def draw_player():
	gfxdraw.filled_circle(screen, int(player["x"] * block_size), int(player["y"] * block_size), int(block_size / 8), (0, 100, 0))
	gfxdraw.line(screen, int(player["x"] * block_size), int(player["y"] * block_size), int(player["x"] * block_size + math.cos(player["direction"])*20), int(player["y"] * block_size + math.sin(player["direction"])*20), (255, 255, 255))

def cast_rays(dir, bubble):
	ray_x = 0
	ray_y = 0
	ray_xjump = 0
	ray_yjump = 0
	rl_dist = 1000
	ud_dist = 1000
	tan_dir = tan_dir_array[int(dir * 10 ** angle_float_precision)] # Reference the tangent memo
	try:
		if dir < pi/2 or dir > pi*1.5: #rightward
			ray_x = math.ceil(player["x"])
			ray_xjump = 1
			ray_y = tan_dir * (ray_x - player["x"]) + player["y"]
			ray_yjump = tan_dir * (ray_xjump)
			while map[math.floor(ray_y)][math.floor(ray_x)] in passable_blocks:
				ray_x += ray_xjump
				ray_y += ray_yjump
		elif dir + pi/2 > pi: #leftward
			ray_x = math.floor(player["x"])
			ray_xjump = -1
			ray_y = tan_dir * (ray_x - player["x"]) + player["y"]
			ray_yjump = tan_dir * (ray_xjump)
			while map[math.floor(ray_y)][math.floor(ray_x) - 1] in passable_blocks:
				ray_x += ray_xjump
				ray_y += ray_yjump
#		gfxdraw.line(screen, int(player["x"] * block_size), int(player["y"] * block_size), int(ray_x * block_size), int(ray_y * block_size), (255, 255, 255))
		rl_dist = (ray_x - player["x"]) ** 2 + (ray_y - player["y"]) ** 2
	except:
		pass

	try:
		if dir < pi: #upward
			ray_y = math.ceil(player["y"])
			ray_x = (ray_y - player["y"]) / tan_dir + player["x"]
			ray_yjump = 1
			ray_xjump = (ray_yjump) / tan_dir
			while map[math.floor(ray_y)][math.floor(ray_x)] in passable_blocks:
				ray_x += ray_xjump
				ray_y += ray_yjump
		elif dir > pi: #downward
			ray_y = math.floor(player["y"])
			ray_x = (ray_y - player["y"]) / tan_dir + player["x"]
			ray_yjump = -1
			ray_xjump = (ray_yjump) / tan_dir
			while map[math.floor(ray_y) - 1][math.floor(ray_x)] in passable_blocks:
				ray_x += ray_xjump
				ray_y += ray_yjump
#		gfxdraw.line(screen, int(player["x"] * block_size), int(player["y"] * block_size), int(ray_x * block_size), int(ray_y * block_size), (0, 255, 0))
		ud_dist = (ray_x - player["x"]) ** 2 + (ray_y - player["y"]) ** 2
	except:
		pass
	return [math.sqrt(min(rl_dist, ud_dist)) * bubble, min(rl_dist, ud_dist) == rl_dist]

def draw_verticals(rays):
	for ray in range(len(rays)):
		[dist, is_left] = rays[ray]
		dist += 0.05 # we don't want any dist values equal to or too close to 0
		block_height = screen_dimensions[0]/dist
		gfxdraw.box(screen, pygame.Rect(ray * resolution, int(screen_dimensions[1]/2 - block_height/2), resolution, block_height), (0, 0, 255) if is_left else (64, 64, 255))


def draw():
	global screen_dimensions
	screen_dimensions = pygame.display.get_window_size()
	screen.fill((128, 128, 200))
	gfxdraw.box(screen, pygame.Rect(0, screen_dimensions[1]/2, screen_dimensions[0], screen_dimensions[1]/2), (230, 230, 230))
#	draw_map()
#	draw_player()
	num_rays = screen_dimensions[0] / resolution
	ray_angle_step = fov / num_rays
	i = -fov/2
	ray_lengths = []
	while i < fov/2:
		angle = round((player["direction"] + i + pi * 2) % (pi * 2), angle_float_precision)
		new_ray = cast_rays(angle, math.cos(i))
		ray_lengths.append(new_ray)
		i += ray_angle_step
	draw_verticals(ray_lengths)
	pygame.display.flip()


while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
		elif event.type == pygame.KEYDOWN:
			do_keys(event.key, True)
		elif event.type == pygame.KEYUP:
			do_keys(event.key, False)
	move_player()
	draw()

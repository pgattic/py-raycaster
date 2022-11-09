import sys, pygame, math
from pygame import gfxdraw

version = "0.1.4"

# Global Variables and Constants
pi = math.pi

fov = pi / 3
resolution = 1 # ray spacing (to reduce lag)


angle_float_precision = 3 # Decimal places precision to memoize tangent to. lower number = lower precision but smaller array
tan_float_precision = 3
tan_dir_array = []

for i in range(math.ceil(pi*2 * (10 ** angle_float_precision))): # Memoize all possible ray tangents
	tan_dir_array.append(round(math.tan(i * 10 ** -angle_float_precision), tan_float_precision))

map = [
	[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0, 7, 0, 8, 0, 1],
	[1, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

## Block defs
passable_blocks = [0]
color_defs = [
	[0, 0, 0],
	[0, 0, 1],
	[0, .70, 0.5],
	[120, .70, 0.5],
	[240, .70, 0.5],
	[60, .70, 0.5],
	[180, .40, 0.5],
	[300, .70, 0.5],
	[32, .70, 0.5],
]

dimensions = (len(map[0]), len(map))

block_size = 64
#screen_dimensions = (len(map[0]) * block_size, len(map) * block_size)
screen_dimensions = (800, 600)

player = {
	"x": 1.5, 
	"y": 14.5,
	"direction": pi/2 * 3,			# Radians
	"forward_vel": 0,		# Pixels per frame
}

movement_speed = 0.05
turn_speed = 0.05

w_down = a_down = s_down = d_down = left_down = right_down = False
transparency = True


pygame.init()

game_clock = pygame.time.Clock()
delta = 0
screen = pygame.display.set_mode(screen_dimensions, pygame.RESIZABLE)
pygame.display.set_caption("Raycaster Test v" + version)

def hsla2rgba(hsla):
	[h, s, l, a] = hsla
	rn = gn = bn = 0
	c = (1 - abs(2 * l - 1)) * s
	x = c * (1 - abs((h / 60) % 2 - 1))
	m = l - c/2
	if h < 60:  [rn, gn, bn] = [c, x, 0]
	elif h < 120: [rn, gn, bn] = [x, c, 0]
	elif h < 180: [rn, gn, bn] = [0, c, x]
	elif h < 240: [rn, gn, bn] = [0, x, c]
	elif h < 300: [rn, gn, bn] = [x, 0, c]
	elif h < 360: [rn, gn, bn] = [c, 0, x]
	return [(rn + m)*255, (gn+m) * 255, (bn + m) * 255, a * 255]



def do_keys(key, val):
	global w_down, a_down, s_down, d_down, left_down, right_down, fov, transparency
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
			if val: transparency = not transparency
		case pygame.K_EQUALS:
			if val: fov += pi/12
		case pygame.K_MINUS:
			if val: fov -= pi/12
		case pygame.K_ESCAPE:
			if val:
				pygame.quit()
				sys.exit()

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

def cast_rays(x, y, dir, bubble):
	ray_x = 0
	ray_y = 0
	ray_xjump = 0
	ray_yjump = 0
	rl_dist = 1000
	ud_dist = 1000
	tan_dir = tan_dir_array[int(dir * 10 ** angle_float_precision)] # Reference the tangent memo instead of calculating the tangent on the fly
	block_type1 = 0
	block_type2 = 0
	end_coords1 = []
	end_coords2 = []
	try:
		if dir < pi/2 or dir > pi*1.5: #rightward
			ray_x = math.ceil(x)
			ray_xjump = 1
			ray_y = tan_dir * (ray_x - x) + y
			ray_yjump = tan_dir * (ray_xjump)
			while map[math.floor(ray_y)][math.floor(ray_x)] in passable_blocks:
				ray_x += ray_xjump
				ray_y += ray_yjump
			block_type1 = map[math.floor(ray_y)][math.floor(ray_x)]
			end_coords1 = [ray_x+0.01, ray_y]
		elif dir + pi/2 > pi: #leftward
			ray_x = math.floor(x)
			ray_xjump = -1
			ray_y = tan_dir * (ray_x - x) + y
			ray_yjump = tan_dir * (ray_xjump)
			while map[math.floor(ray_y)][math.floor(ray_x) - 1] in passable_blocks:
				ray_x += ray_xjump
				ray_y += ray_yjump
			block_type1 = map[math.floor(ray_y)][math.floor(ray_x) - 1]
			end_coords1 = [ray_x-0.01, ray_y]
#		gfxdraw.line(screen, int(player["x"] * block_size), int(player["y"] * block_size), int(ray_x * block_size), int(ray_y * block_size), (255, 255, 255))
		rl_dist = (ray_x - player["x"]) ** 2 + (ray_y - player["y"]) ** 2
	except:
		pass

	try:
		if dir < pi: #upward
			ray_y = math.ceil(y)
			ray_x = (ray_y - y) / tan_dir + x
			ray_yjump = 1
			ray_xjump = (ray_yjump) / tan_dir
			while map[math.floor(ray_y)][math.floor(ray_x)] in passable_blocks:
				ray_x += ray_xjump
				ray_y += ray_yjump
			block_type2 = map[math.floor(ray_y)][math.floor(ray_x)]
			end_coords2 = [ray_x, ray_y+0.01]
		elif dir > pi: #downward
			ray_y = math.floor(y)
			ray_x = (ray_y - y) / tan_dir + x
			ray_yjump = -1
			ray_xjump = (ray_yjump) / tan_dir
			while map[math.floor(ray_y) - 1][math.floor(ray_x)] in passable_blocks:
				ray_x += ray_xjump
				ray_y += ray_yjump
			block_type2 = map[math.floor(ray_y) - 1][math.floor(ray_x)]
			end_coords2 = [ray_x, ray_y-0.01]
#		gfxdraw.line(screen, int(player["x"] * block_size), int(player["y"] * block_size), int(ray_x * block_size), int(ray_y * block_size), (0, 255, 0))
		ud_dist = (ray_x - player["x"]) ** 2 + (ray_y - player["y"]) ** 2
	except:
		pass
	minimum = min(rl_dist, ud_dist)
	end_type = 0
	end_coords = []
	if minimum == rl_dist:
		is_rl = True
		end_type = block_type1
		end_coords = end_coords1
	else:
		is_rl = False
		end_type = block_type2
		end_coords = end_coords2
	return [math.sqrt(minimum) * bubble, is_rl, end_type, end_coords]

def draw_verticals(rays):		# Draws the vertical "bars" onto the screen based on the ray distances (with some fancy color manipulation to simulate distance)
	for ray in range(len(rays)):
		[dist, is_left, block_type, coords, index] = rays[ray]
		dist += 0.05 # we don't want any dist values equal to or too close to 0
		block_height = screen_dimensions[0]/dist * ((pi/3)/fov)
		darkness = (0.55 if is_left else 0.65) - dist / 100
		color = list(color_defs[block_type])
		color.insert(2, darkness)
		display_color = hsla2rgba(color)
		if not transparency: display_color.pop()
		gfxdraw.box(screen, pygame.Rect(index * resolution, int(screen_dimensions[1]/2 - block_height/2), resolution, block_height), display_color)


def draw():
	global screen_dimensions
	screen_dimensions = pygame.display.get_window_size()
	screen.fill((135, 206, 235))
	gfxdraw.box(screen, pygame.Rect(0, screen_dimensions[1]/2, screen_dimensions[0], screen_dimensions[1]/2), (238, 238, 238))
#	draw_map()
#	draw_player()
	num_rays = math.ceil(screen_dimensions[0] / resolution)
	ray_angle_step = fov / num_rays
	i = -fov/2
	ray_lengths = []
	for i in range(num_rays):
		relative_angle = (i/num_rays) * fov - fov/2
		angle = (player["direction"] + relative_angle + pi * 2) % (pi * 2)
		new_ray = cast_rays(player["x"], player["y"], angle, math.cos(relative_angle))
		new_ray.append(i)
		ray_lengths.insert(0, new_ray)
		while transparency and color_defs[new_ray[2]][2] < 1:
			new_ray_test = cast_rays(new_ray[3][0], new_ray[3][1], angle, math.cos(relative_angle))
			if new_ray_test[2] != new_ray[2]:
				new_ray_test.append(i)
				ray_lengths.insert(0, new_ray_test)
			new_ray = new_ray_test
	draw_verticals(ray_lengths)

	# crosshair
	gfxdraw.box(screen, pygame.Rect(screen_dimensions[0] / 2 - 1, screen_dimensions[1] / 2 - 8, 2, 16), (255, 255, 255))
	gfxdraw.box(screen, pygame.Rect(screen_dimensions[0] / 2 - 8, screen_dimensions[1] / 2 - 1, 16, 2), (255, 255, 255))

	pygame.display.flip()

def main():
	while 1:
		delta = game_clock.tick(60)
		fps = game_clock.get_fps()
		pygame.display.set_caption(f"Raycaster Test v{version} - FPS: {math.floor(fps)} - FOV: {round(fov/pi*180)}")
		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit()
			elif event.type == pygame.KEYDOWN:
				do_keys(event.key, True)
			elif event.type == pygame.KEYUP:
				do_keys(event.key, False)
		move_player()
		draw()

if __name__ == "__main__":
	main()

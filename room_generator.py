#room_generator.py

import maya.cmds as cmds
from collections import namedtuple
import functools

door_infos = []
option_menu_l = []
width_l = []
height_l = []
position_l = []
door_infos = []
DoorInfo = namedtuple("DoorInfo", "side position width height")
WindowInfo = namedtuple("WindowInfo", "side position_x position_y width height")

def create_ui(window_title, apply_callback):
	win_id = window_title + '_id' 
	if cmds.window(win_id, exists=True):
		cmds.deleteUI(win_id)
	
	def add_door(*pArgs):
		global rows
		rows  += 1
		update_row()
	
	def remove_door(index, *pArgs):
		global rows
		rows  -= 1
		option_menu_l.pop(index)
		width_l.pop(index)
		height_l.pop(index)
		position_l.pop(index)
		door_infos.pop(index)
		update_row()
	
	def apply(*pArgs):
		update_row()
		apply_callback(floor_ceiling, walls, option_menu_l, width_l, height_l, position_l, door_infos)
	
	global rows
	global option_menu_l
	global width_l
	global height_l
	global position_l
	global door_infos
	
	rows = 0
	option_menu_l = []
	width_l = []
	height_l = []
	position_l = []
	door_infos = []
	
	w = cmds.window()  
	c = cmds.columnLayout(adj=True)
	
	floor_ceiling = cmds.checkBoxGrp( numberOfCheckBoxes=2, labelArray2=['Floor', 'Ceiling'], value1=True, value2=True )
	walls = cmds.checkBoxGrp( numberOfCheckBoxes=4, labelArray4=['North', 'South', 'East', 'West'], value1=True, value2=True, value3=True, value4=True )
	cmds.button(label='Create', command=apply)													  
	cmds.button(label='Add Door', command=add_door)
	
	scroll = cmds.scrollLayout()
	form = cmds.formLayout()
	
	def update_row(*_):
		global rows
		global option_menu_l
		global width_l
		global height_l
		global position_l
		
		global door_infos
		door_infos = []

		for i in range(len(option_menu_l)):
			side = cmds.optionMenu(option_menu_l[i], query=True, value=True)
			position = cmds.floatSlider(position_l[i], query=True, value=True)
			width = cmds.floatField(width_l[i], query=True, value=True)
			height = cmds.floatField(height_l[i], query=True, value=True)
			door_infos.append(DoorInfo(side=side, position=position, width=width, height=height))
			
		option_menu_l = []
		width_l = []
		height_l = []
		position_l = []
		
		columns = 8
		
		for n in cmds.formLayout(form, q=True, ca=True) or []:
			cmds.deleteUI(n)
		cmds.setParent(form)		
		
		new_row = cmds.rowColumnLayout(nc = columns)
		for r in range(rows):
			val = door_infos[r].side if r < len(door_infos) else 'North'
			if val == 'North':
				val = 1
			elif val == 'South':
				val = 2
			elif val == 'East':
				val = 3
			else:
				val = 4			
			side_menu = cmds.optionMenu(label='Position')			
			cmds.menuItem( label='North')
			cmds.menuItem( label='South')
			cmds.menuItem( label='East')
			cmds.menuItem( label='West')
			cmds.optionMenu(side_menu, e=True, select=val)
			option_menu_l.append(side_menu)
			cmds.text(label='Width:')
			width_ctr = cmds.floatField()
			val = door_infos[r].width if r < len(door_infos) else 1
			cmds.floatField(width_ctr, e=True, value=val)
			width_l.append(width_ctr)
			cmds.text(label='Height:')
			height_ctr = cmds.floatField()
			val = door_infos[r].height if r < len(door_infos) else 1
			cmds.floatField(height_ctr, e=True, value=val)
			height_l.append(height_ctr)
			cmds.text(label='Relative Position:')
			position_ctr = cmds.floatSlider(min=-1, max=1, value=0, step=0.01)
			val = door_infos[r].position if r < len(door_infos) else 0
			cmds.floatSlider(position_ctr, e=True, value=val)
			position_l.append(position_ctr)
			cmds.button(label='X', command=functools.partial(remove_door, r))
			
		cmds.formLayout(form, e=True, af = [(new_row,'top',0), (new_row, 'bottom', 0 ), (new_row,  'left', 0 ), (new_row, 'right', 0)])
   
	update_row()
	cmds.showWindow(w)

def generate_walls(volume_t, wall_mask, wall_width, door_infos, room_grp):
	
	p_room_x = cmds.getAttr('%s.translateX' % (volume_t))
	p_room_y = cmds.getAttr('%s.translateY' % (volume_t))
	p_room_z = cmds.getAttr('%s.translateZ' % (volume_t))
	
	r_room_x = cmds.getAttr('%s.rotateX' % (volume_t))
	r_room_y = cmds.getAttr('%s.rotateY' % (volume_t))
	r_room_z = cmds.getAttr('%s.rotateZ' % (volume_t))
	
	s_room_x = cmds.getAttr('%s.scaleX' % (volume_t))
	s_room_y = cmds.getAttr('%s.scaleY' % (volume_t))
	s_room_z = cmds.getAttr('%s.scaleZ' % (volume_t))
	
	if wall_mask[0]:
		floor = cmds.polyCube(w=s_room_x, h=wall_width, d=s_room_z, name='floor_room_#')
		cmds.move(p_room_x, p_room_y - (s_room_y*0.5) + (wall_width*0.5), p_room_z, floor)
		cmds.parent(floor, room_grp)
	if wall_mask[1]:
		ceiling = cmds.polyCube(w=s_room_x, h=wall_width, d=s_room_z, name='ceiling_room_#')
		cmds.move(p_room_x, p_room_y + (s_room_y*0.5) - (wall_width*0.5), p_room_z, ceiling)
		cmds.parent(ceiling, room_grp)
	if wall_mask[2]:
		wall_n = cmds.polyCube(w=s_room_x, h=s_room_y - (wall_width*2), d=wall_width, name='wallN_room_#')
		cmds.move(p_room_x, p_room_y, p_room_z + (s_room_z*0.5) - (wall_width*0.5), wall_n)
		cmds.parent(wall_n, room_grp)
	if wall_mask[3]:
		wall_s = cmds.polyCube(w=s_room_x, h=s_room_y - (wall_width*2), d=wall_width, name='wallS_room_#')
		cmds.move(p_room_x, p_room_y, p_room_z - (s_room_z*0.5) + (wall_width*0.5), wall_s)
		cmds.parent(wall_s, room_grp)
	if wall_mask[4]:
		wall_e = cmds.polyCube(w=wall_width, h=s_room_y - (wall_width*2), d=s_room_z - (wall_width*2), name='wallE_room_#')
		cmds.move(p_room_x + (s_room_x * 0.5) - (wall_width * 0.5), p_room_y, p_room_z, wall_e)
		cmds.parent(wall_e, room_grp)
	if wall_mask[5]:
		wall_w = cmds.polyCube(w=wall_width, h=s_room_y - (wall_width*2), d=s_room_z - (wall_width*2), name='wallW_room_#')
		cmds.move(p_room_x - (s_room_x * 0.5) + (wall_width * 0.5), p_room_y, p_room_z, wall_w)
		cmds.parent(wall_w, room_grp)
	
	cmds.xform(room_grp, centerPivots=True)
	
	for info in door_infos:
		#print 'generating door: ' + str(info.side)
		generate_door(room_grp,
				 [p_room_x, p_room_y, p_room_z],
				 [r_room_x, r_room_y, r_room_z],
				 [s_room_x, s_room_y, s_room_z],
				 wall_width,
				 info)
	
	cmds.rotate(r_room_x, r_room_y, r_room_z, room_grp)
	
	cmds.hide(volume_t)

def generate_door(room_grp, room_pos, room_rot, room_size, wall_width, door_info): 
	offset = room_pos
	wall_name = ''
	door_offset = door_info.width + (2 * wall_width)
	door_rot = [0,0,0]
	
	side = door_info.side
	if side == 'North':
		offset[0] += (room_size[0] - door_offset) * 0.5 * door_info.position
		offset[2] = room_pos[2] + (room_size[2]*0.5) - (wall_width*0.5)
		wall_name = filter(lambda x: 'N' in x, cmds.listRelatives(room_grp))
	elif side == 'South':
		offset[0] += (room_size[0] - door_offset) * 0.5 * door_info.position
		offset[2] = room_pos[2] - (room_size[2]*0.5) + (wall_width*0.5)
		wall_name = filter(lambda x: 'S' in x, cmds.listRelatives(room_grp))
	elif side == 'East':
		offset[2] += (room_size[2] - door_offset) * 0.5 * door_info.position
		offset[0] = room_pos[0] + (room_size[0] * 0.5) - (wall_width*0.5)
		wall_name = filter(lambda x: 'E' in x, cmds.listRelatives(room_grp))
		door_rot[1] = 90
	elif side == 'West':
		offset[2] += (room_size[2] - door_offset) * 0.5 * door_info.position
		offset[0] = room_pos[0] - (room_size[0] * 0.5) + (wall_width*0.5)
		wall_name = filter(lambda x: 'W' in x, cmds.listRelatives(room_grp))
		door_rot[1] = 90
	else:
		print 'side was: ' + side
		return
		
	wall_name_full = ''
	
	if type(wall_name) is list and len(wall_name) > 1:
		print str(len(wall_name))	
		wall_name = filter(lambda x: '_holed' in x, wall_name)
		index = 0
		lenght = 0
		
		for x in range(len(wall_name)):
			print wall_name[x]
			if len(wall_name[x]) > lenght:
				index = x
				lenght = len(wall_name[x])
				
		print str(len(wall_name))		
		print str(index)		
		wall_name_full = wall_name[index]
	else:
		wall_name_full = wall_name[0]
	
	cut_hole(wall_name_full, side, door_info.width, door_info.height,
			 room_grp, room_size, door_rot, offset, wall_width)

def generate_window((room_grp, room_pos, room_rot, room_size, wall_width, window_info):
	offset = room_pos
	wall_name = ''
	window_offset = window_info.width + (2 * wall_width)
	window_rot = [0,0,0]
	
	side = window_info.side

	if side == 'Floor':
		wall_name = filter(lambda x: 'floor' in x, cmds.listRelatives(room_grp))
		window_rot[0] = 90
	elif side == 'Ceiling':
		wall_name = filter(lambda x: 'ceiling' in x, cmds.listRelatives(room_grp))
		window_rot[0] = 90
	elif side == 'North':
		offset[0] += (room_size[0] - window_offset) * 0.5 * window_info.position_x
		offset[2] = room_pos[2] + (room_size[2]*0.5) - (wall_width*0.5)
		wall_name = filter(lambda x: 'N' in x, cmds.listRelatives(room_grp))
	elif side == 'South':
		offset[0] += (room_size[0] - window_offset) * 0.5 * window_info.position_x
		offset[2] = room_pos[2] - (room_size[2]*0.5) + (wall_width*0.5)
		wall_name = filter(lambda x: 'S' in x, cmds.listRelatives(room_grp))
	elif side == 'East':
		offset[2] += (room_size[2] - window_offset) * 0.5 * window_info.position_x
		offset[0] = room_pos[0] + (room_size[0] * 0.5) - (wall_width*0.5)
		wall_name = filter(lambda x: 'E' in x, cmds.listRelatives(room_grp))
		window_rot[1] = 90
	elif side == 'West':
		offset[2] += (room_size[2] - window_offset) * 0.5 * window_info.position_x
		offset[0] = room_pos[0] - (room_size[0] * 0.5) + (wall_width*0.5)
		wall_name = filter(lambda x: 'W' in x, cmds.listRelatives(room_grp))
		window_rot[1] = 90
	else:
		#print 'side was: ' + side
		return
		
	wall_name_full = ''
	
	if type(wall_name) is list and len(wall_name) > 1:
		#print str(len(wall_name))	
		wall_name = filter(lambda x: '_holed' in x, wall_name)
		index = 0
		lenght = 0
		
		for x in range(len(wall_name)):
			#print wall_name[x]
			if len(wall_name[x]) > lenght:
				index = x
				lenght = len(wall_name[x])
				
		#print str(len(wall_name))		
		#print str(index)		
		wall_name_full = wall_name[index]
	else:
		wall_name_full = wall_name[0]
	
	cut_hole(wall_name_full, side, window_info.width, window_info.height,
			 room_grp, room_size, window_rot, offset, wall_width)

def cut_hole(wall_name_full, side, width, height, room_grp, room_size, rot, offset, wall_width):
	hole = cmds.polyCube(w=width, h=height, d=(wall_width + 0.1), name=room_grp + '_hole_%s_#' % (side))
	cmds.xform(hole, centerPivots=True)
	cmds.rotate(rot[0], rot[1], rot[2], hole)
	cmds.move(offset[0], offset[1] - (room_size[1]*0.5) + (height*0.5), offset[2], hole)
	cmds.parent(hole, room_grp, relative=False)
	cutted_wall = cmds.polyBoolOp(wall_name_full, hole[0], op=2, n=wall_name_full+ '_holed')[0]
	cmds.inheritTransform(cutted_wall, off=True)
	cmds.parent(cutted_wall, room_grp)
	cmds.hide(hole)
	cmds.hide(wall_name_full)

def apply_callback(floor_ceiling, walls, option_menu_l, width_l, height_l, position_l, d_i, *pArgs):
	do_floor_ceiling = cmds.checkBoxGrp( floor_ceiling, query=True, valueArray2=True )	 
	do_walls = cmds.checkBoxGrp( walls, query=True, valueArray4=True )
	
	global door_infos
	
	s_list = cmds.ls(selection=True, type='transform')
	wall_width = 0.1
	t_name = s_list[0]
	room_grp = cmds.group(empty=True, name='grp_room_#')
	
	wall_mask = [do_floor_ceiling[0], do_floor_ceiling[1],
				 do_walls[0], do_walls[1], do_walls[2], do_walls[3]]
	
	generate_walls(t_name, wall_mask, wall_width, door_infos, room_grp)


create_ui('Room Settings', apply_callback)
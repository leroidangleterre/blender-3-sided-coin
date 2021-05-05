import bpy
import random
import fnmatch

MAX_FRAME = 400

nbRows = 12
nbCols = 12

# This is the ratio between the thickness and the diameter.
ratio = 0.1

initialAltitude = 10


altitudes_list = []


def cancel_simulation():
    bpy.ops.screen.animation_cancel()


def process_markers_coordinates():
    print("Markers coordinates:")
    for object in bpy.context.scene.objects:
        
        parent = object.parent
        if parent is not None:
            # print("Object: " + object.name + ", " + parent.name)
            if object.parent.name.startswith("Cylinder"):
                # At this point, 'object' is a marker.
                # We need to know its altitude.
                
                coords_matrix = object.parent.matrix_world * object.matrix_basis
                altitude = coords_matrix[2][3]
                # print("Z-coordinate of the marker: " + str(altitude))
                altitudes_list.append(altitude)
    # Now we extract the result for each coin (Heads, Tails, or Side) based on the altitude.
    altitudes_list.sort()
    
    print(altitudes_list)


def stop_playback(scene):
    if scene.frame_current == MAX_FRAME:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        process_markers_coordinates()



# Create a single coin of radius one and the given thickness
# Add a weightless marker on one side of the coin.
def createCoin(ratio, newX, newY):

    # Create the coin, which is a rigid body
    bpy.ops.mesh.primitive_cylinder_add()
    coin = bpy.context.active_object
    coin.scale[2] = ratio
    coin.location[0] = newX
    coin.location[1] = newY
    coin.location[2] = initialAltitude
    mat_white = bpy.data.materials.get("Mat.white")
    if coin.data.materials:
        coin.data.materials[0] = mat_white
    else:
        coin.data.materials.append(mat_white)

    #print("Coin placed at " + str(coin.location[0]) + ", " + str(coin.location[1]) + ", " + str(coin.location[2]))
    
    # Add to the rigid body sim
    bpy.ops.rigidbody.objects_add(type='ACTIVE')
    
    # Add two keyframes on the rotation to set the coin spinning
    bpy.data.scenes["Scene"].frame_current = 1
    #coin.rotation_euler[0] = 2*random.random()
    #coin.rotation_euler[1] = 2*random.random()
    #coin.rotation_euler[2] = 2*random.random()
    coin.keyframe_insert(data_path="rotation_euler", frame=1)
    coin.keyframe_insert(data_path="location", frame=1)
    coin.rigid_body.kinematic = True;
    coin.keyframe_insert(data_path="rigid_body.kinematic", frame = 1)
    
    bpy.data.scenes["Scene"].frame_current = 2
    coin.rotation_euler[0] = 2*random.random()
    coin.rotation_euler[1] = 2*random.random()
    coin.rotation_euler[2] = 2*random.random()
    coin.keyframe_insert(data_path="rotation_euler", frame=2)
    coin.rigid_body.kinematic = True;
    coin.keyframe_insert(data_path="rigid_body.kinematic", frame = 2)
    
    bpy.data.scenes["Scene"].frame_current = 3
    coin.rigid_body.kinematic = False;
    coin.keyframe_insert(data_path="rigid_body.kinematic", frame = 3)
    
    # Add the weightless marker    
    bpy.ops.mesh.primitive_cylinder_add()
    marker = bpy.context.active_object
    marker.scale[2] = 0.2/ratio
    marker.location[0] = 0
    marker.location[1] = 0
    marker.location[2] = marker.dimensions[2]/2
    mat_red = bpy.data.materials.get("Mat.red")
    if marker.data.materials:
        marker.data.materials[0] = mat_red
    else:
        marker.data.materials.append(mat_red)
    
    marker.parent = coin



print("Start")
nbCoinsCreated = 0
for line in range(nbRows):
    
    print("Placing row " + str(line) + "/" + str(nbRows))
    for col in range(nbCols):
        x = (line - nbRows/2) * 3
        y = (col - nbCols/2) * 3
        # print("nb coins created: "+str(nbCoinsCreated+1))
        createCoin(ratio, x, y)
        nbCoinsCreated = nbCoinsCreated + 1
print("End")

# Clear the previous animation-stopping handlers:
bpy.app.handlers.frame_change_pre.clear()

# The animation must be stopped after n steps:
bpy.app.handlers.frame_change_pre.append(stop_playback)

# Launch the simulation !
bpy.data.scenes["Scene"].frame_current = 1
bpy.ops.screen.animation_play()

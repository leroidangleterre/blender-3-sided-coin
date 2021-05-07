import bpy
import random
import fnmatch
import math





class CoinGenerator:

    altitudes_list = []

    coordinates_already_processed = False

    coin_thickness = 0
    coin_radius = 0
    marker_length = 0
    
    nb_heads = 0
    nb_tails = 0
    nb_sides = 0
    nb_unknown = 0
    
    
    
    def find_closest_value(value, list):
        best_candidate = 1000 # TODO: replace thiat with MAX something ?
        error = abs(best_candidate - value)
        for x in list:
            new_error = abs(x-value)
            if(new_error < error):
                # found a better candidate
                best_candidate = x
                error = new_error
        return best_candidate



    # Find which altitudes correspond to heads or tails or side,
    # and how many occurrences we have of each.
    def count_heads_tails_sides(self):
        
        print("count_heads_tails_sides: Analysing coin toss")
        #print("Test values: " + str(coin_thickness) + ", " + str(coin_radius) + ", " + str(marker_length))
        
        
        # Compute the theoretical altitudes of the marker in case of HEADS, TAILS, or SIDES:
        # HEADS: marker up
        altitude_heads = self.coin_thickness + self.marker_length
        # TAILS: marker down
        altitude_tails = -self.marker_length
        # SIDES: marker horizontal
        altitude_sides = self.coin_radius
        
        theoretical_altitudes = [altitude_heads, altitude_tails, altitude_sides]
        
        # print("List:")
        # print(self.altitudes_list)
        # print("Theoretical altitudes: " + str(altitude_heads) + ", " + str(altitude_sides) + ", " + str(altitude_tails))
        
        # Associate to each altitude the coin value (H, T, S) that corresponds to the closest theoretical altitude.
        for current_altitude in self.altitudes_list:
            estimated_altitude = CoinGenerator.find_closest_value(current_altitude, theoretical_altitudes)
            error = abs(estimated_altitude - current_altitude)
            # print("estimated altitude: " + str(estimated_altitude) + ", " + str(current_altitude) + ", error: " + str(error))
            
            max_error = abs(altitude_heads - altitude_sides)/10
            if error <= max_error:
                # Increment the corresponding count:
                if estimated_altitude == altitude_heads:
                    self.nb_heads += 1
                if estimated_altitude == altitude_sides:
                    self.nb_sides += 1
                if estimated_altitude == altitude_tails:
                    self.nb_tails += 1
            else:
                self.nb_unknown += 1
        
        # DISPLAY FINAL RESULTS
        print(str(self.nb_heads + self.nb_sides + self.nb_tails + self.nb_unknown) + " coins tossed; thickness: " + str(self.coin_thickness) + ", " + str(self.nb_heads) + " H; " + str(self.nb_tails) + " T; " + str(self.nb_sides) + " S; " + str(self.nb_unknown) + " unknown.")
            
            


    def process_markers_coordinates(self):
        if not self.coordinates_already_processed:
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
                        self.altitudes_list.append(altitude)
            # Now we extract the result for each coin (Heads, Tails, or Side) based on the altitude.
            self.altitudes_list.sort()
            
            CoinGenerator.count_heads_tails_sides(self)
            
        else:
            print("already processed the coordinates")




    # Create a single coin of radius one and the given thickness
    # Add a weightless marker on one side of the coin.
    def createCoin(self, ratio, newX, newY):

        # Create the coin, which is a rigid body
        bpy.ops.mesh.primitive_cylinder_add()
        coin = bpy.context.active_object
        
        # Coins with a small ratio must be enlarged, otherwise they get too thin and go through the ground.
        # Gravity must be adapted.
        if(ratio >= 1):
            coin.scale[2] = ratio
            bpy.data.scenes["Scene"].gravity[2] = -9.81
        else:
            coin.scale[0] = 1/ratio
            coin.scale[1] = 1/ratio
            bpy.data.scenes["Scene"].gravity[2] = -20
        
        # Apply the scale of the coin
        bpy.ops.object.transform_apply(scale=True)
            
        coin.location[0] = newX
        coin.location[1] = newY
        coin.location[2] = initialAltitude
        mat_white = bpy.data.materials.get("Mat.white")
        if coin.data.materials:
            coin.data.materials[0] = mat_white
        else:
            coin.data.materials.append(mat_white)
        
        # Add to the rigid body sim
        try:
            bpy.ops.rigidbody.objects_add(type='ACTIVE')
            coin.rigid_body.friction = 0.001
        except:
            print("Cannot add rigid body sim")
        
        # Add two keyframes on the rotation to set the coin spinning
        bpy.data.scenes["Scene"].frame_current = 1
        coin.rotation_euler[0] = 0
        coin.rotation_euler[1] = 0
        coin.rotation_euler[2] = 0
        coin.keyframe_insert(data_path="rotation_euler", frame=1)
        #coin.keyframe_insert(data_path="location", frame=1)
        coin.rigid_body.kinematic = True;
        coin.keyframe_insert(data_path="rigid_body.kinematic", frame = 1)
        
        bpy.data.scenes["Scene"].frame_current = 2
        init_rotation_factor = 0.3
        coin.rotation_euler[0] = init_rotation_factor * random.random()
        coin.rotation_euler[1] = init_rotation_factor * random.random()
        coin.keyframe_insert(data_path="rotation_euler", frame=2)
        coin.rigid_body.kinematic = True;
        coin.keyframe_insert(data_path="rigid_body.kinematic", frame = 2)
        
        bpy.data.scenes["Scene"].frame_current = 3
        coin.rigid_body.kinematic = False;
        coin.keyframe_insert(data_path="rigid_body.kinematic", frame = 3)
        
        
        # Add the weightless marker    
        bpy.ops.mesh.primitive_cylinder_add()
        marker = bpy.context.active_object
        
        marker.name = "Marker." + marker.name
        
        mat_red = bpy.data.materials.get("Mat.red")
        if marker.data.materials:
            marker.data.materials[0] = mat_red
        else:
            marker.data.materials.append(mat_red)
        
        # Apply the scale of the marker
        marker.dimensions = [0.5, 0.5, 2*coin.dimensions[2]]
        bpy.ops.object.transform_apply(scale=True)
        
        # Set the coordinates of the marker, relative to the parent.
        marker.location[0] = 0
        marker.location[1] = 0
        marker.location[2] = coin.dimensions[2]/2 + marker.dimensions[2]/2
        
        # Move the origin of the marker to its tip.
        bpy.context.scene.cursor_location[0] = 0
        bpy.context.scene.cursor_location[1] = 0
        bpy.context.scene.cursor_location[2] =  coin.dimensions[2]/2 + marker.dimensions[2]
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        
        self.coin_thickness = coin.dimensions[2]
        self.coin_radius = coin.dimensions[0] / 2
        self.marker_length = marker.dimensions[2]
        
        # print("Created a coin. Thickness = " + str(self.coin_thickness) + ", radius = " + str(self.coin_radius) + ", marker length = " + str(self.marker_length))
        
        marker.parent = coin

# END CLASS COIN_GENERATOR










# MAIN PROGRAM





print("Start")


MAX_FRAME = 400

nbRows = 30
nbCols = 30

# This is the ratio between the thickness and the diameter.
ratio = .5

initialAltitude = 10
nbCoinsCreated = 0

coinGenerator = CoinGenerator()

def stop_playback(scene):
    
    if scene.frame_current == MAX_FRAME:
        bpy.ops.screen.animation_cancel(restore_frame = False)
        bpy.app.handlers.frame_change_pre.clear()
        CoinGenerator.process_markers_coordinates(coinGenerator)  
        



for line in range(nbRows):
    
    print("Placing row " + str(line) + "/" + str(nbRows))
    for col in range(nbCols):
        
        x = (line - nbRows/2) * 3
        y = (col - nbCols/2) * 3
        # print("nb coins created: "+str(nbCoinsCreated+1))
        CoinGenerator.createCoin(coinGenerator, ratio, x, y)
        nbCoinsCreated = nbCoinsCreated + 1
print("End")


# Clear the previous animation-stopping handlers:
bpy.app.handlers.frame_change_pre.clear()



# The animation must be stopped after n steps:
bpy.app.handlers.frame_change_pre.append(stop_playback)



# Launch the simulation !
bpy.data.scenes["Scene"].frame_current = 1

bpy.ops.screen.animation_play()

import math
import random
import matplotlib.pyplot as plt

# class SnowflakeLine:
#     length: int
#     left_branch: SnowflakeLine | None
#     right_branch: SnowflakeLine | None

#     p1x: int
#     p1y: int
#     p2x: int
#     p2y: int

#     def __init__(self):
#         length = 

# def generate(min_D, max_D):

def generate_snowflake_arm(
        arm_length=10.0,
        num_segments=24,
        base_branch_length=2.0,
        base_branch_probability=.8):
    """
    Generates a single snowflake arm that is perfectly symmetrical
    about the central axis. Sub‑branches become shorter and less common
    as they move outward.
    """

    segments = []
    main_points = [(0,0)]
    angle = 90  # straight upward

    # Build center spine
    for i in range(1, num_segments + 1):
        progress = i / num_segments
        seg_len = arm_length / num_segments

        prev = main_points[-1]
        dx = seg_len * math.cos(math.radians(angle))
        dy = seg_len * math.sin(math.radians(angle))
        new_pt = (prev[0] + dx, prev[1] + dy)
        main_points.append(new_pt)

        # Add main spine segment (center)
        segments.append((prev, new_pt))

    # Add symmetrical branches
    for i in range(1, num_segments):
        progress = i / num_segments

        # *Probability* decreases toward the tip
        branch_prob = base_branch_probability * (1 - progress)

        if random.random() < branch_prob:

            # *Branch length* also decreases toward the tip
            branch_length = base_branch_length * (1 - progress)

            origin = main_points[i]

            # Branch angles
            left_angle  = 90 + random.uniform(35, 65)
            right_angle = 90 - (left_angle - 90)  # perfect symmetry

            # Compute endpoints
            lx = origin[0] + branch_length * math.cos(math.radians(left_angle))
            ly = origin[1] + branch_length * math.sin(math.radians(left_angle))

            rx = origin[0] + branch_length * math.cos(math.radians(right_angle))
            ry = origin[1] + branch_length * math.sin(math.radians(right_angle))

            # Add branch segments
            segments.append((origin, (lx, ly)))
            segments.append((origin, (rx, ry)))

    return segments


# -------- VISUALIZE --------
segments = generate_snowflake_arm()

plt.figure(figsize=(5,10))
for (p1, p2) in segments:
    plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-')

plt.gca().set_aspect('equal', 'box')
plt.title("Symmetrical Snowflake Arm\n(Shorter Branches Near Tip)")
plt.show()

env = {
    "network": {
        "network_links": [
            (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0),
            (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0), (19, 0), (20, 0),

            (21, 1), (22, 1), (23, 1), (24, 1), (25, 1), (26, 1), (27, 1), (26, 2), (27, 2), (28, 2), (29, 2), (30, 2), (31, 2), (32, 2),
            (31, 3), (32, 3), (33, 3), (34, 3), (35, 3), (36, 3), (37, 3), (36, 4), (37, 4), (38, 4), (39, 4), (40, 4), (41, 4), (42, 4),
            (41, 5), (42, 5), (43, 5), (44, 5), (45, 5), (46, 5), (47, 5), (46, 6), (47, 6), (48, 6), (49, 6), (50, 6), (51, 6), (52, 6),
            (51, 7), (52, 7), (53, 7), (54, 7), (55, 7), (56, 7), (57, 7), (56, 8), (57, 8), (58, 8), (59, 8), (60, 8), (61, 8), (62, 8),
            (61, 9), (62, 9), (63, 9), (64, 9), (65, 9), (66, 9), (67, 9), (66, 10), (67, 10), (68, 10), (69, 10), (70, 10), (71, 10), (72, 10),
            (71, 11), (72, 11), (73, 11), (74, 11), (75, 11), (76, 11), (77, 11), (76, 12), (77, 12), (78, 12), (79, 12), (80, 12), (81, 12), (82, 12),
            (81, 13), (82, 13), (83, 13), (84, 13), (85, 13), (86, 13), (87, 13), (86, 14), (87, 14), (88, 14), (89, 14), (90, 14), (91, 14), (92, 14),
            (91, 15), (92, 15), (93, 15), (94, 15), (95, 15), (96, 15), (97, 15), (96, 16), (97, 16), (98, 16), (99, 16), (100, 16), (101, 16), (102, 16),
            (101, 17), (102, 17), (103, 17), (104, 17), (105, 17), (106, 17), (107, 17), (106, 18), (107, 18), (108, 18), (109, 18), (110, 18), (111, 18), (112, 18),
            (111, 19), (112, 19), (113, 19), (114, 19), (115, 19), (116, 19), (117, 19), (116, 20), (117, 20), (118, 20), (119, 20), (120, 20),

        ],
        "bandwidth_device_to_edge": 2000,
        # Consider linear relation between bandwidth and power
        "power_device_to_edge": 77.80,
        "bandwidth_edge_to_cloud": 10000,
        "power_edge_to_cloud": 30.0,


        "upload_bandwidth_device": 2000,
        "download_bandwidth_edge_device": 2000,
        "upload_bandwidth_edge_cloud": 10000,
        "download_bandwidth_cloud": 10000,
    },

    "power": {
        "powers": [
            # Raspberry Pi zero 2W
            [
                [0.2171, 0.2509, 0.2933, 0.3252, 0.3646],  # MEMORY
                [0.1432, 0.1847, 0.2157, 0.2521, 0.2942],  # BRANCH
                [0.1871, 0.2264, 0.2707, 0.3167, 0.3677],  # FMULT
                [0.1109, 0.1435, 0.1781, 0.2074, 0.2437],  # SIMD

                # Old values
                [0.0725, 0.1175, 0.1425, 0.2225, 0.2575],  # MATMUL
                [0.0935, 0.1295, 0.1510, 0.2135, 0.2415]  # DEFAULT
            ],
            # A72 cores
            [
                [0.3254, 0.4468, 0.4802, 0.5834, 0.6084, 0.6408, 0.7001, 0.7871, 0.8712, 0.9560],
                [0.1192, 0.1933, 0.2388, 0.3076, 0.3023, 0.3599, 0.4170, 0.4861, 0.5590, 0.6389],
                [0.2192, 0.3113, 0.3687, 0.4316, 0.4588, 0.5196, 0.5908, 0.6773, 0.7719, 0.8757],
                [0.2269, 0.3283, 0.3812, 0.4560, 0.4769, 0.5526, 0.6135, 0.7112, 0.8025, 0.9147],

                # Old values
                [0.316, 0.388, 0.441, 0.502, 0.560, 0.618, 0.676, 0.732, 0.794, 0.828],
                [0.214, 0.275, 0.313, 0.352, 0.393, 0.433, 0.474, 0.515, 0.556, 0.594]
            ],
            # Xeon cores
            [
                [0.6308, 0.8179, 1.0597, 1.4009, 1.8723, 2.9005, 2.7326, 3.4297, 4.6080, 4.8275, 4.5440, 5.3327, 6.4054, 6.9846, 6.9005, 9.0073, 90.073],
                [0.3266, 0.4244, 0.5702, 0.6721, 0.7790, 0.9654, 1.0632, 1.1859, 1.4400, 1.5516, 1.8208, 2.0846, 2.2540, 2.4113, 2.8502, 8.4868, 84.868],
                [0.3037, 0.3486, 0.5118, 0.5897, 0.6615, 0.8555, 0.9619, 1.0521, 1.2470, 1.3783, 1.6631, 1.9064, 2.0144, 2.1491, 2.5709, 8.1846, 81.846],
                [0.4794, 0.5967, 0.7912, 0.9217, 1.0614, 1.3074, 1.4350, 1.5951, 1.9256, 2.0816, 2.3681, 2.7218, 2.9341, 3.1431, 3.7330, 9.4239, 94.239],

                # Old values
                [2.829, 3.196, 3.394, 3.865, 4.392, 4.648, 5.224, 5.536, 6.182, 7.035, 7.532, 9.030, 10.252, 11.063, 12.809, 12.809],
                [2.622, 2.905, 3.060, 3.454, 3.909, 4.129, 4.624, 4.885, 5.434, 6.174, 6.594, 7.957, 8.970, 9.675, 11.109, 11.109]
            ]
        ],
        "base_powers": [
            1.0674, # Raspberry Pi zero 2W
            3.2058, # Raspberry Pi 5 Model B
            62.7007, # Intel Xeon Silver 4309Y
        ],

    },

    "execution_time_multipliers": [
        # [0.676, 1.376, 0.264, 0.278, 0.746, 0.6677],
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [0.5043, 0.4678, 0.4267, 0.1937, 0.232, 0.363],
        [0.0807, 0.0478, 1.3447, 0.1752, 0.127, 0.305]
    ],

    "compute_resources": {
        "frequencies": [
            # Raspberry Pi zero 2W
            [0.6, 0.7, 0.8, 0.9, 1.0],
            # Raspberry Pi 5 Model B
            [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4],
            # Intel Xeon Silver 4309Y
            [0.8, 0.9, 1.1, 1.2, 1.3, 1.5, 1.6, 1.7, 1.9, 2.0, 2.1, 2.3, 2.4, 2.5, 2.7, 2.8, 28.0]
        ],
        "nodes": [
            # Devices, Edge, Cloud
            100, 20, 1
        ],
        "num_cores": [
            #Cloud
            8,
            #Edge
            4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,

            #Devices
            4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
            4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,

        ]

    }
}

env = {
    "network": {
        "network_links": [
            (1, 0), (2, 0), (3, 0), (4, 0),  # edge to cloud
            (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1),  # devices to edge 1
            (8, 2), (9, 2), (10, 2), (5, 2), (6, 2), (7, 2),  # devices to edge 2
            (11, 3), (12, 3), (13, 3), (14, 3), (15, 3), (16, 3),  # devices to edge 3
            (14, 4), (15, 4), (16, 4), (11, 4), (12, 4), (13, 4),  # devices to edge 4
        ],
        "bandwidth_device_to_edge": 18,
        "power_device_to_edge": 0.7,
        "bandwidth_edge_to_cloud": 100,
        "power_edge_to_cloud": 0.3
    },

    "power": {
        "powers": [
            # # big cores
            # [
            #     [0.265,0.3075,0.4625,0.5475,0.835,1.3625], # MEMORY
            #     [0.1025,0.1475,0.2575,0.3175,0.4875,0.8825],  # BRANCH
            #     [0.1225,0.1725,0.3025,0.3625,0.5575,0.9525],  # FMULT
            #     [0.3075,0.4225,0.76,0.8775,1.4075,2.455],  # SIMD
            #     [0.205,0.285,0.4775,0.585,0.885,1.5225],  # MATMUL
            #     [0.2005,0.267,0.452,0.538,0.8345,1.435]  # DEFAULT
            # ],
            # LITTLE cores
            [
                [0.195, 0.2325, 0.24, 0.2875, 0.3075],  # MEMORY
                [0.0775, 0.1075, 0.1275, 0.195, 0.2275],  # BRANCH
                [0.045, 0.0675, 0.0975, 0.13, 0.1475],  # FMULT
                [0.0775, 0.1225, 0.1475, 0.2325, 0.2675],  # SIMD
                [0.0725, 0.1175, 0.1425, 0.2225, 0.2575],  # MATMUL
                [0.0935, 0.1295, 0.151, 0.2135, 0.2415]  # DEFAULT
            ],
            # A72 cores
            [
                [0.176, 0.233, 0.267, 0.299, 0.332, 0.365, 0.396, 0.436, 0.461, 0.493],
                [0.153, 0.206, 0.232, 0.261, 0.288, 0.318, 0.350, 0.378, 0.410, 0.442],
                [0.215, 0.277, 0.318, 0.357, 0.399, 0.441, 0.484, 0.528, 0.572, 0.616],
                [0.211, 0.270, 0.306, 0.344, 0.383, 0.423, 0.463, 0.503, 0.545, 0.589],
                [0.316, 0.388, 0.441, 0.502, 0.560, 0.618, 0.676, 0.732, 0.794, 0.828],
                [0.214, 0.275, 0.313, 0.352, 0.393, 0.433, 0.474, 0.515, 0.556, 0.594]
            ],
            # Xeon cores
            [
                [2.649, 2.890, 3.019, 3.342, 3.738, 3.953, 4.434, 4.684, 5.186, 5.874, 6.249, 7.534, 8.411, 9.104,
                 10.374],
                [2.497, 2.757, 2.903, 3.281, 3.712, 3.911, 4.353, 4.584, 5.081, 5.763, 6.147, 7.469, 8.399, 9.054,
                 10.356],
                [2.429, 2.669, 2.803, 3.162, 3.577, 3.767, 4.185, 4.398, 4.867, 5.502, 5.878, 7.145, 8.023, 8.634,
                 9.895],
                [2.706, 3.012, 3.183, 3.618, 4.129, 4.365, 4.922, 5.223, 5.854, 6.694, 7.162, 8.609, 9.767, 10.522,
                 12.110],
                [2.829, 3.196, 3.394, 3.865, 4.392, 4.648, 5.224, 5.536, 6.182, 7.035, 7.532, 9.030, 10.252, 11.063,
                 12.809],
                [2.622, 2.905, 3.060, 3.454, 3.909, 4.129, 4.624, 4.885, 5.434, 6.174, 6.594, 7.957, 8.970, 9.675,
                 11.109]
            ]
        ],
        "base_powers": [
            # Values for entire CPUs:
            # 2.98, # A15
            2.58,  # A7
            2.38,  # A72
            8.345731  # Xeon
            # Per-core values
            # 0.645, # A7
            # 0.595, # A72
            # 2.08643275 # Xeon
        ],

    },

    "execution_time_multipliers": [
        # [0.676, 1.376, 0.264, 0.278, 0.746, 0.6677],
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [0.670, 0.643, 0.132, 0.140, 0.232, 0.363],
        [0.158, 0.089, 0.769, 0.383, 0.127, 0.305]
    ],

    "compute_resources": {
        "frequencies": [
            # big
            # [0.6, 0.8, 1.0, 1.2, 1.4],
            # LITTLE
            [0.6, 0.8, 1.0, 1.2, 1.4],
            # A72
            [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
            # Xeon
            [1.2, 1.4, 1.5, 1.7, 1.9, 2.0, 2.2, 2.3, 2.5, 2.7, 2.8, 3.0, 3.2, 3.3, 3.5]
        ],
        "nodes": [
            # Devices, Edge, Cloud
            12, 4, 1
        ],
        "num_cores": [
            #Devices
            4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
            #Edge
            4, 4, 4, 4,
            #Cloud
            4
        ]

    }
}

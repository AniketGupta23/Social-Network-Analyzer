
CREATE DATABASE IF NOT EXISTS social_network_analyzer;

USE social_network_analyzer;


-- Stores information about uploaded datasets
CREATE TABLE IF NOT EXISTS datasets (
    dataset_id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    is_directed BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- Stores nodes belonging to each dataset
CREATE TABLE IF NOT EXISTS nodes (
    node_id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT NOT NULL,
    node_label VARCHAR(255) NOT NULL,

    UNIQUE (dataset_id, node_label),
    UNIQUE (dataset_id, node_id),

    FOREIGN KEY (dataset_id)
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE
);


-- Stores relationships between nodes
CREATE TABLE IF NOT EXISTS edges (
    edge_id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT NOT NULL,
    source_node_id INT NOT NULL,
    target_node_id INT NOT NULL,
    weight DOUBLE NOT NULL DEFAULT 1.0,

    UNIQUE (dataset_id, source_node_id, target_node_id),

    FOREIGN KEY (dataset_id)
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE,

    FOREIGN KEY (dataset_id, source_node_id)
        REFERENCES nodes(dataset_id, node_id),

    FOREIGN KEY (dataset_id, target_node_id)
        REFERENCES nodes(dataset_id, node_id)
);

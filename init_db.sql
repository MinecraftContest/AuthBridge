CREATE TABLE IF NOT EXISTS teams(
    id SERIAL PRIMARY KEY,
    title_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS mc_users(
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) DEFAULT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    team_id INT DEFAULT NULL,
    CONSTRAINT fk_team FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE RESTRICT
);
